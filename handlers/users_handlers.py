from aiogram import F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import (CallbackQuery, Message, PhotoSize)
from datetime import timedelta, datetime
import tabulate


from states.states import FSMFillForm
from keyboards.keyboards import Sex_markup, Dist_markup, select_dist_markup, create_pagination_keyboard
from lexicon.lexicon_ru import LEXICON_INLINE_BUTTUNS, LEXICON_SELECT_DIST
from calc_func.calculations import find_vdot, count_target_tempo
from calc_func.planing import get_plan

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
    await state.update_data(age=float(message.text))

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
# выборе пола, если выбран мужской пол и переводить в состояние ввода веса
@router.callback_query(StateFilter(FSMFillForm.fill_gender),
                   F.data.in_(['male']))
async def process_gender_press(callback: CallbackQuery, state: FSMContext):
    # Cохраняем пол (callback.data нажатой кнопки) в хранилище,
    # по ключу "gender"
    data = await state.get_data()
    await state.update_data(gender=callback.data)
    await state.update_data(max_pulse=208. - 0.7*data['age'])
    # Удаляем сообщение с кнопками, потому что следующий этап - загрузка фото
    # чтобы у пользователя не было желания тыкать кнопки
    # Отправляем пользователю сообщение с клавиатурой
    await callback.message.delete()
    await callback.message.answer(
        text='Спасибо!\n\nУкажите ваш вес'

    )
    # Устанавливаем состояние ожидания выбора пола
    await state.set_state(FSMFillForm.fill_weight)


# Этот хэндлер будет срабатывать на нажатие кнопки при
# выборе пола, если выбран женский пол и переводить в состояние ввода веса
@router.callback_query(StateFilter(FSMFillForm.fill_gender),
                   F.data.in_(['female']))
async def process_gender_press(callback: CallbackQuery, state: FSMContext):
    # Cохраняем пол (callback.data нажатой кнопки) в хранилище,
    # по ключу "gender"
    data = await state.get_data()
    await state.update_data(gender=callback.data)
    await state.update_data(max_pulse=(206. - 0.88*data['age']) )
    # Удаляем сообщение с кнопками, потому что следующий этап - загрузка фото
    # чтобы у пользователя не было желания тыкать кнопки
    # Отправляем пользователю сообщение с клавиатурой
    await callback.message.delete()
    await callback.message.answer(
        text='Спасибо!\n\nУкажите ваш вес'

    )
    # Устанавливаем состояние ожидания выбора пола
    await state.set_state(FSMFillForm.fill_weight)


# Этот хэндлер будет срабатывать, если введен вес
# и переводить в состояние ввода дистанции
@router.message(StateFilter(FSMFillForm.fill_weight),
            lambda x: x.text.isdigit() and 35.0 <= int(x.text) <= 150.0)
async def process_weight_sent(message: Message, state: FSMContext):
    # Cохраняем вес в хранилище по ключу "weight"
    await state.update_data(weight=float(message.text))

    # Отправляем пользователю сообщение с клавиатурой
    await message.answer(
        text='Спасибо!\n\nВведите рост'
    )
    # Устанавливаем состояние ожидания выбора пола
    await state.set_state(FSMFillForm.fill_height)


# Этот хэндлер будет срабатывать, если во время ввода возраста
# будет введено что-то некорректное
@router.message(StateFilter(FSMFillForm.fill_weight))
async def warning_not_weight(message: Message):
    await message.answer(
        text='Калькулятор рассчитан на вес от 35 до 150 кг\n\n'
             'Если ваш вес отличается от указанного,\n\nто вы можете прервать '
             'заполнение анкеты - отправьте команду /cancel'
    )


# Этот хэндлер будет срабатывать, если введен вес
# и переводить в состояние ввода дистанции
@router.message(StateFilter(FSMFillForm.fill_height),
            lambda x: all(map(lambda b: b.isdigit(), x.text.split('.'))) and 135.0 <= float(x.text) <= 250.0)
async def process_weight_sent(message: Message, state: FSMContext):
    # Cохраняем вес в хранилище по ключу "weight"
    await state.update_data(height=float(message.text))

    # Отправляем пользователю сообщение с клавиатурой
    await message.answer(
        text='Спасибо!\n\nВведите дистанцию, за которую\nхотите ввести свои результаты',
        reply_markup=Dist_markup
    )
    # Устанавливаем состояние ожидания выбора пола
    await state.set_state(FSMFillForm.fill_res_distances)


# Этот хэндлер будет срабатывать, если во время ввода роста
# будет введено что-то некорректное
@router.message(StateFilter(FSMFillForm.fill_height))
async def warning_not_weight(message: Message):

    await message.answer(
        text='Калькулятор рассчитан на рост от 135 до 250 см\n\n'
             'Если ваш вес отличается от указанного,\n\nто вы можете прервать '
             'заполнение анкеты - отправьте команду /cancel'
    )


# Этот хэндлер будет срабатывать на нажатие кнопки при
# выборе дистанции и переводить в состояние ввода результата
@router.callback_query(StateFilter(FSMFillForm.fill_res_distances), F.data.in_(LEXICON_INLINE_BUTTUNS))
async def process_res_distances(callback: CallbackQuery, state: FSMContext):
    # Cохраняем дистанцию (callback.data нажатой кнопки) в хранилище,
    # по ключу "res_distances"

    await state.update_data(res_distances=callback.data)
    t=callback.data
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
    # Отправляем пользователю анкету, если она есть в "базе данных"
    user_dict[message.from_user.id]['result'] = timedelta(hours=user_dict[message.from_user.id]["res_hours"], minutes=user_dict[message.from_user.id]["res_minutes"],
                                  seconds=user_dict[message.from_user.id]["res_secs"])
    if message.from_user.id in user_dict:
        await message.answer_photo(
            photo=user_dict[message.from_user.id]['photo_id'],
            caption=
            f'Имя: {user_dict[message.from_user.id]["name"]}\n'
                    f'Возраст: {user_dict[message.from_user.id]["age"]}\n'
                    f'Пол: {user_dict[message.from_user.id]["gender"]}\n'
                    f'Вес: {user_dict[message.from_user.id]["weight"]}\n'
                    f'Рост: {user_dict[message.from_user.id]["height"]}\n'
                    f'Дистанция: {LEXICON_INLINE_BUTTUNS[user_dict[message.from_user.id]["res_distances"]]}\n'
                    f'Результат: {user_dict[message.from_user.id]['result'] }\n'
            # {timedelta(hours=user_dict[message.from_user.id]["res_hours"],
            #                       minutes=user_dict[message.from_user.id]["res_minutes"],
            #                       seconds=user_dict[message.from_user.id]["res_secs"])}\n
                    f'Индекс массы тела: {round(user_dict[message.from_user.id]["weight"]*1000/
                                                user_dict[message.from_user.id]["height"]**2, 2)}\n'
                    f'\bПульсовые зоны:\b \n'
                    f'Максимальный пульс: {round(user_dict[message.from_user.id]["max_pulse"])}\n'

                    f'I зона: {round(user_dict[message.from_user.id]["max_pulse"]*0.5)} - '
                                                        f'{round(user_dict[message.from_user.id]["max_pulse"]*0.6)}\n'
                    f'II зона: {round(user_dict[message.from_user.id]["max_pulse"] * 0.6)} - '
                                                        f'{round(user_dict[message.from_user.id]["max_pulse"] * 0.75)}\n'
                    f'III зона: {round(user_dict[message.from_user.id]["max_pulse"] * 0.75)} - '
                                                        f'{round(user_dict[message.from_user.id]["max_pulse"] * 0.85)}\n'
                    f'IV зона: {round(user_dict[message.from_user.id]["max_pulse"] * 0.85)} - '
                                                        f'{round(user_dict[message.from_user.id]["max_pulse"] * 0.95)}\n'
                    f'V зона: {round(user_dict[message.from_user.id]["max_pulse"] * 0.95)} - '
                                                            f'{round(user_dict[message.from_user.id]["max_pulse"])}\n'
                    f'/calculate'
        )

    # else:
    #     # Если анкеты пользователя в базе нет - предлагаем заполнить
    #     await message.answer(
    #         text='Вы еще не заполняли анкету. Чтобы приступить - '
    #         'отправьте команду /fillform'
    #     )

@router.message(Command(commands='calculate'), StateFilter(FSMFillForm.wait_calc))
async def process_calcvdot_command(message: Message, state: FSMContext):

    my_current_time = datetime.strptime(str(user_dict[message.from_user.id]['result']), '%H:%M:%S')

    distance = [user_dict[message.from_user.id]["res_distances"]]

    vdot, results = find_vdot(*distance, my_current_time)
    count_tempo = count_target_tempo(results['5000 м'], vdot)
    await state.update_data(count_tempo=count_tempo)

    await message.answer(text=tabulate.tabulate([(k, v) for k, v in results.items()]))
    await message.answer(text=tabulate.tabulate([(k, v) for k, v in count_tempo.items()]),
                         reply_markup=select_dist_markup)

    await state.set_state(FSMFillForm.select_dist)

@router.callback_query(StateFilter(FSMFillForm.select_dist), F.data.in_(LEXICON_SELECT_DIST))
async def process_calcvdot_command(callback: CallbackQuery, state: FSMContext):
    d = int(callback.data)
    x = await state.get_data()
    train_plan = get_plan(d, x['count_tempo'])
    user_dict[callback.from_user.id]['plan'] = dict(
        [(int(k), 'Week {}:\n-------\n1-st train: {}.\n2-nd train: {}.\n3-rd train: {}.'.format(k, *v))
         for k, v in train_plan.items()])
    user_dict[callback.from_user.id]['page'] = len(user_dict[callback.from_user.id]['plan'])

    text = user_dict[callback.from_user.id]['plan'][user_dict[callback.from_user.id]['page']]
    await callback.message.answer(text= text, reply_markup=create_pagination_keyboard(
                'backward',
                f'{(user_dict[callback.from_user.id]["page"]+1)}/{len(user_dict[callback.from_user.id]['plan'])}',
                'forward'))

    # Завершаем машину состояний
    # await state.clear()

# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки "вперед"
# во время взаимодействия пользователя с сообщением-книгой
@router.callback_query(F.data == 'forward')
async def process_forward_press(callback: CallbackQuery):
    if user_dict[callback.from_user.id]['page'] > 1:
        user_dict[callback.from_user.id]['page'] -= 1
        text = user_dict[callback.from_user.id]['plan'][user_dict[callback.from_user.id]['page']]
        await callback.message.edit_text(
            text=text,
            reply_markup=create_pagination_keyboard(
                'backward',
                f'{user_dict[callback.from_user.id]["page"]}/{len(user_dict[callback.from_user.id]['plan'])}',
                'forward'
            )
        )
    await callback.answer()

    # Этот хэндлер будет срабатывать на нажатие инлайн-кнопки "назад"
    # во время взаимодействия пользователя с сообщением-книгой
    @router.callback_query(F.data == 'backward')
    async def process_backward_press(callback: CallbackQuery):
        if user_dict[callback.from_user.id]['page'] < len(user_dict[callback.from_user.id]['plan']):
            user_dict[callback.from_user.id]['page'] += 1
            text = user_dict[callback.from_user.id]['plan'][user_dict[callback.from_user.id]['page']]
            await callback.message.edit_text(
                text=text,
                reply_markup=create_pagination_keyboard(
                    'backward',
                    f'{user_dict[callback.from_user.id]["page"]}/{len(user_dict[callback.from_user.id]['plan'])}',
                    'forward'
                )
            )
        await callback.answer()
