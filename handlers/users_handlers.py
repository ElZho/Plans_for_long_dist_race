import logging
import os
from aiogram import F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext
from aiogram.types import (CallbackQuery, Message, PhotoSize, FSInputFile, ErrorEvent)

from aiogram.utils import formatting
from datetime import timedelta, datetime
from re import findall

from services.services import format_plan_details, calculate_pulse_zones, calculate_imt, calculate_max_pulse, \
    calculate_vdot
from states.states import FSMFillForm
from keyboards.keyboards import create_pagination_keyboard, create_inline_kb
from lexicon.lexicon_ru import LEXICON_INLINE_BUTTUNS, LEXICON_SELECT_DIST, SHOW_DATA
from lexicon import lexicon_ru
from services.calculations import find_vdot
from services.planing import get_plan, sent_plan
from filters.filtres import CheckTime
from database.methods import add_user, create_profile, create_race_report, create_training_plan, create_plan_details

logger = logging.getLogger(__name__)
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
async def process_help_command(message: Message):
    await message.answer(
        text=lexicon_ru.LEXICON_RU['help']
    )


# Этот хэндлер будет срабатывать на команду "/cancel" в состоянии
# не равным по умолчанию и сообщать, что эта команда работает внутри машины состояний
@router.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(
        text=lexicon_ru.LEXICON_RU['cancel in FSM']
    )
    # Сбрасываем состояние и очищаем данные, полученные внутри состояний
    await state.clear()


@router.error()
async def error_handler(event: ErrorEvent):
    logger.critical("Critical error caused by %s", event.exception, exc_info=True)


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
# выборе пола, если выбран женский пол и переводить в состояние ввода веса
@router.callback_query(StateFilter(FSMFillForm.fill_gender))
async def process_gender_press(callback: CallbackQuery, state: FSMContext):
    # Получаем ранее сохраненные данные
    data = await state.get_data()
    # считаем максимальный пульс
    max_pulse = calculate_max_pulse(callback.data, data['age'])
    # Cохраняем пол (callback.data нажатой кнопки) в хранилище,
    # по ключу "gender" и максимальный пульс по ключу max_pulse
    await state.update_data(gender=callback.data, max_pulse=max_pulse)

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
async def process_res_time_sent(message: Message, state: FSMContext):
    # Превращаем часы, минуты, секунды в время"
    h, m, s = findall(r'(\d{2})', message.text)

    # Cохраняем часы в хранилище по ключу "result"
    await state.update_data(result=timedelta(hours=int(h), minutes=int(m), seconds=int(s)))

    # Отправляем пользователю сообщение с клавиатурой
    await message.answer(
        text=lexicon_ru.LEXICON_RU['time_sent']
    )
    # Устанавливаем состояние ожидания выбора фото
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
    pulse_zone = calculate_pulse_zones(user_dict['max_pulse'])
    # считаем индекс массы тела
    user_dict["IMT"] = calculate_imt(user_dict["weight"], user_dict["height"])
    # сохраняем данные
    await state.update_data(pulse_zone=pulse_zone, IMT=user_dict["IMT"])
    # готовим сообщение
    pulse = formatting.as_marked_section(
        formatting.Bold(lexicon_ru.LEXICON_RU['showdata'][0]),
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
                                 lexicon_ru.LEXICON_RU['showdata'][1],
                                 formatting.BotCommand('/save_data'),
                                 sep="\n\n",
                                 )
    await message.answer_photo(
        photo=user_dict['photo_id'],
        caption=caption.as_html())


@router.message(Command(commands='save_data'), StateFilter(FSMFillForm.wait_calc))
async def process_save_data_command(message: Message, state: FSMContext):
    user_dict = await state.get_data()
    add_user(message.from_user.id, user_dict["name"], user_dict['gender'])
    create_profile(message.from_user.id, user_dict['weight'], user_dict['height'], user_dict['age'],
                   user_dict['IMT'], user_dict['max_pulse'], user_dict['photo_id'])

    await message.answer(text=lexicon_ru.LEXICON_RU['save_data'])


@router.message(Command(commands='calculate'), StateFilter(FSMFillForm.wait_calc))
async def process_calculate_vdot_command(message: Message, state: FSMContext):
    # получаем данные пользователя
    user_dict = await state.get_data()

    # считаем VO2Max
    user_dict['vdot'], user_dict['results'] = (
        find_vdot(user_dict["res_distances"],
                  datetime.strptime(str(user_dict['result']), '%H:%M:%S')))
    if int(user_dict['vdot']) < 65:
        user_dict['count_tempo'], content = calculate_vdot(user_dict['results']['5000 м'],
                                                           user_dict['vdot'], user_dict['results'])

        # считаем темпы и оформляем достижимые результаты
        await state.update_data(count_tempo=user_dict['count_tempo'],
                                vdot=user_dict['vdot'])

        # сохраняем данные о текущих результатах пользователя
        create_race_report(message.from_user.id, user_dict['res_distances'], user_dict['result'], user_dict['vdot'])

        await message.answer(**content.as_kwargs(), reply_markup=create_inline_kb(2, LEXICON_SELECT_DIST))
        await state.set_state(FSMFillForm.select_dist)
    else:
        await message.answer(lexicon_ru.LEXICON_RU['process_calculate_vdot_command'][3].format(user_dict['vdot']))
        await state.clear()


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

    user_dict['page'] = len(user_dict['plan'])
    # сохраняем план в хранилище
    await state.update_data(plan=user_dict['plan'],
                            page=user_dict['page'])
    # формируем сообщение

    content = format_plan_details(user_dict['plan'][str(user_dict['page'])], user_dict['selected_dist'],
                                  user_dict['page'], ['/get_plan_in_file', '/save_plan'])

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

        content = format_plan_details(user_dict['plan'][str(user_dict['page'])], user_dict['selected_dist'],
                                      user_dict['page'], ['/get_plan_in_file', '/save_plan'])

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
        # text = user_dict['plan'][str(user_dict['page'])]

        content = format_plan_details(user_dict['plan'][str(user_dict['page'])], user_dict['selected_dist'],
                                      user_dict['page'], ['/get_plan_in_file', '/save_plan'])

        await callback.message.edit_text(**content.as_kwargs(), reply_markup=create_pagination_keyboard(
            'backward',
            f'{user_dict["page"]}/{len(user_dict['plan'])}',
            'forward'))
    await callback.answer()


@router.message(Command(commands='save_plan'), StateFilter(FSMFillForm.wait_sent_file))
async def process_save_plan(message: Message, state: FSMContext):
    # получаем данные
    user_dict = await state.get_data()
    dt = datetime.now()
    # создаем ид
    plan_id = message.from_user.id + int(dt.timestamp())
    # сохраняем в бд
    create_training_plan(message.from_user.id, user_dict['selected_dist'], plan_id)
    # сохраняем детали плана
    for k, v in user_dict['plan'].items():
        create_plan_details(message.from_user.id, plan_id, k, v[0], v[1], v[2])

    await message.answer(lexicon_ru.LEXICON_RU['save_plan'])

    await state.clear()


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
