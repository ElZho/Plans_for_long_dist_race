import logging

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import (CallbackQuery, Message, FSInputFile, PhotoSize)
from aiogram.utils import formatting

from database.methods import get_users_profile
from filters.filtres import IsAdmin
from lexicon import lexicon_ru


logger = logging.getLogger(__name__)
router = Router()
router.message.filter(IsAdmin())


@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    text = lexicon_ru.LEXICON_RU['admins_commands'] + '\n\n' +\
            lexicon_ru.LEXICON_RU['help_for_authorized_user']
    await message.answer(
        text=text
    )


@router.message(Command(commands='get_my_users'))
async def process_start_command(message: Message):
    users = get_users_profile()
    text = []
    for user in users:
        text.append(formatting.as_line(user.user_name, user.gender, 'age:', str(user.age), 'plans:',str(user.tp_quant), sep=', '))
    content = formatting.as_marked_section(formatting.Bold("Твои пользователи:\n"),*text, marker="🔸 ",)

    await message.answer(
        **content.as_kwargs()
    )
