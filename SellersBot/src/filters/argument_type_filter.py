from typing import Literal

from aiogram.types import Message
from aiogram.filters import Filter
from urllib.parse import urlparse

from ..tools import get_arguments


def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


class ArgumentType(Filter):
    def __init__(self, index: int, expected_type: Literal["str", "int", "url", "any"],
                 inverted: bool = False) -> None:
        if not isinstance(index, int):
            raise TypeError
        if not isinstance(expected_type, str):
            raise TypeError
        if not isinstance(inverted, bool):
            raise TypeError
        if expected_type not in ["str", "int", "url", "any"]:
            raise ValueError("Unexpected type")

        self.index = index
        self.expected_type = expected_type
        self.inverted = inverted

    async def __call__(self, message: Message) -> bool:
        arguments = get_arguments(message.text)

        if len(arguments) <= self.index:
            return self.inverted is not False

        if self.expected_type == "int":
            try:
                int(arguments[self.index])
            except ValueError:
                return self.inverted is not False
            return self.inverted is not True
        elif self.expected_type == "str":
            return self.inverted is not True
        elif self.expected_type == "url":
            return self.inverted is not is_valid_url(arguments[self.index])
        elif self.expected_type == "any":
            return self.inverted is not True
