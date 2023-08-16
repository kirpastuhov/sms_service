from contextvars import ContextVar

import asks
import asyncclick as click
import trio
from dotenv import load_dotenv
from loguru import logger

from src.exceptions import SmscApiError


@click.command()
@click.option(
    "--login", show_default=True, type=str, help="Server address", envvar="LOGIN"
)
@click.option(
    "--password",
    envvar="PASSWORD",
)
@click.option(
    "--phones_list",
    envvar="PHONES_LIST",
)
@click.option(
    "--message",
    envvar="MESSAGE",
)
@click.option(
    "--valid_for",
    envvar="VALID_FOR",
)
async def main(
    login: str, password: str, phones_list: list[str], message: str, valid_for: int
):
    smsc_login.set(login)
    smsc_password.set(password)

    await request_smsc(
        "POST",
        "send",
        login="",
        password="",
        payload={"phones": phones_list, "message": message, "valid_for": valid_for},
    )

    # sms_id = response.json().get("id", 0)


async def request_smsc(
    http_method: str,
    api_method: str,
    login: str | None,
    password: str | None,
    payload: dict = {},
) -> dict:
    """Send request to SMSC.ru service.

    Args:
        http_method (str): E.g. 'GET' or 'POST'.
        api_method (str): E.g. 'send' or 'status'.
        login (str): Login for account on smsc.ru.
        password (str): Password for account on smsc.ru.
        payload (dict): Additional request params, override default ones.
    Returns:
        dict: Response from smsc.ru API.
    Raises:
        SmscApiError: If smsc.ru API response status is not 200 or JSON response
        has "error_code" inside.

    Examples:
        >>> await request_smsc(
        ...   'POST',
        ...   'send',
        ...   login='smsc_login',
        ...   password='smsc_password',
        ...   payload={'phones': '+79123456789'}
        ... )
        {'cnt': 1, 'id': 24}
        >>> await request_smsc(
        ...   'GET',
        ...   'status',
        ...   login='smsc_login',
        ...   password='smsc_password',
        ...   payload={
        ...     'phone': '+79123456789',
        ...     'id': '24',
        ...   }
        ... )
        {'status': 1, 'last_date': '28.12.2019 19:20:22', 'last_timestamp': 1577550022}
    """
    login = login or smsc_login.get()
    password = password or smsc_password.get()

    match http_method:
        case "POST":
            if api_method != "send":
                raise SmscApiError("Invalid HTTP method")
            logger.debug(
                f"Sending {payload.get('message', '')} to {payload.get('phones', '')}"
            )
            response = await asks.post(
                f"https://smsc.ru/sys/send.php?login={login}&psw={password}&phones={payload.get('phones', '')}&mes={payload.get('message', '')}&valid={payload.get('valid_for', '')}&fmt=3"
            )
            print(response.json())
            return "Bad request"
        case "GET":
            if api_method != "status":
                raise SmscApiError("Invalid API method")
            response = await asks.post(
                f"https://smsc.ru/sys/status.php?login={login}&psw={password}&phone={payload.get('phone','')}&id={payload.get('id', '')}&fmt=3"
            )
            print(response.json())
        case _:
            return "Something's wrong with the internet"


if __name__ == "__main__":
    asks.init(trio)

    load_dotenv()

    smsc_login: ContextVar[str] = ContextVar("smsc_login")
    smsc_password: ContextVar[str] = ContextVar("smsc_password")

    main(_anyio_backend="trio")
