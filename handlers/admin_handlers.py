import logging

from aiogram import Router
from aiogram.filters import Command

from aiogram.types import (Message)
from fluentogram import TranslatorRunner

from database import Database

from filters.filtres import IsAdmin
from lexicon import lexicon_ru


logger = logging.getLogger(__name__)
router = Router()
router.message.filter(IsAdmin())


# this handler works when user is admin and sand command help
@router.message(Command(commands='help'))
async def process_help_command(message: Message, i18n: TranslatorRunner):
    text = i18n.help_.admin()
    await message.answer(
        text=text
    )


# this handler works when admin wants to see all his users
@router.message(Command(commands='get_my_users'))
async def process_start_command(message: Message, db: Database, i18n: TranslatorRunner):

    users = await db.get_users_profile()
    users_info = []

    for user in users:

        users_info.append(i18n.get('getmyusers', case=1, usersname=user.user_name,
                                   age=user.age, plans=str(user.tp_quant)))

    await message.answer(text=i18n.get('getmyusers', case=0) + "\n🔸 " + "\n🔸 ".join(users_info))

