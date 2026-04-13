"""Event loop implementations offering high level event handling/hooking for bots."""

import logging
from typing import Callable, Iterable, Optional, Tuple, Union

from .client import Client
from .events import EventFilter, HookCallback, NewMessage
from .rpc import Rpc
from .transport import JsonRpcError
from .types import Event, EventType, Message, NewMsgEvent, SpecialContactId


class Bot(Client):
    """A Delta Chat client for bots.

    This bot client triggers "NewMessage" highlevel events in addition to raw core events.
    """

    def __init__(
        self,
        rpc: Rpc,
        hooks: Optional[Iterable[Tuple[HookCallback, Union[type, EventFilter]]]] = None,
        logger: Optional[logging.Logger] = None,
        command_prefix: str = "/",
    ) -> None:
        """If hooks is an instance of HookCollection, also its post-hooks will be registered."""
        self.command_prefix = command_prefix
        logger = logger or logging.getLogger("deltachat2.Bot")
        super().__init__(rpc, hooks, logger)

    def has_command(self, command: str) -> bool:
        """Return True if the bot has a hook/callback registered for the given command,
        False otherwise."""
        if not command or not command.startswith(self.command_prefix):
            return False
        for hook in self._hooks.get(NewMessage, []):
            if command == hook[1].command:
                return True
        return False

    def run_until(self, func: Callable[[Event], bool], account_id: int = 0) -> Event:
        """Process events until the given callable evaluates to True.

        The callable will receive the Event object representing the last processed event.
        The event is returned when the callable evaluates to True.
        """
        if account_id:
            if self.rpc.is_configured(account_id):
                self.rpc.start_io(account_id)
        else:
            self.rpc.start_io_for_all_accounts()

        def _wrapper(event: Event) -> bool:
            if event.event.kind == EventType.INCOMING_MSG:
                self._process_message(event.account_id, event.event.msg_id)
            return func(event)

        return super().run_until(_wrapper, account_id)

    def _parse_command(self, accid: int, event: NewMsgEvent) -> None:
        cmds = [hook[1].command for hook in self._hooks.get(NewMessage, []) if hook[1].command]
        parts = event.msg.text.split(maxsplit=1)
        payload = parts[1] if len(parts) > 1 else ""
        cmd = parts.pop(0)

        if "@" in cmd:
            suffix = "@" + self.rpc.get_contact(accid, SpecialContactId.SELF).address
            if cmd.endswith(suffix):
                cmd = cmd[: -len(suffix)]
            else:
                return

        parts = cmd.split("_")
        _payload = payload
        while parts:
            _cmd = "_".join(parts)
            if _cmd in cmds:
                break
            _payload = (parts.pop() + " " + _payload).rstrip()

        if parts:
            cmd = _cmd
            payload = _payload

        event.command = cmd
        event.payload = payload

    def _process_message(self, accid: int, msgid: int) -> None:
        try:
            msg = self.rpc.get_message(accid, msgid)
            if msg.from_id > SpecialContactId.LAST_SPECIAL:
                event = NewMsgEvent(command="", payload="", msg=msg)
                if not msg.is_info and msg.text.startswith(self.command_prefix):
                    self._parse_command(accid, event)
                self._on_event(Event(accid, event), NewMessage)  # noqa
        except JsonRpcError as err:
            self.logger.exception(err)
