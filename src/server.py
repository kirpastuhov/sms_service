import json

import trio
from quart import render_template, websocket
from quart_trio import QuartTrio

app = QuartTrio(__name__)


@app.route("/")
async def hello():
    return await render_template("index.html")


@app.websocket("/ws")
async def ws():
    while True:
        await websocket.send(json.dumps({"id": 456}))
        await trio.sleep(3)


app.run()
