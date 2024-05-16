from aiogram.fsm.state import State, StatesGroup

# Cоздаем класс, наследуемый от StatesGroup, для группы состояний нашей FSM
class FSMFillForm(StatesGroup):
    # Создаем экземпляры класса State, последовательно
    # перечисляя возможные состояния, в которых будет находиться
    # бот в разные моменты взаимодействия с пользователем
    fill_name = State()        # Состояние ожидания ввода имени
    fill_age = State()         # Состояние ожидания ввода возраста
    fill_gender = State()      # Состояние ожидания выбора пола
    fill_weight = State()     # Состояние ожидания ввода веса
    fill_height = State()  # Состояние ожидания ввода веса
    fill_res_distances = State()   # Состояние ожидания выбора дистанции для ввода результатов
    fill_res_hours = State()   # Состояние ожидания ввода часов
    fill_res_minutes = State()  # Состояние ожидания ввода минуты
    fill_res_sec = State()  # Состояние ожидания ввода секунд
    upload_photo = State() # ждем фото
    wait_calc = State()  # считаем VDOT
    select_dist = State()  # выбираем дистанцию подготовки
    plan_dist = State()  # планируем подготовку