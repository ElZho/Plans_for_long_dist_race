import logging
import os
from aiogram import F, Router, html
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext
from aiogram.types import (CallbackQuery, Message, PhotoSize, ErrorEvent)

from fluentogram import TranslatorRunner

from services.services import calculate_imt, calculate_max_pulse
from states.states import FSMFillForm
from keyboards.keyboards import create_inline_kb

from database import Database


logger = logging.getLogger(__name__)
router = Router()


# Этот хэндлер будет срабатывать на команду /start вне состояний
# и предлагать перейти к заполнению анкеты, отправив команду /fillform
@router.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message, i18n: TranslatorRunner):
    username = html.quote(message.from_user.full_name)
    await message.answer(
        text=i18n.hello.user(username=username)
    )


# Этот хэндлер будет срабатывать на команду /help вне состояний
# и рассказывать о возможностях системы и сообщать команды.
@router.message(Command(commands='help'))
async def process_help_command(message: Message, i18n: TranslatorRunner):
    await message.answer(
        text=i18n.help_.user()
    )


# Этот хэндлер будет срабатывать на команду "/cancel" в состоянии
# неравным по умолчанию и сообщать, что эта команда работает внутри машины состояний
@router.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext, i18n: TranslatorRunner):
    await message.answer(
        text=i18n.cancel_.in_.fsm_()
    )
    # Сбрасываем состояние и очищаем данные, полученные внутри состояний
    await state.clear()


@router.error()
async def error_handler(event: ErrorEvent):
    logger.critical("Critical error caused by %s", event.exception, exc_info=True)


# Этот хэндлер будет срабатывать на команду /fillform
# и переводить бота в состояние ожидания ввода имени
@router.message(Command(commands='fillform'), StateFilter(default_state))
async def process_fillform_command(message: Message, state: FSMContext, i18n: TranslatorRunner):
    await message.answer(text=i18n.fill.form())
    # Устанавливаем состояние ожидания ввода имени
    await state.set_state(FSMFillForm.fill_name)


# Этот хэндлер будет срабатывать, если введено корректное имя
# и переводить в состояние ожидания ввода возраста
@router.message(StateFilter(FSMFillForm.fill_name), F.text.isalpha(), F.text.istitle())
async def process_name_sent(message: Message, state: FSMContext, i18n: TranslatorRunner):
    # Cохраняем введенное имя в хранилище по ключу "name"
    name = message.text
    await state.update_data(name=message.text)
    await message.answer(text=i18n.get('name_-sent', name=name))
    # Устанавливаем состояние ожидания ввода возраста
    await state.set_state(FSMFillForm.fill_age)


# Этот хэндлер будет срабатывать, если во время ввода имени
# будет введено что-то некорректное
@router.message(StateFilter(FSMFillForm.fill_name))
async def wrong_name(message: Message, i18n: TranslatorRunner):
    await message.answer(
        text=i18n.get('wrong-name_', name=message.text) )


# Этот хэндлер будет срабатывать, если введен корректный возраст
# и переводить в состояние выбора пола
@router.message(StateFilter(FSMFillForm.fill_age),
                lambda x: x.text.isdigit() and 16 <= int(x.text) <= 90)
async def process_age_sent(message: Message, state: FSMContext, i18n: TranslatorRunner):
    # Cохраняем возраст в хранилище по ключу "age"
    await state.update_data(age=float(message.text))

    # Отправляем пользователю сообщение с клавиатурой
    await message.answer(
        text=i18n.age.sent(),
        # Sex_markup
        reply_markup=create_inline_kb(2, {'male':i18n.male(), 'female': i18n.female()})
    )
    # Устанавливаем состояние ожидания выбора пола
    await state.set_state(FSMFillForm.fill_gender)


# Этот хэндлер будет срабатывать, если во время ввода возраста
# будет введено что-то некорректное
@router.message(StateFilter(FSMFillForm.fill_age))
async def wrong_age(message: Message, i18n: TranslatorRunner):
    await message.answer(
        text=i18n.wrong.age()
    )


# Этот хэндлер будет срабатывать на нажатие кнопки при
# выборе пола, если выбран женский пол и переводить в состояние ввода веса
@router.callback_query(StateFilter(FSMFillForm.fill_gender), F.data.in_(['female', 'male']))
async def process_gender_press(callback: CallbackQuery, state: FSMContext, i18n: TranslatorRunner):
    # Получаем ранее сохраненные данные
    data = await state.get_data()
    # считаем максимальный пульс
    max_pulse,  physiologist = calculate_max_pulse(callback.data, data['age'])
    # Cохраняем пол (callback.data нажатой кнопки) в хранилище,
    # по ключу "gender" и максимальный пульс по ключу max_pulse
    await state.update_data(gender=callback.data, max_pulse=max_pulse)

    # Удаляем сообщение с кнопками, потому что следующий этап - загрузка фото
    # чтобы у пользователя не было желания тыкать кнопки
    # Отправляем пользователю сообщение с клавиатурой
    await callback.message.delete()
    await callback.message.answer(
        text=i18n.get('gender-pressed', physiologist=physiologist ,maxpulse=max_pulse)
    )
    # Устанавливаем состояние ожидания выбора пола
    await state.set_state(FSMFillForm.fill_weight)


@router.callback_query(StateFilter(FSMFillForm.fill_gender),
                       ~F.data.in_(['female', 'male']))
async def process_gender_press(callback: CallbackQuery, i18n: TranslatorRunner):
    """This handler works when user pressed wrong buttons"""
    await callback.answer(
        text=i18n.wrong.gender()
    )


# Этот хэндлер будет срабатывать, если введен вес
# и переводить в состояние ввода дистанции
@router.message(StateFilter(FSMFillForm.fill_weight),
                lambda x: x.text.replace(',', '').replace('.', '').isdigit()
                and 35.0 <= float(x.text.replace(',', '.')) <= 150.0)
async def process_weight_sent(message: Message, state: FSMContext, i18n: TranslatorRunner):
    # Cохраняем вес в хранилище по ключу "weight"
    await state.update_data(weight=float(message.text.replace(',', '.')))

    # Отправляем пользователю сообщение с клавиатурой
    await message.answer(
        text=i18n.fill.weight()
    )
    # Устанавливаем состояние ожидания выбора пола
    await state.set_state(FSMFillForm.fill_height)


# Этот хэндлер будет срабатывать, если во время ввода возраста
# будет введено что-то некорректное
@router.message(StateFilter(FSMFillForm.fill_weight), lambda x: x.text.replace(',', '').replace('.', '').isdigit()
                and not 35.0 <= float(x.text.replace(',', '.')) <= 150.0 )

async def wrong_weight(message: Message, i18n: TranslatorRunner):
    await message.answer(
        text=i18n.wrong.weight()
    )


# Этот хэндлер будет срабатывать, если введен вес
# и переводить в состояние ввода дистанции
@router.message(StateFilter(FSMFillForm.fill_height),
                lambda x: x.text.replace(',', '').replace('.', '').isdigit()
                and 135.0 <= float(x.text.replace(',', '.')) <= 250.0)
async def process_weight_sent(message: Message, state: FSMContext, i18n: TranslatorRunner):

    # Cохраняем вес в хранилище по ключу "weight"
    await state.update_data(height=float(message.text.replace(',', '.')))

    # # Sand message with answer
    await message.answer(text=i18n.fill.height())

    # Устанавливаем состояние ожидания выбора дистанции
    await state.set_state(FSMFillForm.upload_photo)


# Этот хэндлер будет срабатывать, если во время ввода роста
# будет введено что-то некорректное
@router.message(StateFilter(FSMFillForm.fill_height))
async def wrong_height(message: Message, i18n: TranslatorRunner):
    await message.answer(
        text=i18n.wrong.height()
    )

@router.message(StateFilter(FSMFillForm.upload_photo),
                F.photo[-1].as_('largest_photo'))
async def process_photo_sent(message: Message,
                             state: FSMContext,
                             largest_photo: PhotoSize, i18n: TranslatorRunner):
    # Cохраняем данные фото (file_unique_id и file_id) в хранилище
    # по ключам "photo_unique_id" и "photo_id"
    await state.update_data(
        photo_unique_id=largest_photo.file_unique_id,
        photo_id=largest_photo.file_id
    )

    # Отправляем пользователю сообщение с клавиатурой
    await message.answer(
        text=i18n.photo_.sent()
    )
    await state.set_state(FSMFillForm.show_data)

# Этот хэндлер будет срабатывать на отправку команды /showdata
# и отправлять в чат данные анкеты, либо сообщение об отсутствии данных
@router.message(Command(commands='showdata'), StateFilter(FSMFillForm.show_data))
async def process_showdata_command(message: Message, state: FSMContext, i18n: TranslatorRunner):
    # получаем данные пользователя
    user_dict = await state.get_data()

    # считаем индекс массы тела
    user_dict["IMT"] = calculate_imt(user_dict["weight"], user_dict["height"])

    # сохраняем данные
    await state.update_data(IMT=user_dict["IMT"])

    pulse_zones = i18n.get("showpulse", maxpulse=user_dict['max_pulse'],
                                beg1=0.5*user_dict['max_pulse'], end1=0.6*user_dict['max_pulse'],
                                beg2=0.6*user_dict['max_pulse'], end2=0.75*user_dict['max_pulse'],
                                beg3=0.75*user_dict['max_pulse'], end3=0.85*user_dict['max_pulse'],
                                beg4=0.85*user_dict['max_pulse'], end4=0.95*user_dict['max_pulse'],
                                beg5=0.95*user_dict['max_pulse'], end5=1.0*user_dict['max_pulse'])

    # show users data
    await message.answer_photo(
        photo=user_dict['photo_id'],
        caption=i18n.get("show_-data_", case=1, user_name=user_dict["name"], user_age=user_dict["age"],
                                user_gender=user_dict["gender"], weight=user_dict["weight"], height=user_dict["height"],
                                imt=user_dict["IMT"], pulsezones=pulse_zones)
                                )
    await state.set_state(FSMFillForm.save_data)


@router.message(Command(commands='save_data'), StateFilter(FSMFillForm.save_data))
async def process_showdata_command(message: Message, state: FSMContext, i18n: TranslatorRunner, db: Database):
    # получаем данные пользователя
    user_dict = await state.get_data()

    await db.add_user(tg_id=message.from_user.id, user_name=user_dict['name'], age=int(user_dict['age']),
                      gender=user_dict['gender'], weight=user_dict["weight"], height=user_dict["height"],
                      imt=user_dict["IMT"], max_pulse=user_dict['max_pulse'], photo_id=user_dict['photo_id']
    )


    await message.answer(i18n.save_.data_())

    await state.clear()

