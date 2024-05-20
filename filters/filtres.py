from aiogram.filters import BaseFilter
from aiogram.types import Message
from re import findall


class CheckTime(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        match = findall(r'(\d{2})', message.text)
        res = (len(match) == 3) and \
              (0 <= int(match[0]) < 25) and \
              (0 <= int(match[1]) < 61) and \
              (0 <= int(match[2]) < 61)

        return res
