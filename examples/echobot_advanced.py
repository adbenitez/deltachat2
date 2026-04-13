"""Advanced single-account echo-bot example."""

from threading import Thread

from deltachat2 import (
    Bot,
    CoreEvent,
    EventType,
    IOTransport,
    MsgData,
    NewMsgEvent,
    Rpc,
    events,
)

hooks = events.HookCollection()


@hooks.on(events.RawEvent)
def log_event(bot: Bot, accid: int, event: CoreEvent) -> None:
    """Log all core events for debugging."""
    if event.kind == EventType.INFO:
        print("DEBUG", event.msg)
    elif event.kind == EventType.WARNING:
        print("WARNING", event.msg)
    elif event.kind == EventType.ERROR:
        print("ERROR", event.msg)
    elif event.kind == EventType.MSG_DELIVERED:
        bot.rpc.delete_messages(accid, [event.msg_id])


@hooks.on(events.NewMessage)
def echo(bot: Bot, accid: int, event: NewMsgEvent) -> None:
    """Echo back any text message"""
    msg = event.msg
    bot.rpc.markseen_msgs(accid, [msg.id])
    bot.rpc.send_msg(accid, msg.chat_id, MsgData(text=msg.text))


@hooks.after(events.NewMessage)
def delete_msgs(bot: Bot, accid: int, event: NewMsgEvent) -> None:
    """Delete already processed messages."""
    bot.rpc.delete_messages(accid, [event.msg.id])


def main() -> None:
    """Configure (if necessary) and run the bot."""
    with IOTransport() as trans:
        rpc = Rpc(trans)
        bot = Bot(rpc, hooks)

        accounts = rpc.get_all_account_ids()
        accid = accounts[0] if accounts else rpc.add_account()

        if not rpc.is_configured(accid):

            def configure():
                rpc.set_config(accid, "bot", "1")
                rpc.add_transport_from_qr(accid, "dcaccount:nine.testrun.org")
                link = rpc.get_chat_securejoin_qr_code(accid, None)
                print(f"Listening at: {link}")

            Thread(target=configure).start()
        else:
            link = rpc.get_chat_securejoin_qr_code(accid, None)
            print(f"Listening at: {link}")

        bot.run_forever()


if __name__ == "__main__":
    main()
