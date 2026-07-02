# Delta Chat client library for Python

[![Latest Release](https://img.shields.io/pypi/v/deltachat2.svg)](https://pypi.org/project/deltachat2)
[![CI](https://github.com/adbenitez/deltachat2/actions/workflows/python-ci.yml/badge.svg)](https://github.com/adbenitez/deltachat2/actions/workflows/python-ci.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Client library for Delta Chat core JSON-RPC interface

## Install

```sh
pip install deltachat2
```

To use this library, you need to have `deltachat-rpc-server` program installed,
you can install it together with this library with:

```sh
pip install 'deltachat2[full]'
```

## Usage

Example echo-bot written with deltachat2:

```python
from deltachat2 import (
    Bot,
    EventType,
    IOTransport,
    MessageData,
    NewMsgEvent,
    Rpc,
    events,
)

hooks = events.HookCollection()


@hooks.on(events.RawEvent)
def log_event(_bot: Bot, _accid: int, event: EventType) -> None:
    """Log all core events for debugging."""
    print(event)


@hooks.on(events.NewMessage)
def echo(bot: Bot, accid: int, event: NewMsgEvent) -> None:
    """Echo back any text message"""
    msg = event.msg
    bot.rpc.send_msg(accid, msg.chat_id, MessageData(text=msg.text))


if __name__ == "__main__":
    with IOTransport() as trans:
        rpc = Rpc(trans)
        bot = Bot(rpc, hooks)

        accounts = rpc.get_all_account_ids()
        accid = accounts[0] if accounts else rpc.add_account()

        if not rpc.is_configured(accid):
            rpc.set_config(accid, "bot", "1")
            rpc.add_transport_from_qr(accid, "dcaccount:nine.testrun.org")

        link = rpc.get_chat_securejoin_qr_code(accid, None)
        print(f"Listening at: {link}")
        bot.run_forever()
```

Save the above code in a `echobot.py` file and run it with Python:

```
python echobot.py
```

Then write to the bot using the invite link that will be printed in the screen.

## Developing bots faster ⚡

If you want to develop bots, you probably should use this library together with
[deltabot-cli-py](https://github.com/deltachat-bot/deltabot-cli-py/), it takes away
the repetitive process of creating the bot CLI and let you focus on writing your
message processing logic.
