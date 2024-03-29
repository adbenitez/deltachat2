"""Utilities"""

import argparse
import sys
from threading import Thread
from typing import Callable, Iterable, Optional, Tuple, Type, Union

from .bot import Bot
from .client import Client
from .events import EventFilter
from .rpc import Rpc
from .transport import IOTransport


def run_client_cli(
    hooks: Optional[Iterable[Tuple[Callable, Union[type, EventFilter]]]] = None,
    argv: Optional[list] = None,
    **kwargs,
) -> None:
    """Run a simple command line app, using the given hooks.

    Extra keyword arguments are passed to the internal Rpc object.
    """
    _run_cli(Client, hooks, argv, **kwargs)


def run_bot_cli(
    hooks: Optional[Iterable[Tuple[Callable, Union[type, EventFilter]]]] = None,
    argv: Optional[list] = None,
    **kwargs,
) -> None:
    """Run a simple bot command line using the given hooks.

    Extra keyword arguments are passed to the internal Rpc object.
    """
    _run_cli(Bot, hooks, argv, **kwargs)


def _run_cli(
    client_type: Type["Client"],
    hooks: Optional[Iterable[Tuple[Callable, Union[type, EventFilter]]]] = None,
    argv: Optional[list] = None,
    **kwargs,
) -> None:
    if argv is None:
        argv = sys.argv

    parser = argparse.ArgumentParser(prog=argv[0] if argv else None)
    parser.add_argument(
        "accounts_dir",
        help="accounts folder (default: current working directory)",
        nargs="?",
    )
    parser.add_argument("--email", action="store", help="email address")
    parser.add_argument("--password", action="store", help="password")
    args = parser.parse_args(argv[1:])

    with IOTransport(accounts_dir=args.accounts_dir, **kwargs) as trans:
        rpc = Rpc(trans)
        client = client_type(rpc, hooks)

        accounts = rpc.get_all_account_ids()
        accid = accounts[0] if accounts else rpc.add_account()

        core_version = rpc.get_system_info().deltachat_core_version
        client.logger.debug("Running deltachat core %s", core_version)

        if not rpc.is_configured(accid):
            assert args.email, "Account is not configured and email must be provided"
            assert args.password, "Account is not configured and password must be provided"
            configure_thread = Thread(
                target=client.configure, args=(accid, args.email, args.password)
            )
            configure_thread.start()

        client.run_forever()
