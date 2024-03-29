"""Minimal/simple single-account client example boilerplate."""

import subprocess
import sys

from deltachat2 import Client, CoreEvent, IOTransport, Rpc, events

hooks = events.HookCollection()


@hooks.on(events.RawEvent)
def log_event(_client: Client, accid: int, event: CoreEvent) -> None:
    """here you should process events and update UI."""
    print(f"[accid={accid}] {event}")


def main() -> None:
    """Configure (if necessary) and run the client."""
    # in a TUI app you don't want the deltachat-rpc-server printing to stderr
    with IOTransport(stderr=subprocess.DEVNULL) as trans:
        rpc = Rpc(trans)
        client = Client(rpc, hooks)

        accounts = rpc.get_all_account_ids()
        accid = accounts[0] if accounts else rpc.add_account()

        if not rpc.is_configured(accid):
            if len(sys.argv) != 3:
                print("ERROR: Account is not configured so email and password must be provided")
                return
            client.configure(accid, sys.argv[1], sys.argv[2])

        client.run_forever()


if __name__ == "__main__":
    main()
