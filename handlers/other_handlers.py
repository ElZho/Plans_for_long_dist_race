import logging

from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import default_state
from fluentogram import TranslatorRunner


logger = logging.getLogger(__name__)
router = Router()

# Этот хэндлер будет срабатывать на команду "/cancel" в состоянии
# по умолчанию и сообщать, что ничего и не рассчитывалось
@router.message(Command(commands='cancel'), StateFilter(default_state))
async def process_cancel_command(message: Message, i18n: TranslatorRunner):
    await message.answer(
        text=i18n.cancel_()
    )


# Этот хэндлер будет срабатывать на любой текст в состоянии
# по умолчанию и сообщать, что пользователь не находится в процессе заполнения формы
@router.message(StateFilter(default_state))
async def process_some_message(message: Message, i18n: TranslatorRunner):
    await message.answer(
        text=i18n.get('messageoutFSM')
    )


@router.callback_query(StateFilter(default_state))
async def process_some_callback(callback: CallbackQuery, i18n: TranslatorRunner):
    await callback.message.answer(
        text=i18n.get('unidentifiedcallback')
    )


@router.message(~StateFilter(default_state))
async def process_some_message(message: Message, i18n: TranslatorRunner):
    await message.answer(
        text=i18n.get('notgetit', data=message.text)
    )


@router.callback_query(~StateFilter(default_state))
async def process_some_callback(callback: CallbackQuery, i18n: TranslatorRunner):
    await callback.message.answer(
        text=i18n.get('notgetit', data=callback.data)
    )

