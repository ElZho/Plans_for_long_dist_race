from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from lexicon.lexicon_ru import LEXICON_INLINE_BUTTUNS, LEXICON_YES_NO

# Создаем объекты инлайн-кнопок определение поля
male_button = InlineKeyboardButton(
        text='Мужской ♂',
        callback_data='male'
    )
female_button = InlineKeyboardButton(
        text='Женский ♀',
             callback_data='female'
    )

# Добавляем кнопки в клавиатуру (две в одном ряду и одну в другом)
keyboard: list[list[InlineKeyboardButton]] = [
        [male_button, female_button]
    ]
# Создаем объект инлайн-клавиатуры
Sex_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

# Инициализируем билдер
kb_builder = InlineKeyboardBuilder()

# Инициализируем список для кнопок
buttons: list[InlineKeyboardButton] = []

# Создаем кнопки игровой клавиатуры
for button in LEXICON_INLINE_BUTTUNS:
    buttons.append(InlineKeyboardButton(
        text=LEXICON_INLINE_BUTTUNS[button] if button in LEXICON_INLINE_BUTTUNS else button,
        callback_data=button))

# Создаем клавиатуру с кнопками результата ответа
kb_builder.row(*buttons, width=3)
Dist_markup = kb_builder.as_markup()

# Инициализируем билдер
yes_no_kb_builder = InlineKeyboardBuilder()

# Инициализируем список для кнопок
y_n_buttons: list[InlineKeyboardButton] = []

# Создаем кнопки с ответами согласия и отказа
for button in LEXICON_YES_NO:
    y_n_buttons.append(InlineKeyboardButton(
        text=LEXICON_YES_NO[button] if button in LEXICON_YES_NO else button,
        callback_data=button))

# Добавляем кнопки в билдер с аргументом width=2
yes_no_kb_builder.row(*y_n_buttons, width=2)

# Создаем клавиатуру с кнопками "Давай!" и "Не хочу!"
Yes_no_markup = yes_no_kb_builder.as_markup()