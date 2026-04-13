"""Event loop implementations offering high level event handling/hooking."""

import logging
from typing import Callable, Optional, TypeVar, Union

from .events import EventFilter, HookCallback, HookCollection, HooksIterable, RawEvent
from .rpc import Rpc
from .types import CoreEvent, Event

T = TypeVar("T", bound=EventFilter)
_HooksIndex = dict[type[T], set[tuple[HookCallback, T]]]


class Client:
    """Delta Chat client that listen to raw core events for multiple account."""

    def __init__(
        self,
        rpc: Rpc,
        hooks: Optional[HooksIterable] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        """If hooks is an instance of HookCollection, also its post-hooks will be registered."""
        self.rpc = rpc
        self.logger = logger or logging.getLogger("deltachat2.Client")
        self._hooks: _HooksIndex = {}
        self._post_hooks: _HooksIndex = {}
        self.add_hooks(hooks or [])
        if isinstance(hooks, HookCollection):
            self.add_post_hooks(hooks.post_hooks_iter())

    def add_hooks(self, hooks: HooksIterable) -> None:
        """Register event hooks callbacks."""
        for hook, event in hooks:
            self.add_hook(hook, event)

    def add_post_hooks(self, hooks: HooksIterable) -> None:
        """Register event post-hooks callbacks."""
        for hook, event in hooks:
            self.add_post_hook(hook, event)

    def add_hook(
        self, hook: HookCallback, event: Union[type[EventFilter], EventFilter] = RawEvent
    ) -> None:
        """Register hook to be called when an event that matches the given filter is received."""
        event2 = event() if isinstance(event, type) else event
        self._hooks.setdefault(type(event2), set()).add((hook, event2))

    def remove_hook(self, hook: HookCallback, event: Union[type[EventFilter], EventFilter]) -> None:
        """Unregister hook from the given event filter."""
        event2 = event() if isinstance(event, type) else event
        self._hooks.get(type(event2), set()).remove((hook, event2))

    def add_post_hook(
        self, hook: HookCallback, event: Union[type[EventFilter], EventFilter] = RawEvent
    ) -> None:
        """Register hook to be called after an event that matches the given filter is processed."""
        event2 = event() if isinstance(event, type) else event
        self._post_hooks.setdefault(type(event2), set()).add((hook, event2))

    def remove_post_hook(
        self, hook: HookCallback, event: Union[type[EventFilter], EventFilter]
    ) -> None:
        """Unregister post-hook from the given event filter."""
        event2 = event() if isinstance(event, type) else event
        self._post_hooks.get(type(event2), set()).remove((hook, event2))

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

    def _on_event(self, event: Event, filter_type: type[EventFilter]) -> None:
        self._notify(self._hooks, event, filter_type)
        self._notify(self._post_hooks, event, filter_type)

    def _notify(self, hooks: _HooksIndex, event: Event, filter_type: type[EventFilter]) -> None:
        for hook, evfilter in hooks.get(filter_type, []):
            if evfilter.filter(event.event):
                try:
                    hook(self, event.account_id, event.event)  # noqa
                except Exception as ex:
                    self.logger.exception(ex)
