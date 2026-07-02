"""Internal utilities"""

# flake8: noqa
import dataclasses
import re
from typing import Any


def camel2snake(name: str) -> str:
    """Convert camelCase/PascalCase string to snake_case"""
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    name = re.sub("__([A-Z])", r"_\1", name)
    name = re.sub("([a-z0-9])([A-Z])", r"\1_\2", name)
    return name.lower()


def snake2camel(name: str) -> str:
    """Convert snake_case string to camelCase"""
    parts = name.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


def camel2snake_dict(arg: Any) -> Any:
    if isinstance(arg, dict):
        return {camel2snake(key): camel2snake_dict(value) for key, value in arg.items()}
    if isinstance(arg, list):
        return [camel2snake_dict(elem) for elem in arg]
    return arg


def snakeclass2cameldict(arg: Any) -> Any:
    if dataclasses.is_dataclass(arg):
        return {snake2camel(key): value for key, value in dataclasses.asdict(arg).items()}
    if isinstance(arg, list):
        return [snake2camel_dict(elem) for elem in arg]
    if isinstance(arg, dict):
        return {key: snake2camel_dict(val) for key, val in arg.items()}
    return arg
