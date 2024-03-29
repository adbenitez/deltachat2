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
pip install deltachat2[full]
```

## Usage

Example echo-bot written with deltachat2:

```python
from deltachat2 import events, run_bot_cli

hooks = events.HookCollection()

@hooks.on(events.RawEvent)
def log_event(bot, accid, event):
    bot.logger.info(event)

@hooks.on(events.NewMessage)
def echo(bot, accid, event):
    msg = event.msg
    bot.rpc.misc_send_text_message(accid, msg.chat_id, msg.text)

if __name__ == "__main__":
    run_bot_cli(hooks)
```

Save the above code in a `echobot.py` file and run it with Python:

```
python echobot.py --email bot@example.com --password MyPassword
```

Then write to the bot address using your Delta Chat client to test it is working.

## Developing bots faster ⚡

If what you want is to develop bots, you probably should use this library together with
[deltabot-cli-py](https://github.com/deltachat-bot/deltabot-cli-py/), it takes away the
repetitive process of creating the bot CLI and let you focus on writing your message
processing logic.
