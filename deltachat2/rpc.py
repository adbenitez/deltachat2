"""JSON-RPC API definition."""

from .transport import RpcTransport


class Rpc:
    """Access to the Delta Chat JSON-RPC API."""

    def __init__(self, transport: RpcTransport) -> None:
        self.transport = transport

    def __getattr__(self, attr: str):
        return lambda *args: self.transport.call(attr, *args)
