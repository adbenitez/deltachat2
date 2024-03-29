"""JSON-RPC API definition."""

from .transport import RpcTransport
from .types import MsgData


class Rpc:
    """Access to the Delta Chat JSON-RPC API."""

    def __init__(self, transport: RpcTransport) -> None:
        self.transport = transport

    def __getattr__(self, attr: str):
        return lambda *args: self.transport.call(attr, *args)

    def send_msg(self, accid: int, chatid: int, data: MsgData) -> int:
        """Send a message and return the message ID of the sent message."""
        return self.transport.call("send_msg", accid, chatid, data)
