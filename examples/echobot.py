"""Minimal/simple single-account echo-bot example."""

import sys

from deltachat2 import Bot, CoreEvent, IOTransport, MsgData, NewMsgEvent, Rpc, events

hooks = events.HookCollection()


@hooks.on(events.RawEvent)
def log_event(bot: Bot, accid: int, event: CoreEvent) -> None:
    """Log all core events for debugging."""
    bot.logger.info(f"[accid={accid}] {event}")


@hooks.on(events.NewMessage)
def echo(bot: Bot, accid: int, event: NewMsgEvent) -> None:
    """Echo back any text message"""
    msg = event.msg
    bot.rpc.send_msg(accid, msg.chat_id, MsgData(text=msg.text))


def main() -> None:
    """Configure (if necessary) and run the bot."""
    with IOTransport() as trans:
        rpc = Rpc(trans)
        bot = Bot(rpc, hooks)

        accounts = rpc.get_all_account_ids()
        accid = accounts[0] if accounts else rpc.add_account()

        print("Running deltachat core", rpc.get_system_info().deltachat_core_version)

        if not rpc.is_configured(accid):
            if len(sys.argv) != 3:
                print("ERROR: Account is not configured so email and password must be provided")
                return
            params = {"addr": sys.argv[1], "password": sys.argv[2]}
            rpc.add_or_update_transport(accid, params)

        bot.run_forever()


if __name__ == "__main__":
    main()
