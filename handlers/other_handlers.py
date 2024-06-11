import logging

from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.fsm.state import default_state

from lexicon.lexicon_ru import LEXICON_RU
from states.states import FSMFillForm


logger = logging.getLogger(__name__)
router = Router()

# Этот хэндлер будет срабатывать на команду "/cancel" в состоянии
# по умолчанию и сообщать, что ничего и не рассчитывалось
@router.message(Command(commands='cancel'), StateFilter(default_state))
async def process_cancel_command(message: Message):
    await message.answer(
        text=LEXICON_RU['cancel out FSM']
    )


# Этот хэндлер будет срабатывать на любой текст в состоянии
# по умолчанию и сообщать, что пользователь не находится в процессе заполнения формы
@router.message(StateFilter(default_state))
async def process_some_message(message: Message):
    await message.answer(
        text=LEXICON_RU['message out FSM']
    )


# удалить в конце
# @router.message()
# async def process_echo_message(message: Message, state: FSMContext):
#     text = message.text
#     st = await state.get_state()
#     await message.answer(
#         text=text
#     )
