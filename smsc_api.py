import asks
import asyncclick as click
import trio
from dotenv import load_dotenv
from loguru import logger

asks.init(trio)

load_dotenv()  # take environment variables from .env.


@click.command()
@click.option("--login", show_default=True, type=str, help="Server address", envvar="LOGIN")
@click.option("--password", envvar="PASSWORD")
@click.option("--phones_list", envvar="PHONES_LIST")
@click.option("--message", envvar="MESSAGE")
@click.option("--valid_for", envvar="VALID_FOR")
async def main(login: str, password: str, phones_list: list[str], message: str, valid_for: int):
    logger.debug(f"Sending {message} to {phones_list}")
    await asks.post(f"https://smsc.ru/sys/send.php?login={login}&psw={password}&phones={phones_list}&mes={message}&valid={valid_for}")


if __name__ == "__main__":
    main(_anyio_backend="trio")
