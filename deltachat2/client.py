"""Event loop implementations offering high level event handling/hooking."""

import logging
from typing import Callable, Dict, Iterable, Optional, Set, Tuple, Type, Union

from .events import EventFilter, HookCallback, RawEvent
from .rpc import Rpc
from .types import CoreEvent, Event


class Client:
    """Delta Chat client that listen to raw core events for multiple account."""

    def __init__(
        self,
        rpc: Rpc,
        hooks: Optional[Iterable[Tuple[HookCallback, Union[type, EventFilter]]]] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.rpc = rpc
        self.logger = logger or logging
        self._hooks: Dict[type, Set[Tuple[HookCallback, EventFilter]]] = {}
        self.add_hooks(hooks or [])

    def add_hooks(self, hooks: Iterable[Tuple[HookCallback, Union[type, EventFilter]]]) -> None:
        """Register event hooks callbacks."""
        for hook, event in hooks:
            self.add_hook(hook, event)

    def add_hook(self, hook: HookCallback, event: Union[type, EventFilter] = RawEvent) -> None:
        """Register hook for the given event filter."""
        event2 = event() if isinstance(event, type) else event
        self._hooks.setdefault(type(event2), set()).add((hook, event2))

    def remove_hook(self, hook: HookCallback, event: Union[type, EventFilter]) -> None:
        """Unregister hook from the given event filter."""
        event2 = event() if isinstance(event, type) else event
        self._hooks.get(type(event2), set()).remove((hook, event2))

    def configure(self, account_id: int, email: str, password: str, **kwargs) -> None:
        """Configure the account with the given account ID."""
        self.rpc.set_config(account_id, "addr", email)
        self.rpc.set_config(account_id, "mail_pw", password)
        if kwargs:
            self.rpc.batch_set_config(account_id, kwargs)
        self.rpc.configure(account_id)

    def run_forever(self, account_id: int = 0) -> None:
        """Process events forever.

        if account_id != 0, only the account with the given ID will be started.
        """
        self.run_until(lambda _: False, account_id)

    def run_until(self, func: Callable[[Event], bool], account_id: int = 0) -> Event:
        """Process events until the given callable evaluates to True.

        The callable will receive the Event object representing the last processed event.
        The event is returned when the callable evaluates to True.
        """
        self.logger.debug("Listening to incoming events...")
        if account_id:
            if self.rpc.is_configured(account_id):
                self.rpc.start_io(account_id)
        else:
            self.rpc.start_io_for_all_accounts()

        while True:
            raw_event = self.rpc.get_next_event()
            event = Event(raw_event.context_id, CoreEvent(raw_event.event))
            self._on_event(event, RawEvent)
            if func(event):
                return event

    def _on_event(self, event: Event, filter_type: Type[EventFilter]) -> None:
        for hook, evfilter in self._hooks.get(filter_type, []):
            if evfilter.filter(event.event):
                try:
                    hook(self, event.account_id, event.event)
                except Exception as ex:
                    self.logger.exception(ex)
