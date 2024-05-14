from aiogram import F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import (CallbackQuery, Message, PhotoSize)
from datetime import timedelta


from states.states import FSMFillForm
from keyboards.keyboards import Sex_markup, Dist_markup, Yes_no_markup
from lexicon.lexicon_ru import LEXICON_RU

router = Router()

user_dict: dict[int, dict[str, str | int | bool]] = {}


# Этот хэндлер будет срабатывать на команду /start вне состояний
# и предлагать перейти к заполнению анкеты, отправив команду /fillform
@router.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message):
    await message.answer(
        text='Этот бот демонстрирует работу FSM\n\n'
             'Чтобы перейти к заполнению анкеты - '
             'отправьте команду /fillform'
    )


# Этот хэндлер будет срабатывать на команду /fillform
# и переводить бота в состояние ожидания ввода имени
@router.message(Command(commands='fillform'), StateFilter(default_state))
async def process_fillform_command(message: Message, state: FSMContext):
    await message.answer(text='Пожалуйста, введите ваше имя')
    # Устанавливаем состояние ожидания ввода имени
    await state.set_state(FSMFillForm.fill_name)


# Этот хэндлер будет срабатывать, если введено корректное имя
# и переводить в состояние ожидания ввода возраста
@router.message(StateFilter(FSMFillForm.fill_name), F.text.isalpha())
async def process_name_sent(message: Message, state: FSMContext):
    # Cохраняем введенное имя в хранилище по ключу "name"
    await state.update_data(name=message.text)
    await message.answer(text='Спасибо!\n\nА теперь введите ваш возраст')
    # Устанавливаем состояние ожидания ввода возраста
    await state.set_state(FSMFillForm.fill_age)


# Этот хэндлер будет срабатывать, если во время ввода имени
# будет введено что-то некорректное
@router.message(StateFilter(FSMFillForm.fill_name))
async def warning_not_name(message: Message):
    await message.answer(
        text='То, что вы отправили не похоже на имя\n\n'
             'Пожалуйста, введите ваше имя\n\n'
             'Если вы хотите прервать заполнение анкеты - '
             'отправьте команду /cancel'
    )


# Этот хэндлер будет срабатывать, если введен корректный возраст
# и переводить в состояние выбора пола
@router.message(StateFilter(FSMFillForm.fill_age),
            lambda x: x.text.isdigit() and 16 <= int(x.text) <= 90)
async def process_age_sent(message: Message, state: FSMContext):
    # Cохраняем возраст в хранилище по ключу "age"
    await state.update_data(age=message.text)

    # Отправляем пользователю сообщение с клавиатурой
    await message.answer(
        text='Спасибо!\n\nУкажите ваш пол',
        reply_markup=Sex_markup
    )
    # Устанавливаем состояние ожидания выбора пола
    await state.set_state(FSMFillForm.fill_gender)


# Этот хэндлер будет срабатывать, если во время ввода возраста
# будет введено что-то некорректное
@router.message(StateFilter(FSMFillForm.fill_age))
async def warning_not_age(message: Message):
    await message.answer(
        text='Калькулятор рассчитан на возраст от 16 до 90\n\n'
             'Если ваш возраст отличается от указанного\n\nто вы можете прервать '
             'заполнение анкеты - отправьте команду /cancel'
    )


# Этот хэндлер будет срабатывать на нажатие кнопки при
# выборе пола и переводить в состояние ввода веса
@router.callback_query(StateFilter(FSMFillForm.fill_gender),
                   F.data.in_(['male', 'female']))
async def process_gender_press(callback: CallbackQuery, state: FSMContext):
    # Cохраняем пол (callback.data нажатой кнопки) в хранилище,
    # по ключу "gender"
    await state.update_data(gender=callback.data)
    # Удаляем сообщение с кнопками, потому что следующий этап - загрузка фото
    # чтобы у пользователя не было желания тыкать кнопки
    # Отправляем пользователю сообщение с клавиатурой
    await callback.message.delete()
    await callback.message.answer(
        text='Спасибо!\n\nУкажите ваш вес'

    )
    # Устанавливаем состояние ожидания выбора пола
    await state.set_state(FSMFillForm.fill_weight)


# Этот хэндлер будет срабатывать, если введен пол
# и переводить в состояние ввода дистанции
@router.message(StateFilter(FSMFillForm.fill_weight))
async def process_weight_sent(message: Message, state: FSMContext):
    # Cохраняем вес в хранилище по ключу "weight"
    await state.update_data(weight=message.text)

    # Отправляем пользователю сообщение с клавиатурой
    await message.answer(
        text='Спасибо!\n\nВведите дистанцию, за которую\nхотите ввести свои результаты',
        reply_markup=Dist_markup
    )
    # Устанавливаем состояние ожидания выбора пола
    await state.set_state(FSMFillForm.fill_res_distantion)


# Этот хэндлер будет срабатывать, если во время ввода возраста
# будет введено что-то некорректное
@router.message(StateFilter(FSMFillForm.fill_weight))
async def warning_not_weight(message: Message):
    await message.answer(
        text='Калькулятор рассчитан на вес от 35 до 150 кг\n\n'
             'Если ваш вес отличается от указанного,\n\nто вы можете прервать '
             'заполнение анкеты - отправьте команду /cancel'
    )


# Этот хэндлер будет срабатывать на нажатие кнопки при
# выборе дистанции и переводить в состояние ввода результата
@router.callback_query(StateFilter(FSMFillForm.fill_res_distantion),
           lambda x: x.data.isdigit() and 0 <= int(x.data) < 9)
async def process_res_distantion(callback: CallbackQuery, state: FSMContext):
    # Cохраняем дистанцию (callback.data нажатой кнопки) в хранилище,
    # по ключу "res_distantion"
    # print(1)
    # a = callback.data
    # print(a)
    await state.update_data(res_distantion=callback.data)
    # print(state.update_data['res_distantion'])

    # Отправляем пользователю сообщение с клавиатурой
    await callback.message.delete()
    await callback.message.answer(
        text='Спасибо!\n\nУкажите ваш результат. Сначала часы:'

    )
    # Устанавливаем состояние ожидания выбора пола
    await state.set_state(FSMFillForm.fill_res_hours)


# Этот хэндлер будет срабатывать, если во время ввода возраста
# будет введено что-то некорректное
@router.message(StateFilter(FSMFillForm.fill_res_distantion))
async def warning_not_distantion(message: Message):
    print(message.text)
    await message.answer(
        text='Часы должны быть целое число в пределах 24-х\n\n'
        'Если ошиблись, повторите ввод.'
    )


# Этот хэндлер будет срабатывать, если введен пол
# и переводить в состояние ввода дистанции
@router.message(StateFilter(FSMFillForm.fill_res_hours),
            lambda x: x.text.isdigit() and 0 <= int(x.text) <= 24)
async def process_age_sent(message: Message, state: FSMContext):
    # Cохраняем часы в хранилище по ключу "res_hours"
    await state.update_data(res_hours=int(message.text))

    # Отправляем пользователю сообщение с клавиатурой
    await message.answer(
        text='Спасибо!\n\nТеперь минуты'
    )
    # Устанавливаем состояние ожидания выбора пола
    await state.set_state(FSMFillForm.fill_res_minutes)


# Этот хэндлер будет срабатывать, если во время ввода возраста
# будет введено что-то некорректное
@router.message(StateFilter(FSMFillForm.fill_res_hours))
async def warning_not_age(message: Message):
    await message.answer(
        text='Часы должны быть целое число в пределах 24-х\n\n'
        'Если ошиблись, повторите ввод.'
    )


# Этот хэндлер будет срабатывать, если введен пол
# и переводить в состояние ввода дистанции
@router.message(StateFilter(FSMFillForm.fill_res_minutes),
            lambda x: x.text.isdigit() and 0 <= int(x.text) <= 60)
async def process_age_sent(message: Message, state: FSMContext):
    # Cохраняем минуты в хранилище по ключу "minutes"
    await state.update_data(res_minutes=int(message.text))

    # Отправляем пользователю сообщение с клавиатурой
    await message.answer(
        text='Спасибо!\n\nТеперь секунды'
    )
    # Устанавливаем состояние ожидания выбора пола
    await state.set_state(FSMFillForm.fill_res_sec)


# Этот хэндлер будет срабатывать, если во время ввода возраста
# будет введено что-то некорректное
@router.message(StateFilter(FSMFillForm.fill_res_minutes))
async def warning_not_age(message: Message):
    await message.answer(
        text='Минуты должны быть целое число в пределах 60-х\n\n'
        'Если ошиблись, повторите ввод.'
    )


# Этот хэндлер будет срабатывать, если введен пол
# и переводить в состояние ввода дистанции
@router.message(StateFilter(FSMFillForm.fill_res_sec),
            lambda x: x.text.isdigit() and (0 <= float(x.text) < 61
            or 0 <= int(x.text) <= 60))
async def process_sec_sent(message: Message, state: FSMContext):
    # Cохраняем секунды в хранилище по ключу "sec"
    await state.update_data(res_secs=float(message.text))
    # Отправляем пользователю сообщение с клавиатурой
    await message.answer(
        text='Спасибо!\n\nТеперь добавьте фото'
    )
    # Устанавливаем состояние ожидания выбора пола
    await state.set_state(FSMFillForm.upload_photo)


# Этот хэндлер будет срабатывать, если во время ввода возраста
# будет введено что-то некорректное
@router.message(StateFilter(FSMFillForm.fill_res_sec))
async def warning_not_sec(message: Message):
    await message.answer(
        text='Секунды должны быть в пределах 61-х\n\n'
        'Если ошиблись, повторите ввод.'
    )


# Этот хэндлер будет срабатывать, если отправлено фото
# и переводить в состояние выбора образования
@router.message(StateFilter(FSMFillForm.upload_photo),
                F.photo[-1].as_('largest_photo'))
async def process_photo_sent(message: Message,
                                 state: FSMContext,
                                 largest_photo: PhotoSize):
    # Cохраняем данные фото (file_unique_id и file_id) в хранилище
    # по ключам "photo_unique_id" и "photo_id"
    await state.update_data(
            photo_unique_id=largest_photo.file_unique_id,
            photo_id=largest_photo.file_id
        )
    user_dict[message.from_user.id] = await state.get_data()

    # Завершаем машину состояний
    await state.clear()
    # Отправляем пользователю сообщение с клавиатурой
    await message.answer(
        text='Спасибо!\n\n'
             'Чтобы посмотреть данные вашей '
             'анкеты - отправьте команду /showdata'
    )


# Этот хэндлер будет срабатывать на отправку команды /showdata
# и отправлять в чат данные анкеты, либо сообщение об отсутствии данных
@router.message(Command(commands='showdata'), StateFilter(default_state))
async def process_showdata_command(message: Message):
    # Отправляем пользователю анкету, если она есть в "базе данных"
    if message.from_user.id in user_dict:
        await message.answer_photo(
            photo=user_dict[message.from_user.id]['photo_id'],
            caption=f'Имя: {user_dict[message.from_user.id]["name"]}\n'
                    f'Возраст: {user_dict[message.from_user.id]["age"]}\n'
                    f'Пол: {user_dict[message.from_user.id]["gender"]}\n'
                    f'Вес: {user_dict[message.from_user.id]["weight"]}\n'
                    f'Дистанция: {user_dict[message.from_user.id]["res_distantion"]}\n'
                    f'Результат: {timedelta(hours=user_dict[message.from_user.id]["res_hours"],
                                  minutes=user_dict[message.from_user.id]["res_minutes"],
                                  seconds=user_dict[message.from_user.id]["res_secs"])}\n'
        )
    else:
        # Если анкеты пользователя в базе нет - предлагаем заполнить
        await message.answer(
            text='Вы еще не заполняли анкету. Чтобы приступить - '
            'отправьте команду /fillform'
        )