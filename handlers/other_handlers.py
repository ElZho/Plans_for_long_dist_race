from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram.fsm.state import default_state

from lexicon.lexicon_ru import LEXICON_RU


router = Router()

# Этот хэндлер будет срабатывать на команду "/cancel" в состоянии
# по умолчанию и сообщать, что ничего и не рассчитывалось
@router.message(Command(commands='cancel'), StateFilter(default_state))
async def process_cancel_command(message: Message):
    await message.answer(
        text=LEXICON_RU['cansel out FSM']
    )


# Этот хэндлер будет срабатывать на любой текст в состоянии
# по умолчанию и сообщать, что пользователь не находится в процессе заполнения формы
@router.message(~StateFilter(default_state))
async def process_some_command(message: Message):
    await message.answer(
        text=LEXICON_RU['message out FSM']
    )