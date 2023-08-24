import json
import warnings
from unittest.mock import patch

import pydantic
import trio
import trio_asyncio
from hypercorn.config import Config as HyperConfig
from hypercorn.trio import serve
from quart import render_template, request, websocket
from quart_trio import QuartTrio
from redis import asyncio as aioredis
from trio_asyncio import aio_as_trio

from db import Database
from schemas import Mailing, Message

app = QuartTrio(__name__)

warnings.filterwarnings("ignore")


@app.route("/")
async def hello():
    return await render_template("index.html")


@app.route("/send/", methods=["POST"])
async def send():
    if request.method != "POST":
        return json.dumps({"errorMessage": "Потеряно соединение с SMSC.ru"})

    try:
        msg = Message(text=await request.get_data(as_text=True))

        phones = [
            "+7 999 519 05 57",
            "911",
            "112",
        ]

        with patch("smsc_api.request_smsc") as mocked_request:
            mocked_request.return_value = {"id": 457, "cnt": 1}
            mocked_resp = await mocked_request(
                "POST",
                "send",
                login="",
                password="",
                payload={"phones": [], "message": msg.text, "valid_for": ""},
            )
            print(mocked_resp)

            await aio_as_trio(
                app.db.add_sms_mailing(mocked_resp["id"], phones, msg.text)
            )

            sms_mailings = await aio_as_trio(app.db.get_sms_mailings(mocked_resp["id"]))
            print("sms_mailings")
            print(sms_mailings)
            return json.dumps({})
    except pydantic.ValidationError:
        return json.dumps({"errorMessage": "Invalid Message."})


@app.websocket("/ws")
async def ws():
    while True:
        await trio.sleep(0.5)
        sms_ids = await aio_as_trio(app.db.list_sms_mailings())
        mailings = await aio_as_trio(app.db.get_sms_mailings(*sms_ids))
        mailings = [
            Mailing(
                timestamp=sms["created_at"],
                SMSText=sms["text"],
                mailingId=sms["sms_id"],
                totalSMSAmount=sms["phones_count"],
                deliveredSMSAmount=2,
                failedSMSAmount=1,
            ).model_dump()
            for sms in mailings
        ]

        await websocket.send_json(
            {"msgType": "SMSMailingStatus", "SMSMailings": mailings}
        )


@app.before_serving
async def create_db_pool():
    app.redis = aioredis.from_url("redis://localhost", decode_responses=True)
    app.db = Database(app.redis)


@app.after_serving
async def create_db_pool():
    await app.redis.close()


async def run_server():
    async with trio_asyncio.open_loop() as loop:
        config = HyperConfig()
        config.bind = [f"127.0.0.1:5000"]
        config.use_reloader = True

        await serve(app, config)


trio.run(run_server)
