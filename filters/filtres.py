from datetime import timedelta

from aiogram.filters import BaseFilter
from aiogram.fsm.context import FSMContext
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

        return message.from_user.id == int(admin_ids)


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


class CheckProfileData(BaseFilter):
    """Check data according to states data (age, weight, height)"""

    async def __call__(self, message: Message, state: FSMContext) -> bool:
        data = await state.get_data()
        val = message.text
        res = False
        if data['key'] == 'age':
            res = (val.isdigit() and 16 <= int(val) <= 90)

        elif data['key'] == 'weight':
            res = (val.replace(',', '').replace('.', '').isdigit()
                   and 35.0 <= float(val.replace(',', '.')) <= 150.0)

        elif data['key'] == 'height':
            res = (val.replace(',', '').replace('.', '').isdigit()
                   and 135.0 <= float(val.replace(',', '.')) <= 250.0)

        return res


class CheckDist(BaseFilter):
    async def __call__(self, message: Message) -> bool:

        return message.text.replace(',', '').replace('.', '').isdigit()
