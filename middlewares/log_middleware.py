import os

from unittest.mock import sentinel


import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext

from aiogram.types import TelegramObject

logger = logging.getLogger(__name__)


class LogMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:


        result = await handler(event, data)

        if result == sentinel.UNHANDLED:
            state: FSMContext = data.get('state')
            state_val = await state.get_state()

            mess = event.message

            if not mess:

                mess = event.callback_query.message.reply_markup.inline_keyboard[0][0].text + ' - callback_data = ' + event.callback_query.message.reply_markup.inline_keyboard[0][0].callback_data
            else:
                mess = mess.text

            # logger.info(' UNHANDLED message: %s',  event.message.text, format('[%(asctime)s] #%(levelname)  - %(message)s'))
            logger.info(' UNHANDLED message: %s state %s',  mess, state_val
                        )

        return result
