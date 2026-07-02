"""JSON-RPC transports to communicate with chatmail core."""

import itertools
import json
import logging
import os
import subprocess
import sys
from abc import ABC, abstractmethod
from queue import Queue
from threading import Event, Thread
from typing import Any, Dict, Iterator, Optional


class JsonRpcError(Exception):
    """An error occurred in your request to the JSON-RPC API."""


class RpcTransport(ABC):
    """Chatmail RPC client's transport."""

    @abstractmethod
    def call(self, method: str, *args) -> Any:
        """Request the RPC server to call a function and return its return value if any."""


class _Result:
    def __init__(self) -> None:
        self._value: Any = None
        self._event = Event()

    def set(self, value: Any) -> None:
        self._value = value
        self._event.set()

    def wait(self) -> Any:
        self._event.wait()
        return self._value


class IOTransport:
    """Chatmail RPC transport over IO using external deltachat-rpc-server program."""

    def __init__(
        self,
        accounts_dir: Optional[str] = None,
        rpc_executable: str = "deltachat-rpc-server",
        **kwargs,
    ):
        """The given arguments will be passed to subprocess.Popen()"""
        self.logger = logging.getLogger("deltachat2.IOTransport")
        if accounts_dir:
            kwargs["env"] = {
                **kwargs.get("env", os.environ),
                "DC_ACCOUNTS_PATH": str(accounts_dir),
            }
        self.rpc_executable = rpc_executable
        self._kwargs = kwargs
        self.process: subprocess.Popen
        self.id_iterator: Iterator[int]
        # Map from request ID to the result.
        self.pending_results: Dict[int, _Result]
        self.request_queue: Queue
        self.closing: bool
        self.reader_thread: Thread
        self.writer_thread: Thread

    def start(self) -> None:
        """Start the RPC server process."""
        if sys.version_info >= (3, 11):
            # Prevent subprocess from capturing SIGINT.
            kwargs = {"process_group": 0, **self._kwargs}
        else:
            # `process_group` is not supported before Python 3.11.
            kwargs = {"preexec_fn": os.setpgrp, **self._kwargs}
        self.process = subprocess.Popen(  # noqa: consider-using-with
            self.rpc_executable,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            **kwargs,
        )
        self.id_iterator = itertools.count(start=1)
        self.pending_results = {}
        self.request_queue = Queue()
        self.closing = False
        self.reader_thread = Thread(target=self._reader_loop)
        self.reader_thread.start()
        self.writer_thread = Thread(target=self._writer_loop)
        self.writer_thread.start()

    def close(self) -> None:
        """Terminate RPC server process and wait until the reader loop finishes."""
        self.closing = True
        self.call("stop_io_for_all_accounts")
        assert self.process.stdin
        self.process.stdin.close()
        self.reader_thread.join()
        self.request_queue.put(None)
        self.writer_thread.join()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, _exc_type, _exc, _tb):
        self.close()

    def _reader_loop(self) -> None:
        try:
            assert self.process.stdout
            while True:
                line = self.process.stdout.readline()
                if not line:  # EOF
                    break
                response = json.loads(line)
                if "id" in response:
                    self.pending_results.pop(response["id"]).set(response)
                else:
                    self.logger.warning("Got a response without ID: %s", response)
        except Exception:
            # Log an exception if the reader loop dies.
            self.logger.exception("Exception in the reader loop")

    def _writer_loop(self) -> None:
        """Writer loop ensuring only a single thread writes requests."""
        try:
            assert self.process.stdin
            while True:
                request = self.request_queue.get()
                if not request:
                    break
                data = (json.dumps(request) + "\n").encode()
                self.process.stdin.write(data)
                self.process.stdin.flush()
        except Exception:
            # Log an exception if the writer loop dies.
            self.logger.exception("Exception in the writer loop")

    def call(self, method: str, *args) -> Any:
        """Request the RPC server to call a function and return its return value if any."""
        request_id = next(self.id_iterator)
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": args,
            "id": request_id,
        }
        result = self.pending_results[request_id] = _Result()
        self.request_queue.put(request)
        response = result.wait()

        if "error" in response:
            raise JsonRpcError(response["error"])
        if "result" in response:
            return response["result"]
        return None
