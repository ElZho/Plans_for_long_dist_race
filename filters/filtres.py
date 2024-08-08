import logging
# from datetime import timedelta

from aiogram.filters import BaseFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from re import findall

from database import Database


# from database_old.methods import check_user
# from services.services import get_plan_id, collect_my_race_report


logger = logging.getLogger(__name__)


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
    async def __call__(self, message: Message, db: Database) -> bool:
        logging.info("Enter users filters")
        user = await db.get_users_data(message.from_user.id)

        if user:
            logging.info("Users found")
            return True
        else:
            logging.info("Users not found")
            return False


class IsAdmin(BaseFilter):

    # Использую имя ключа в сигнатуре метода для проверки принадлежности к администратору
    async def __call__(self, message: Message, admin_ids: list[int]) -> bool:

        return message.from_user.id == int(admin_ids)


class CheckRaces(BaseFilter):
    async def __call__(self, callback: CallbackQuery, db: Database) -> bool:
        result = False

        if callback.data.isdigit():

            list_of_races = await db.get_race_from_id(callback.from_user.id, int(callback.data))
            if list_of_races:

                result = True

        return result


class CheckPlans(BaseFilter):
    async def __call__(self, callback: CallbackQuery, db: Database) -> bool:
        logging.info("Enter plans filters")
        if callback.data.isdigit():
            list_of_plans = await db.get_my_plans_ids(callback.from_user.id)

            return int(callback.data) in list_of_plans
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


class CheckResults(BaseFilter):
    async def __call__(self, callback: CallbackQuery, db: Database) -> bool:
        logging.info("Enter plans filters")
        if callback.data.isdigit():
            list_of_races = await db.get_my_race_id(callback.from_user.id)

            return int(callback.data) in list_of_races
        else:
            return False


class CheckTrainDist(BaseFilter):

    # Check if it is true plan
    async def __call__(self, callback: CallbackQuery, plans: dict) -> bool:

        return callback.data in plans.keys()


class CheckRaceDist(BaseFilter):

    # Check if it is true plan
    async def __call__(self, callback: CallbackQuery, vdot_guides: list) -> bool:

        return callback.data != "VD0T" and callback.data in vdot_guides[0].keys()


class CheckIntervals(BaseFilter):

    # Check if it is true plan
    async def __call__(self, callback: CallbackQuery, state: FSMContext) -> bool:
        data = await state.get_data()
        if float(callback.data) in data['intervals'].keys():
            return True

        return False


class CheckTrainTimes(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        times = message.text.split(' ')
        if all(map(str.isdigit, times)):
            result = []

            for item in times:
                match = findall(r'(\d{2})', item)
                res = (len(match) == 3) and \
                      (0 <= int(match[0]) < 25) and \
                      (0 <= int(match[1]) < 61) and \
                      (0 <= int(match[2]) < 61)
                result.append(res)

            return all(result)

        return False
