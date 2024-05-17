from aiogram import F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import (CallbackQuery, Message, PhotoSize)
from aiogram.utils import formatting
from datetime import timedelta, datetime

from states.states import FSMFillForm
from keyboards.keyboards import Sex_markup, Dist_markup, select_dist_markup, create_pagination_keyboard, \
    create_inline_kb
from lexicon.lexicon_ru import LEXICON_INLINE_BUTTUNS, LEXICON_SELECT_DIST, SHOW_DATA
from lexicon import lexicon_ru
from calc_func.calculations import find_vdot, count_target_tempo
from calc_func.planing import get_plan

router = Router()

user_dict: dict[int, dict[str, str | int | bool]] = {}


# Этот хэндлер будет срабатывать на команду /start вне состояний
# и предлагать перейти к заполнению анкеты, отправив команду /fillform
@router.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message):
    await message.answer(
        text=lexicon_ru.LEXICON_RU['start']  # 'Этот бот демонстрирует работу FSM\n\n'
        # 'Чтобы перейти к заполнению анкеты - '
        # 'отправьте команду /fillform'
    )


# Этот хэндлер будет срабатывать на команду /fillform
# и переводить бота в состояние ожидания ввода имени
@router.message(Command(commands='fillform'), StateFilter(default_state))
async def process_fillform_command(message: Message, state: FSMContext):
    await message.answer(text=lexicon_ru.LEXICON_RU['fillform'])
    # Устанавливаем состояние ожидания ввода имени
    await state.set_state(FSMFillForm.fill_name)


# Этот хэндлер будет срабатывать, если введено корректное имя
# и переводить в состояние ожидания ввода возраста
@router.message(StateFilter(FSMFillForm.fill_name), F.text.isalpha())
async def process_name_sent(message: Message, state: FSMContext):
    # Cохраняем введенное имя в хранилище по ключу "name"
    await state.update_data(name=message.text)
    await message.answer(text=lexicon_ru.LEXICON_RU['name_sent'])
    # Устанавливаем состояние ожидания ввода возраста
    await state.set_state(FSMFillForm.fill_age)


# Этот хэндлер будет срабатывать, если во время ввода имени
# будет введено что-то некорректное
@router.message(StateFilter(FSMFillForm.fill_name))
async def wrong_name(message: Message):
    await message.answer(
        text=lexicon_ru.LEXICON_RU['wrong_name']
    )


# Этот хэндлер будет срабатывать, если введен корректный возраст
# и переводить в состояние выбора пола
@router.message(StateFilter(FSMFillForm.fill_age),
                lambda x: x.text.isdigit() and 16 <= int(x.text) <= 90)
async def process_age_sent(message: Message, state: FSMContext):
    # Cохраняем возраст в хранилище по ключу "age"
    await state.update_data(age=float(message.text))

    # Отправляем пользователю сообщение с клавиатурой
    await message.answer(
        text=lexicon_ru.LEXICON_RU['fill_age'],
        # Sex_markup
        reply_markup=create_inline_kb(2, lexicon_ru.Sex_buttons)
    )
    # Устанавливаем состояние ожидания выбора пола
    await state.set_state(FSMFillForm.fill_gender)


# Этот хэндлер будет срабатывать, если во время ввода возраста
# будет введено что-то некорректное
@router.message(StateFilter(FSMFillForm.fill_age))
async def wrong_age(message: Message):
    await message.answer(
        text=lexicon_ru.LEXICON_RU['wrong_not_age']
    )


# Этот хэндлер будет срабатывать на нажатие кнопки при
# выборе пола, если выбран мужской пол и переводить в состояние ввода веса
@router.callback_query(StateFilter(FSMFillForm.fill_gender),
                       F.data.in_(['Мужской']))
async def process_gender_press(callback: CallbackQuery, state: FSMContext):
    # Cохраняем пол (callback.data нажатой кнопки) в хранилище,
    # по ключу "gender"
    data = await state.get_data()
    await state.update_data(gender=callback.data)
    await state.update_data(max_pulse=round(208. - 0.7 * data['age']))
    # Удаляем сообщение с кнопками, потому что следующий этап - загрузка фото
    # чтобы у пользователя не было желания тыкать кнопки
    # Отправляем пользователю сообщение с клавиатурой
    await callback.message.delete()
    await callback.message.answer(
        text=lexicon_ru.LEXICON_RU['gender_press']
    )
    # Устанавливаем состояние ожидания выбора пола
    await state.set_state(FSMFillForm.fill_weight)


# Этот хэндлер будет срабатывать на нажатие кнопки при
# выборе пола, если выбран женский пол и переводить в состояние ввода веса
@router.callback_query(StateFilter(FSMFillForm.fill_gender),
                       F.data.in_(['Женский']))
async def process_gender_press(callback: CallbackQuery, state: FSMContext):
    # Cохраняем пол (callback.data нажатой кнопки) в хранилище,
    # по ключу "gender"
    data = await state.get_data()
    await state.update_data(gender=callback.data)
    await state.update_data(max_pulse=round(206. - 0.88 * data['age']))
    # Удаляем сообщение с кнопками, потому что следующий этап - загрузка фото
    # чтобы у пользователя не было желания тыкать кнопки
    # Отправляем пользователю сообщение с клавиатурой
    await callback.message.delete()
    await callback.message.answer(
        text=lexicon_ru.LEXICON_RU['gender_press']
    )
    # Устанавливаем состояние ожидания выбора пола
    await state.set_state(FSMFillForm.fill_weight)


# Этот хэндлер будет срабатывать, если введен вес
# и переводить в состояние ввода дистанции
@router.message(StateFilter(FSMFillForm.fill_weight),
                lambda x: x.text.replace(',', '').replace('.', '').isdigit()
                          and 35.0 <= float(x.text.replace(',', '.')) <= 150.0)
async def process_weight_sent(message: Message, state: FSMContext):
    # Cохраняем вес в хранилище по ключу "weight"
    await state.update_data(weight=float(message.text.replace(',', '.')))

    # Отправляем пользователю сообщение с клавиатурой
    await message.answer(
        text=lexicon_ru.LEXICON_RU['fill_weight']
    )
    # Устанавливаем состояние ожидания выбора пола
    await state.set_state(FSMFillForm.fill_height)


# Этот хэндлер будет срабатывать, если во время ввода возраста
# будет введено что-то некорректное
@router.message(StateFilter(FSMFillForm.fill_weight))
async def wrong_weight(message: Message):
    await message.answer(
        text=lexicon_ru.LEXICON_RU['wrong_weight']
    )


# Этот хэндлер будет срабатывать, если введен вес
# и переводить в состояние ввода дистанции
@router.message(StateFilter(FSMFillForm.fill_height),
                lambda x: x.text.replace(',', '').replace('.', '').isdigit()
                          and 135.0 <= float(x.text.replace(',', '.')) <= 250.0)
async def process_weight_sent(message: Message, state: FSMContext):
    # Cохраняем вес в хранилище по ключу "weight"
    await state.update_data(height=float(message.text.replace(',', '.')))

    # Отправляем пользователю сообщение с клавиатурой
    await message.answer(
        text=lexicon_ru.LEXICON_RU['fill_height'],
        # Dist_markup
        reply_markup=create_inline_kb(3,
                                      LEXICON_INLINE_BUTTUNS)
    )
    # Устанавливаем состояние ожидания выбора дистанции
    await state.set_state(FSMFillForm.fill_res_distances)


# Этот хэндлер будет срабатывать, если во время ввода роста
# будет введено что-то некорректное
@router.message(StateFilter(FSMFillForm.fill_height))
async def wrong_height(message: Message):
    await message.answer(
        text= lexicon_ru.LEXICON_RU['wrong_height']
    )


# Этот хэндлер будет срабатывать на нажатие кнопки при
# выборе дистанции и переводить в состояние ввода результата
@router.callback_query(StateFilter(FSMFillForm.fill_res_distances), F.data.in_(LEXICON_INLINE_BUTTUNS))
async def select_distances(callback: CallbackQuery, state: FSMContext):
    # Cохраняем дистанцию (callback.data нажатой кнопки) в хранилище,
    # по ключу "res_distances"
    await state.update_data(res_distances=callback.data)
    t = callback.data
    # Отправляем пользователю сообщение с клавиатурой
    await callback.message.delete()
    await callback.message.answer(
        text=f'{t} Спасибо!\n\nУкажите ваш результат. Сначала часы:'

    )
    # Устанавливаем состояние ожидания выбора пола
    await state.set_state(FSMFillForm.fill_res_hours)


# Этот хэндлер будет срабатывать, если во время ввода дистанции
# будет введено что-то некорректное
@router.message(StateFilter(FSMFillForm.fill_res_distances))
async def warning_not_distances(message: Message):
    await message.answer(
        text='Нажмите кнопку выбора дистанции\n\n'
             'Если ошиблись, повторите ввод.'
    )


# Этот хэндлер будет срабатывать, если введенs часы
# и переводить в состояние ввода дистанции
@router.message(StateFilter(FSMFillForm.fill_res_hours),
                lambda x: x.text.isdigit() and 0 <= int(x.text) <= 24)
async def process_hours_sent(message: Message, state: FSMContext):
    # Cохраняем часы в хранилище по ключу "res_hours"
    await state.update_data(res_hours=int(message.text))

    # Отправляем пользователю сообщение с клавиатурой
    await message.answer(
        text='Спасибо!\n\nТеперь минуты'
    )
    # Устанавливаем состояние ожидания выбора пола
    await state.set_state(FSMFillForm.fill_res_minutes)


# Этот хэндлер будет срабатывать, если во время ввода часов
# будет введено что-то некорректное
@router.message(StateFilter(FSMFillForm.fill_res_hours))
async def warning_not_age(message: Message):
    await message.answer(
        text='Часы должны быть целое число в пределах 24-х\n\n'
             'Если ошиблись, повторите ввод.'
    )


# Этот хэндлер будет срабатывать, если введены минуты
# и переводить в состояние ввода секунд
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


# Этот хэндлер будет срабатывать, если во время ввода минут
# будет введено что-то некорректное
@router.message(StateFilter(FSMFillForm.fill_res_minutes))
async def warning_not_age(message: Message):
    await message.answer(
        text='Минуты должны быть целое число в пределах 60-х\n\n'
             'Если ошиблись, повторите ввод.'
    )


# Этот хэндлер будет срабатывать, если введены секунды
# и переводить в состояние ввода фото
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


# Этот хэндлер будет срабатывать, если во время ввода секунд
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

    # Отправляем пользователю сообщение с клавиатурой
    await message.answer(
        text='Спасибо!\n\n'
             'Чтобы посмотреть данные вашей '
             'анкеты - отправьте команду /showdata'
    )
    await state.set_state(FSMFillForm.wait_calc)


# Этот хэндлер будет срабатывать на отправку команды /showdata
# и отправлять в чат данные анкеты, либо сообщение об отсутствии данных
@router.message(Command(commands='showdata'), StateFilter(FSMFillForm.wait_calc))
async def process_showdata_command(message: Message, state: FSMContext):
    # Превращаем часы, минуты, секунды в время"
    user_dict[message.from_user.id]['result'] = timedelta(hours=user_dict[message.from_user.id]["res_hours"],
                                                          minutes=user_dict[message.from_user.id]["res_minutes"],
                                                          seconds=user_dict[message.from_user.id]["res_secs"])
    # сохраняем в состояния
    await state.update_data(result=user_dict[message.from_user.id]['result'])
    # считаем пульсовые зоны
    pulse_zone = [formatting.as_line(k, round(v[0] * user_dict[message.from_user.id]["max_pulse"]), '-',
                                     round(v[1] * user_dict[message.from_user.id]["max_pulse"]), sep=' ')
                  for k, v in SHOW_DATA['pulse_zone'].items()]

    # готовим сообщение
    pulse = formatting.as_marked_section(
        formatting.Bold("Пульсовые зоны:"),
        *pulse_zone,
        marker="🔸 ",
    )
    # считаем ИМТ
    user_dict[message.from_user.id]["IMT"] = round(user_dict[message.from_user.id]["weight"] * 1000 /
                                                   user_dict[message.from_user.id]["height"] ** 2, 2)
    name = f'Имя - {user_dict[message.from_user.id]["name"]}\n'
    caption = formatting.as_list(formatting.as_section(formatting.Bold(name),
                                                       formatting.as_list(formatting.as_list(
                                                           *[f"{v}: {user_dict[message.from_user.id][k]}"
                                                             for k, v in
                                                             SHOW_DATA['photo_capt'].items()]), sep="\n\n", )),
                                 pulse,
                                 formatting.BotCommand('/calculate'),
                                 sep="\n\n",
                                 )
    if message.from_user.id in user_dict:
        await message.answer_photo(
            photo=user_dict[message.from_user.id]['photo_id'],
            caption=caption.as_html())


@router.message(Command(commands='calculate'), StateFilter(FSMFillForm.wait_calc))
async def process_calcvdot_command(message: Message, state: FSMContext):
    my_current_time = datetime.strptime(str(user_dict[message.from_user.id]['result']), '%H:%M:%S')

    distance = [user_dict[message.from_user.id]["res_distances"]]
    # считаем VO2Max
    vdot, results = find_vdot(*distance, my_current_time)
    # считаем темпы
    count_tempo = count_target_tempo(results['5000 м'], vdot)

    # оформляем достижимые результаты
    target_results = [formatting.as_line(k, formatting.Italic(v), sep=' ')
                      for k, v in results.items() if k != 'VD0T']
    # оформляем темпы для тренировок
    paces = [formatting.as_line(k, v, sep=' ') for k, v in count_tempo.items()]
    # оформляем сообщение
    content = formatting.as_list(formatting.as_line('Твой VO2max - ', results['VD0T']),
                                 formatting.as_marked_section(
        formatting.Bold("Достижимые результаты для тебя на разных дистанциях:\n"),
        *target_results,
        marker="🔸 ", ),
        formatting.as_marked_section(
            formatting.Bold("Твои тренировочные темпы для разных дистанций\n"),
            *paces,
            marker="🔸 ", ),
    )

    await state.update_data(count_tempo=count_tempo)
    await message.answer(**content.as_kwargs(), reply_markup=select_dist_markup)
    await state.set_state(FSMFillForm.select_dist)


@router.callback_query(StateFilter(FSMFillForm.select_dist), F.data.in_(LEXICON_SELECT_DIST))
async def process_calcvdot_command(callback: CallbackQuery, state: FSMContext):
    d = int(callback.data)
    x = await state.get_data()
    train_plan = get_plan(d, x['count_tempo'])
    user_dict[callback.from_user.id]['plan'] = train_plan
    #
    user_dict[callback.from_user.id]['page'] = len(user_dict[callback.from_user.id]['plan'])

    text = user_dict[callback.from_user.id]['plan'][str(user_dict[callback.from_user.id]['page'])]
    page = f"Неделя: {user_dict[callback.from_user.id]['page']}\n"
    training = [formatting.as_line(i + 1, '-я тренировка ', text[i]) for i in range(3)]

    content = formatting.as_marked_section(
        formatting.Bold(page),
        *training,
        marker="🔸 ",
    )
    await callback.message.delete()
    await callback.message.answer(**content.as_kwargs(), reply_markup=create_pagination_keyboard(
        'backward',
        f'{user_dict[callback.from_user.id]["page"]}/{len(user_dict[callback.from_user.id]['plan'])}',
        'forward'))

    await state.clear()


# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки "вперед"
# во время взаимодействия пользователя с сообщением-книгой
@router.callback_query(F.data == 'forward')
async def process_forward_press(callback: CallbackQuery):
    if user_dict[callback.from_user.id]['page'] > 1:
        user_dict[callback.from_user.id]['page'] -= 1
        text = user_dict[callback.from_user.id]['plan'][str(user_dict[callback.from_user.id]['page'])]
        page = f"Неделя: {user_dict[callback.from_user.id]['page']}\n"
        training = [formatting.as_line(i + 1, '-я тренировка ', text[i]) for i in range(3)]

        content = formatting.as_marked_section(
            formatting.Bold(page),
            *training,
            marker="🔸 ",
        )
        await callback.message.edit_text(**content.as_kwargs(), reply_markup=create_pagination_keyboard(
            'backward',
            f'{user_dict[callback.from_user.id]["page"]}/{len(user_dict[callback.from_user.id]['plan'])}',
            'forward'))
    await callback.answer()


# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки "назад"
# во время взаимодействия пользователя с сообщением-книгой
@router.callback_query(F.data == 'backward')
async def process_backward_press(callback: CallbackQuery):
    if user_dict[callback.from_user.id]['page'] < len(user_dict[callback.from_user.id]['plan']):
        user_dict[callback.from_user.id]['page'] += 1
        text = user_dict[callback.from_user.id]['plan'][str(user_dict[callback.from_user.id]['page'])]
        page = f"Неделя: {user_dict[callback.from_user.id]['page']}\n"
        training = [formatting.as_line(i + 1, '-я тренировка ', text[i]) for i in range(3)]

        content = formatting.as_marked_section(
            formatting.Bold(page),
            *training,
            marker="🔸 ",
        )
        await callback.message.edit_text(**content.as_kwargs(), reply_markup=create_pagination_keyboard(
            'backward',
            f'{user_dict[callback.from_user.id]["page"]}/{len(user_dict[callback.from_user.id]['plan'])}',
            'forward'))
    await callback.answer()
