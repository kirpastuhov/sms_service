import json
from unittest.mock import patch

import pydantic
import trio
from quart import redirect, render_template, request, url_for, websocket
from quart_trio import QuartTrio

from schemas import Message

app = QuartTrio(__name__)


@app.route("/")
async def hello():
    return await render_template("index.html")


@app.route("/send/", methods=["POST"])
async def send():
    if request.method != "POST":
        return json.dumps({"errorMessage": "Потеряно соединение с SMSC.ru"})

    try:
        msg = Message(text=await request.get_data(as_text=True))
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
            return json.dumps({})
    except pydantic.ValidationError:
        return json.dumps({"errorMessage": "Invalid Message."})


@app.websocket("/ws")
async def ws():
    while True:
        await websocket.send(json.dumps({"id": 456}))
        await trio.sleep(3)


app.run()
