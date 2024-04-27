"""High-level classes for event processing and filtering."""

import re
from abc import ABC, abstractmethod
from typing import (
    TYPE_CHECKING,
    Callable,
    Iterable,
    Iterator,
    Optional,
    Set,
    Tuple,
    Union,
)

from .types import CoreEvent, EventType, NewMsgEvent

if TYPE_CHECKING:
    from .bot import Bot
    from .client import Client
ClientHookCallback = Callable[["Client", int, CoreEvent], None]
BotHookCallback = Union[
    Callable[["Bot", int, CoreEvent], None], Callable[["Bot", int, NewMsgEvent], None]
]
HookCallback = Union[ClientHookCallback, BotHookCallback]
HookDecorator = Callable[[HookCallback], HookCallback]


def _tuple_of(obj, type_: type) -> tuple:
    if not obj:
        return ()
    if isinstance(obj, type_):
        obj = (obj,)

    if not all(isinstance(elem, type_) for elem in obj):
        raise TypeError()
    return tuple(obj)


class EventFilter(ABC):
    """The base event filter."""

    def __init__(self, func: Optional[Callable] = None):
        self.func = func

    @abstractmethod
    def __hash__(self) -> int:
        """Object's unique hash"""

    @abstractmethod
    def __eq__(self, other) -> bool:
        """Return True if two event filters are equal."""

    def __ne__(self, other):
        return not self == other

    def _call_func(self, event: Union[CoreEvent, NewMsgEvent]) -> bool:
        if not self.func:
            return True
        return bool(self.func(event))

    @abstractmethod
    def filter(self, event: Union[CoreEvent, NewMsgEvent]):
        """Return True if the event matched the filter and should be used, or False otherwise."""


class RawEvent(EventFilter):
    """Matches raw core events.

    :param types: The types of event to match.
    :param func: A Callable that should accept the CoreEvent as parameter, and return
                 a boolean value indicating whether the event should be dispatched or not.
    """

    def __init__(
        self,
        types: Union[None, EventType, Iterable[EventType]] = None,
        func: Optional[Callable[[CoreEvent], bool]] = None,
    ):
        super().__init__(func=func)
        try:
            self.types = _tuple_of(types, EventType)
        except TypeError as err:
            raise TypeError(f"Invalid event type given: {types}") from err

    def __hash__(self) -> int:
        return hash((self.types, self.func))

    def __eq__(self, other) -> bool:
        if isinstance(other, RawEvent):
            return (self.types, self.func) == (other.types, other.func)
        return False

    def filter(self, event: Union[CoreEvent, NewMsgEvent]) -> bool:
        """Return True if the event matched the filter and should be used, or False otherwise."""
        assert isinstance(event, CoreEvent), "event must be an instance of CoreEvent"
        if self.types and event.kind not in self.types:
            return False
        return self._call_func(event)


class NewMessage(EventFilter):
    """Matches whenever a new message arrives. This event is only triggered by Bot clients.

    :param pattern: if set, this Pattern will be used to filter the message by its text
                    content.
    :param command: If set, only match messages with the given command (ex. /help).
                    Setting this property implies `is_info==False`.
    :param is_bot: If set to True only match messages sent by bots, if set to None
                   match messages from bots and users. If omitted or set to False
                   only messages from users will be matched.
    :param is_info: If set to True only match info/system messages, if set to False
                    only match messages that are not info/system messages. If omitted
                    info/system messages as well as normal messages will be matched.
    :param func: A Callable that should accept the NewMsgEvent event as parameter,
                 and return a boolean indicating whether the event should be dispatched or not.
    """

    def __init__(
        self,
        pattern: Union[
            None,
            str,
            Callable[[str], bool],
            re.Pattern,
        ] = None,
        command: Optional[str] = None,
        is_bot: Optional[bool] = False,
        is_info: Optional[bool] = None,
        func: Optional[Callable[[NewMsgEvent], bool]] = None,
    ) -> None:
        super().__init__(func=func)
        self.is_bot = is_bot
        self.is_info = is_info
        if command is not None and not isinstance(command, str):
            raise TypeError("Invalid command")
        self.command = command
        if self.is_info and self.command:
            raise AttributeError("Can not use command and is_info at the same time.")
        if isinstance(pattern, str):
            pattern = re.compile(pattern)
        if isinstance(pattern, re.Pattern):
            self.pattern: Optional[Callable] = pattern.match
        elif not pattern or callable(pattern):
            self.pattern = pattern
        else:
            raise TypeError("Invalid pattern type")

    def __hash__(self) -> int:
        return hash((self.pattern, self.command, self.is_bot, self.is_info, self.func))

    def __eq__(self, other) -> bool:
        if isinstance(other, NewMessage):
            return (
                self.pattern,
                self.command,
                self.is_bot,
                self.is_info,
                self.func,
            ) == (
                other.pattern,
                other.command,
                other.is_bot,
                other.is_info,
                other.func,
            )
        return False

    def filter(self, event: Union[CoreEvent, NewMsgEvent]) -> bool:
        """Return True if the event matched the filter and should be used, or False otherwise."""
        assert isinstance(event, NewMsgEvent), "event must be an instance of NewMsgEvent"
        if self.is_bot is not None and self.is_bot != event.msg.is_bot:
            return False
        if self.is_info is not None and self.is_info != event.msg.is_info:
            return False
        if self.command and self.command != event.command:
            return False
        if self.pattern:
            match = self.pattern(event.msg.text)
            if not match:
                return False
        return super()._call_func(event)


_HookSet = Set[Tuple[HookCallback, Union[type, EventFilter]]]


class HookCollection:
    """
    Helper class to collect event hooks and post-hooks
    that can be later added to a Delta Chat client.
    """

    def __init__(self) -> None:
        self._hooks: _HookSet = set()
        self._post_hooks: _HookSet = set()

    def __iter__(self) -> Iterator[Tuple[HookCallback, Union[type, EventFilter]]]:
        return iter(self._hooks)

    def post_hooks_iter(self) -> Iterator[Tuple[HookCallback, Union[type, EventFilter]]]:
        """Iterator over the registered post-hooks"""
        return iter(self._post_hooks)

    def on(self, event: Union[type, EventFilter]) -> HookDecorator:
        """Register decorated function to be called for events that match the given filter."""
        return self._on(self._hooks, event)

    def after(self, event: Union[type, EventFilter]) -> HookDecorator:
        """Register decorated function to be called after an event that matches
        the given filter is processed.
        """
        return self._on(self._post_hooks, event)

    def _on(self, hooks: _HookSet, event: Union[type, EventFilter]) -> HookDecorator:
        if isinstance(event, type):
            event = event()
        assert isinstance(event, EventFilter), "Invalid event filter"

        def _decorator(func: HookCallback) -> HookCallback:
            hooks.add((func, event))
            return func

        return _decorator
