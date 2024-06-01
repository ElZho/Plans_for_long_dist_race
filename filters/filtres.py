from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from re import findall

from database.methods import check_user
from services.services import get_plan_id, collect_my_race_report


class CheckTime(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        match = findall(r'(\d{2})', message.text)
        res = (len(match) == 3) and \
              (0 <= int(match[0]) < 25) and \
              (0 <= int(match[1]) < 61) and \
              (0 <= int(match[2]) < 61)

        return res


class IsAuthorized(BaseFilter):

    # Использую имя ключа в сигнатуре метода для проверки принадлежности к администратору
    async def __call__(self, message: Message) -> bool:
        return check_user(message.from_user.id)


class IsAdmin(BaseFilter):

    # Использую имя ключа в сигнатуре метода для проверки принадлежности к администратору
    async def __call__(self, message: Message, admin_ids: list[int]) -> bool:
        return message.from_user.id in admin_ids


class CheckPlans(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> bool:
        if callback.data.isdigit():
            list_of_plans = get_plan_id(callback.from_user.id)
            return int(callback.data) in list_of_plans
        else:
            return False


class CheckRaces(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> bool:
        if callback.data.isdigit():
            list_of_races = list(collect_my_race_report(callback.from_user.id).keys())
            return callback.data in list_of_races
        else:
            return False
