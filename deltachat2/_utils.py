"""Internal utilities"""

import re
from typing import Union


class AttrDict(dict):
    """Dictionary that allows accessing values using the "dot notation" as attributes."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(
            {
                _camel_to_snake(key): to_attrdict(value)
                for key, value in dict(*args, **kwargs).items()
            }
        )

    def __getattr__(self, attr):
        if attr in self:
            return self[attr]
        raise AttributeError("Attribute not found: " + str(attr))

    def __setattr__(self, attr, val):
        if attr in self:
            raise AttributeError("Attribute-style access is read only")
        super().__setattr__(attr, val)


def _camel_to_snake(name: str) -> str:
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    name = re.sub("__([A-Z])", r"_\1", name)
    name = re.sub("([a-z0-9])([A-Z])", r"\1_\2", name)
    return name.lower()


def to_attrdict(obj: Union[AttrDict, dict, list]) -> Union[AttrDict, list]:
    """Convert any dict or dict inside a list to AttrDict"""
    if isinstance(obj, AttrDict):
        return obj
    if isinstance(obj, dict):
        return AttrDict(obj)
    if isinstance(obj, list):
        return [to_attrdict(elem) for elem in obj]
    return obj
