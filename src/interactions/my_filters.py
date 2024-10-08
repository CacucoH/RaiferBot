from typing import Any
from aiogram.filters import BaseFilter
from aiogram.types import Message


class ChatTypeFilter(BaseFilter):
    def __init__(self, allowed_types: list[str] | str):
        self.allowed_types = allowed_types

    async def __call__(self, message: Message) -> bool:
        if not isinstance(self.allowed_types, str):
            return message.chat.type in self.allowed_types
        else:
            return message.chat.type == self.allowed_types