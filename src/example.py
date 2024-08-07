import argparse
import asyncio

import trio
import trio_asyncio
from redis import asyncio as aioredis

from db import Database


def create_argparser():
    parser = argparse.ArgumentParser(description="Redis database usage example")
    parser.add_argument(
        "--address",
        action="store",
        dest="redis_uri",
        help="Redis URL. See examples at https://aioredis.readthedocs.io/en/latest/api/high-level/#aioredis.client.Redis.from_url",
        default="redis://localhost",
    )
    return parser


async def main():
    parser = create_argparser()
    args = parser.parse_args()

    redis = aioredis.from_url(args.redis_uri, decode_responses=True)

    try:
        db = Database(redis)

        sms_id = "1"

        phones = [
            "+7 999 519 05 57",
            "911",
            "112",
        ]
        text = "Вечером будет шторм!"

        await db.add_sms_mailing(sms_id, phones, text)

        sms_ids = await db.list_sms_mailings()
        print("Registered mailings ids", sms_ids)

        pending_sms_list = await db.get_pending_sms_list()
        print("pending:")
        print(pending_sms_list)

        await db.update_sms_status_in_bulk(
            [
                # [sms_id, phone_number, status]
                [sms_id, "112", "failed"],
                [sms_id, "911", "pending"],
                [sms_id, "+7 999 519 05 57", "delivered"],
                # following statuses are available: failed, pending, delivered
            ]
        )

        pending_sms_list = await db.get_pending_sms_list()
        print("pending:")
        print(pending_sms_list)

        sms_mailings = await db.get_sms_mailings("1")
        print("sms_mailings")
        print(sms_mailings)

        async def send():
            while True:
                await asyncio.sleep(1)
                await redis.publish("updates", sms_id)

        async def listen():
            channel = redis.pubsub()
            await channel.subscribe("updates")

            while True:
                message = await channel.get_message(
                    ignore_subscribe_messages=True, timeout=1.0
                )

                if not message:
                    continue

                print("Got message:", repr(message["data"]))

        await asyncio.gather(send(), listen())

    finally:
        await redis.close()


if __name__ == "__main__":
    # asyncio.run(main())
    trio_asyncio.run(trio_asyncio.aio_as_trio(main))

    # async def async_main_wrapper(*args):
    #     async with trio_asyncio.open_loop() as loop:
    #         assert loop == asyncio.get_event_loop()
    #         await main(*args)

    # trio.run(async_main_wrapper)
