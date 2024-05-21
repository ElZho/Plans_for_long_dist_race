import os
from aiogram import F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext
from aiogram.types import (CallbackQuery, Message, PhotoSize, FSInputFile)

from aiogram.utils import formatting
from datetime import timedelta, datetime
from re import findall

from states.states import FSMFillForm
from keyboards.keyboards import create_pagination_keyboard, create_inline_kb
from lexicon.lexicon_ru import LEXICON_INLINE_BUTTUNS, LEXICON_SELECT_DIST, SHOW_DATA
from lexicon import lexicon_ru
from calc_func.calculations import find_vdot, count_target_tempo
from calc_func.planing import get_plan, sent_plan
from filters.filtres import CheckTime

router = Router()


# Этот хэндлер будет срабатывать на команду /start вне состояний
# и предлагать перейти к заполнению анкеты, отправив команду /fillform
@router.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message):
    await message.answer(
        text=lexicon_ru.LEXICON_RU['start']
    )


# Этот хэндлер будет срабатывать на команду /help вне состояний
# и рассказывать о возможностях системы и сообщать команды.
@router.message(Command(commands='help'))
async def process_start_command(message: Message):
    await message.answer(
        text=lexicon_ru.LEXICON_RU['help']
    )


# Этот хэндлер будет срабатывать на команду "/cancel" в состоянии
# не равным по умолчанию и сообщать, что эта команда работает внутри машины состояний
@router.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(
        text=lexicon_ru.LEXICON_RU['cansel in FSM']
    )
    # Сбрасываем состояние и очищаем данные, полученные внутри состояний
    await state.clear()


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


@router.callback_query(StateFilter(FSMFillForm.fill_gender),
                       ~ F.data.in_(['Женский', 'Мужской']))
async def process_gender_press(callback: CallbackQuery):
    await callback.answer(
        text=lexicon_ru.LEXICON_RU['wrong_ans']
    )


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
        text=lexicon_ru.LEXICON_RU['wrong_height']
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
        text=lexicon_ru.LEXICON_RU['select_distances'].format(t)
    )
    # Устанавливаем состояние ожидания выбора пола
    await state.set_state(FSMFillForm.fill_res_time)


# Этот хэндлер будет срабатывать, если во время ввода дистанции
# будет введено что-то некорректное
@router.message(StateFilter(FSMFillForm.fill_res_distances))
async def warning_not_distances(message: Message):
    await message.answer(
        text=lexicon_ru.LEXICON_RU['warning_not_distances']
    )


# Этот хэндлер будет срабатывать, если введенs часы
# и переводить в состояние ввода дистанции
@router.message(StateFilter(FSMFillForm.fill_res_time), CheckTime())
                # lambda x: len(findall(r'(\d{2})', x.text)) == 3)
async def process_res_time_sent(message: Message, state: FSMContext):
    # Превращаем часы, минуты, секунды в время"
    h, m, s = findall(r'(\d{2})', message.text)

    # Cохраняем часы в хранилище по ключу "result"
    await state.update_data(result=timedelta(hours=int(h), minutes=int(m), seconds=int(s)))

    # Отправляем пользователю сообщение с клавиатурой
    await message.answer(
        text=lexicon_ru.LEXICON_RU['time_sent']
    )
    # Устанавливаем состояние ожидания выбора пола
    await state.set_state(FSMFillForm.upload_photo)


# Этот хэндлер будет срабатывать, если во время ввода часов
# будет введено что-то некорректное
@router.message(StateFilter(FSMFillForm.fill_res_time))
async def warning_wrong_time(message: Message):
    await message.answer(
        text=lexicon_ru.LEXICON_RU['warning_wrong_time']
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
    # user_dict[message.from_user.id] = await state.get_data()
    # Отправляем пользователю сообщение с клавиатурой
    await message.answer(
        text=lexicon_ru.LEXICON_RU['photo_sent']
    )
    await state.set_state(FSMFillForm.wait_calc)


# Этот хэндлер будет срабатывать, если во время ввода часов
# будет введено что-то некорректное
@router.message(StateFilter(FSMFillForm.upload_photo), ~F.photo[-1].as_('largest_photo'))
async def warning_not_photo(message: Message):
    await message.answer(
        text=lexicon_ru.LEXICON_RU['not_photo']
    )


# Этот хэндлер будет срабатывать на отправку команды /showdata
# и отправлять в чат данные анкеты, либо сообщение об отсутствии данных
@router.message(Command(commands='showdata'), StateFilter(FSMFillForm.wait_calc))
async def process_showdata_command(message: Message, state: FSMContext):
    # получаем данные пользователя
    user_dict = await state.get_data()
    # считаем пульсовые зоны
    pulse_zone = [formatting.as_line(k, round(v[0] * user_dict['max_pulse']), '-',
                                     round(v[1] * user_dict["max_pulse"]), sep=' ')
                  for k, v in SHOW_DATA['pulse_zone'].items()]
    # считаем ИМТ
    user_dict["IMT"] = round(user_dict["weight"] * 1000 /
                             user_dict["height"] ** 2, 2)
    await state.update_data(pulse_zone=pulse_zone, IMT=user_dict["IMT"])
    # готовим сообщение
    pulse = formatting.as_marked_section(
        formatting.Bold(lexicon_ru.LEXICON_RU['showdata']),
        *pulse_zone,
        marker="🔸 ",
    )
    # формируем текст ответа
    name = f'Имя - {user_dict["name"]}\n'
    caption = formatting.as_list(formatting.as_section(formatting.Bold(name),
                                                       formatting.as_list(formatting.as_list(
                                                           *[formatting.as_key_value(v,
                                                                                     user_dict[k])
                                                             for k, v in
                                                             SHOW_DATA['photo_capt'].items()]), sep="\n\n", )),
                                 pulse,
                                 formatting.BotCommand('/calculate'),
                                 sep="\n\n",
                                 )
    # if message.from_user.id in user_dict:
    await message.answer_photo(
        photo=user_dict['photo_id'],
        caption=caption.as_html())


@router.message(Command(commands='calculate'), StateFilter(FSMFillForm.wait_calc))
async def process_calculate_vdot_command(message: Message, state: FSMContext):
    # получаем данные пользователя
    user_dict = await state.get_data()
    # my_current_time = datetime.strptime(str(user_dict[message.from_user.id]['result']), '%H:%M:%S')
    #
    # distance = user_dict[message.from_user.id]["res_distances"]
    # считаем VO2Max
    user_dict['vdot'], user_dict['results'] = (
        find_vdot(user_dict["res_distances"],
                  datetime.strptime(str(user_dict['result']), '%H:%M:%S')))
    # считаем темпы
    user_dict['count_tempo'] = (
        count_target_tempo(user_dict['results']['5000 м'],
                           user_dict['vdot']))
    await state.update_data(count_tempo=user_dict['count_tempo'],
                            vdot=user_dict['vdot'])
    # оформляем достижимые результаты
    target_results = [formatting.as_line(k, formatting.Italic(v), sep=' ')
                      for k, v in user_dict['results'].items() if k != 'VD0T']
    # оформляем темпы для тренировок
    paces = [formatting.as_line(k, v, sep=' ') for k, v in user_dict['count_tempo'].items()]
    # оформляем сообщение
    content = formatting.as_list(
        formatting.as_line(lexicon_ru.LEXICON_RU['process_calculate_vdot_command'][0],
                           user_dict['results']['VD0T']),
        formatting.as_marked_section(
            formatting.Bold(lexicon_ru.LEXICON_RU['process_calculate_vdot_command'][1]),
            *target_results,
            marker="🔸 ", ),
        formatting.as_marked_section(
            formatting.Bold(lexicon_ru.LEXICON_RU['process_calculate_vdot_command'][2]),
            *paces,
            marker="🔸 ", ),
    )

    await message.answer(**content.as_kwargs(), reply_markup=create_inline_kb(2, LEXICON_SELECT_DIST))
    await state.set_state(FSMFillForm.select_dist)


@router.message(StateFilter(FSMFillForm.wait_calc))
async def warning_showdata_command(message: Message):
    await message.answer(
        text=(lexicon_ru.LEXICON_RU['wrong_ans'] + ' - ' + message.text)
    )


# получаем план тренировок и выкладываем его в виде книги
@router.callback_query(StateFilter(FSMFillForm.select_dist), F.data.in_(LEXICON_SELECT_DIST))
async def process_calculate_plan_command(callback: CallbackQuery, state: FSMContext):
    # сохраняем выбранную дистанцию в хранилище по ключу selected_dist
    await state.update_data(selected_dist=int(callback.data))
    # получаем данные из хранилища
    user_dict = await state.get_data()
    # запускаем расчет плана подготовки передав выбранную дистанцию и рассчитанные ранее темпы
    user_dict['plan'] = get_plan(int(callback.data),
                                 user_dict['count_tempo'])

    # user_dict[callback.from_user.id]['plan'] = train_plan
    #
    user_dict['page'] = len(user_dict['plan'])
    # сохраняем план в хранилище
    await state.update_data(plan=user_dict['plan'],
                            page=user_dict['page'])
    # формируем сообщение
    text = user_dict['plan'][str(user_dict['page'])]
    page = lexicon_ru.LEXICON_RU['process_calculate_plan_command'][0].format(user_dict['page'])
    # преобразуем план в текстовый формат для вывода пользователю
    training = [formatting.as_key_value(formatting.as_line(i + 1,
                                                               lexicon_ru.LEXICON_RU['process_calculate_plan_command'][
                                                                   1],
                                                               end='\n------------------------------\n'),
                                            text[i],) for i in range(3)]

    content = formatting.as_list(
        formatting.Underline(
            formatting.as_line(lexicon_ru.LEXICON_RU['process_calculate_plan_command'][2],
                               lexicon_ru.LEXICON_SELECT_DIST[str(user_dict['selected_dist'])])),
        formatting.as_marked_section(
            formatting.Bold(page),
            *training,
            marker="🔸 ",
        ),
        formatting.BotCommand('/get_plan_in_file')
    )
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(**content.as_kwargs(), reply_markup=create_pagination_keyboard(
        'backward',
        f'{user_dict["page"]}/{len(user_dict['plan'])}',
        'forward'))
    await state.set_state(FSMFillForm.wait_sent_file)


# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки "вперед"
# во время взаимодействия пользователя с сообщением-книгой
@router.callback_query(StateFilter(FSMFillForm.wait_sent_file), F.data == 'forward')
async def process_forward_press(callback: CallbackQuery, state: FSMContext):
    # получаем данные из хранилища
    user_dict = await state.get_data()
    if user_dict['page'] > 1:
        # перелистываем страницу назад
        user_dict['page'] -= 1
        await state.update_data(page=user_dict['page'])
        # получаем текст страницы
        text = user_dict['plan'][str(user_dict['page'])]
        page = lexicon_ru.LEXICON_RU['process_calculate_plan_command'][0].format(
            user_dict['page'])

        training = [formatting.as_key_value(formatting.as_line(i + 1,
                                                               lexicon_ru.LEXICON_RU['process_calculate_plan_command'][
                                                                   1],
                                                               end='\n------------------------------\n'),
                                            text[i], ) for i in range(3)]

        content = formatting.as_list(
            formatting.Underline(
                formatting.as_line(lexicon_ru.LEXICON_RU['process_calculate_plan_command'][2],
                                   lexicon_ru.LEXICON_SELECT_DIST[
                                       str(user_dict['selected_dist'])])),
            formatting.as_marked_section(
                formatting.Bold(page),
                *training,
                marker="🔸 ",
            ),
            formatting.BotCommand('/get_plan_in_file')
        )
        await callback.message.edit_text(**content.as_kwargs(), reply_markup=create_pagination_keyboard(
            'backward',
            f'{user_dict["page"]}/{len(user_dict['plan'])}',
            'forward'))

    await callback.answer()


# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки "назад"
# во время взаимодействия пользователя с сообщением-книгой
@router.callback_query(StateFilter(FSMFillForm.wait_sent_file), F.data == 'backward')
async def process_backward_press(callback: CallbackQuery, state: FSMContext):
    # получаем данные из хранилища
    user_dict = await state.get_data()
    # проверяем долистали ли страницу до конца
    if user_dict['page'] < len(user_dict['plan']):
        user_dict['page'] += 1
        # обновляем хранилище
        await state.update_data(page=user_dict['page'])
        # формируем текст сообщения
        text = user_dict['plan'][str(user_dict['page'])]
        page = lexicon_ru.LEXICON_RU['process_calculate_plan_command'][0].format(
            user_dict['page'])
        training = [formatting.as_key_value(formatting.as_line(i + 1,
                                                               lexicon_ru.LEXICON_RU['process_calculate_plan_command'][
                                                                   1],
                                                               end='\n------------------------------\n'),
                                            text[i],) for i in range(3)]

        content = formatting.as_list(
            formatting.Underline(
                formatting.as_line(lexicon_ru.LEXICON_RU['process_calculate_plan_command'][2],
                                   lexicon_ru.LEXICON_SELECT_DIST[
                                       str(user_dict['selected_dist'])])),
            formatting.as_marked_section(
                formatting.Bold(page),
                *training,
                marker="🔸 ",
            ),
            formatting.BotCommand('/get_plan_in_file')
        )
        await callback.message.edit_text(**content.as_kwargs(), reply_markup=create_pagination_keyboard(
            'backward',
            f'{user_dict["page"]}/{len(user_dict['plan'])}',
            'forward'))
    await callback.answer()


@router.message(Command(commands='get_plan_in_file'), StateFilter(FSMFillForm.wait_sent_file))
async def process_sent_file(message: Message, state: FSMContext):
    # получаем данные пользователя из хранилища
    # получаем данные из хранилища
    user_dict = await state.get_data()
    # упаковываем в файл txt
    filename = sent_plan(LEXICON_SELECT_DIST[str(user_dict['selected_dist'])],
                         lexicon_ru.LEXICON_RU['Info_text'], user_dict['plan'], message.chat.id)
    # отправляем
    doc = FSInputFile(filename)
    await message.reply_document(doc)
    # удаляем файл
    os.remove(filename)
    await state.clear()


@router.message(StateFilter(FSMFillForm.wait_calc))
async def warning_showdata_command(message: Message, state: FSMContext):
    await message.answer(
        text=(lexicon_ru.LEXICON_RU['wrong_ans'] + ' - ' + message.text)
    )
    await state.clear()


# Этот хэндлер будет срабатывать на любой текст в состоянии
# по умолчанию и сообщать, что пользователь не находится в процессе заполнения формы
@router.message(Command(commands='esc'), ~StateFilter(default_state))
async def process_esc(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text='Все очистил - начинай сначала!'
    )
