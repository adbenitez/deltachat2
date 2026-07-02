"""Simple single-profile echo-bot example."""

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
