from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
import psycopg2
import aiohttp


# Инициализация бота
bot = Bot(token="YOUR_TOKEN_HERE")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Подключение к базе данных
conn = psycopg2.connect(
    host="YOUR_HOST",
    database="YOUR_DATABASE",
    user="YOUR_USER",
    password="YOUR_PASSWORD",
    port=5432
)
cur = conn.cursor()

# States - определение состояний для машины состояний
class Registration(StatesGroup):
    login = State()

class AddOperation(StatesGroup):
    type_operation = State()
    sum_operation = State()
    date_operation = State()

class DeleteOperation(StatesGroup):
    id_operation = State()


# Обработчик команды /start
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    # Отправляется сообщение с приветствием и списком доступных команд
    # Также создается клавиатура с кнопками команд для удобства пользователя
    await message.reply("Welcome message")
    commands_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    commands_keyboard.add("/start", "/reg", "/add_operation", "/operations", "/delete_operation")
    await message.reply("Commands list", reply_markup=commands_keyboard)


# Обработчик команды /reg
@dp.message_handler(commands=["reg"])
async def reg(message: types.Message):
    # Регистрация пользователя, добавление его в базу данных
    # Перевод состояния в Registration.login для получения логина
    await Registration.login.set()
    await message.reply("Enter your login:")


# Обработчик для получения логина при регистрации пользователя
@dp.message_handler(state=Registration.login)
async def reg_login(message: types.Message, state: FSMContext):
    # Запись логина пользователя в базу данных
    login = message.text
    cur.execute("INSERT INTO users (name, chat_id) VALUES (%s, %s)", (login, message.chat.id))
    conn.commit()
    await state.finish()
    await message.reply("You have been successfully registered.")


# Добавление операции
@dp.message_handler(commands=["add_operation"])
async def add_operation(message: types.Message):
    # Определение типа операции: РАСХОД или ДОХОД
    # Перевод состояния в AddOperation.type_operation
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("РАСХОД", "ДОХОД")
    await message.reply("Select operation type", reply_markup=markup)
    await AddOperation.type_operation.set()


# Получение типа операции (РАСХОД или ДОХОД)
@dp.message_handler(state=AddOperation.type_operation)
async def add_operation_type(message: types.Message, state: FSMContext):
    # Запись типа операции в состояние
    type_operation = message.text
    await state.update_data(type_operation=type_operation)
    await message.reply("Enter operation sum:")


# Получение суммы операции
@dp.message_handler(state=AddOperation.sum_operation)
async def add_operation_sum(message: types.Message, state: FSMContext):
    # Запись суммы операции в состояние
    sum_operation = int(message.text)
    await state.update_data(sum_operation=sum_operation)
    await message.reply("Enter operation date (YYYY-MM-DD):")


# Получение даты операции
@dp.message_handler(state=AddOperation.date_operation)
async def add_operation_date(message: types.Message, state: FSMContext):
    # Запись даты операции в базу данных
    data = await state.get_data()
    type_operation = data["type_operation"]
    sum_operation = data["sum_operation"]
    cur.execute("INSERT INTO operations (date, sum, chat_id, type_operation) VALUES (%s, %s, %s, %s)",
               (message.text, sum_operation, message.chat.id, type_operation))
    conn.commit()
    await state.finish()
    await message.reply("Operation added.")


# Получение списка операций с возможностью выбора валюты
@dp.message_handler(commands=["operations"])
async def operations(message: types.Message):
    cur.execute("SELECT * FROM users WHERE chat_id = %s", (message.chat.id,))
    if not cur.fetchone():
        await message.reply("You are not registered. Please register using /reg.")
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("RUB", "EUR", "USD")
    await message.reply("Select currency", reply_markup=markup)


# Получение курса валюты и вывод списка операций
@dp.message_handler(lambda message: message.text in ["RUB", "EUR", "USD"])
async def operations_currency(message: types.Message):
    # Обработка выбора валюты и вывод операций
    pass  # Здесь дополнительный код для обработки выбранной валюты


# Удаление операции
@dp.message_handler(commands=["delete_operation"])
async def delete_operation(message: types.Message):
    cur.execute("SELECT * FROM users WHERE chat_id = %s", (message.chat.id,))
    if not cur.fetchone():
        await message.reply("You are not registered. Please register using /reg.")
        return
    await message.reply("Enter operation ID:")
    await DeleteOperation.id_operation.set()


# Удаление операции по ID
@dp.message_handler(state=DeleteOperation.id_operation)
async def delete_operation_id(message: types.Message, state: FSMContext):
    # Удаление операции из базы данных по ID
    pass  # Дополнительный код для удаления операции


# Запуск бота
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)