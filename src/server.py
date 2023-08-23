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
from schemas import Message

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
    total = 347

    while True:
        for i in range(total):
            await websocket.send_json(
                {
                    "msgType": "SMSMailingStatus",
                    "SMSMailings": [
                        {
                            "timestamp": 1123131392.734,
                            "SMSText": "Сегодня гроза! Будьте осторожны!",
                            "mailingId": "1",
                            "totalSMSAmount": total,
                            "deliveredSMSAmount": i,
                            "failedSMSAmount": 5,
                        },
                        {
                            "timestamp": 1323141112.924422,
                            "SMSText": "Новогодняя акция!!! Приходи в магазин и получи скидку!!!",
                            "mailingId": "new-year",
                            "totalSMSAmount": 3993,
                            "deliveredSMSAmount": 801,
                            "failedSMSAmount": 0,
                        },
                    ],
                }
            )
            await trio.sleep(0.3)
        await trio.sleep(3)


@app.before_serving
async def create_db_pool():
    # app.db_pool = await ...
    app.redis = aioredis.from_url("redis://localhost", decode_responses=True)
    app.db = Database(app.redis)


# @app.before_serving
# async def use_g():
#     g.something.do_something()


# @app.while_serving
# async def lifespan():
#     ...  # startup
#     yield
#     ...  # shutdown


# @app.route("/")
# async def index():
#     app.db_pool.execute(...)
#     # g.something is not available here


@app.after_serving
async def create_db_pool():
    # await app.db_pool.close()
    await app.redis.close()


# app.run()


async def run_server():
    async with trio_asyncio.open_loop() as loop:
        config = HyperConfig()
        config.bind = [f"127.0.0.1:5000"]
        config.use_reloader = True

        # здесь живёт остальной код инициализации
        # ...
        await serve(app, config)


trio.run(run_server)
