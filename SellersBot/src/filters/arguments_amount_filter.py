from typing import Literal

from aiogram.types import Message
from aiogram.filters import Filter

from ..tools import remove_all_extra_spaces_for_arguments


class ArgumentsAmount(Filter):
    def __init__(self, operator: Literal[">", "<", "=", ">=", "<=", "!="], amount: int) -> None:
        if not isinstance(amount, int):
            raise TypeError("Invalid amount type!")
        if isinstance(amount, int) and amount < 0:
            raise ValueError("Negative amount of arguments is not possible!")
        if operator not in [">", "<", "=", ">=", "<=", "!="]:
            raise ValueError("Invalid operator!")

        self.amount = amount
        self.operation = operator

    async def __call__(self, message: Message) -> bool:
        arguments_amount = remove_all_extra_spaces_for_arguments(message.text).count(" ")
        if self.operation == "<":
            return arguments_amount < self.amount
        elif self.operation == "<=":
            return arguments_amount <= self.amount
        elif self.operation == ">":
            return arguments_amount > self.amount
        elif self.operation == ">=":
            return arguments_amount >= self.amount
        elif self.operation == "!=":
            return arguments_amount != self.amount
        return arguments_amount == self.amount

