from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
import psycopg2
import aiohttp


# Bot
bot = Bot(token="6767097413:AAHknm4fPLMbTzNA-lONT8pkTWcu3sGfko8")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# База данных
conn = psycopg2.connect(
    host="127.0.0.1",
    database="RGZ_RPP",
    user="Kashira",
    password="54691452",
    port=5432
)
cur = conn.cursor()

# States
class Registration(StatesGroup):
    login = State()

class AddOperation(StatesGroup):
    type_operation = State()
    sum_operation = State()
    date_operation = State()

class DeleteOperation(StatesGroup):
    id_operation = State()


@dp.message_handler(commands=["start"])
async def reg(message: types.Message):
    commands_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    commands_keyboard.add("/reg")
    await message.reply(f"Вас приветствует телеграм бот учета винансов Fynance_Cash_bot. \n"
                         f"Перед тем как начать пользоваться нашим ботом зарегистрируйтесь, используя команду \n"
                         f"/reg", reply_markup=commands_keyboard)


@dp.message_handler(commands=["reg"])
async def reg(message: types.Message):
    cur.execute("SELECT * FROM users WHERE chat_id = %s", (message.chat.id,))
    if cur.fetchone():
        await message.reply("Вы уже зарегистрированы.")
        commands_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        commands_keyboard.add("/start", "/reg", "/add_operation", "/operations", "/delete_operation")
        await message.reply(f"Добро пожаловать, вот список доступных вам команд:\n"
                            f"/start \n"
                            f"/reg \n"
                            f"/add_operation \n"
                            f"/operations \n"
                            f"/delete_operation \n", reply_markup=commands_keyboard)
        return
    await Registration.login.set()
    await message.reply("Введите логин:")

@dp.message_handler(state=Registration.login)
async def reg_login(message: types.Message, state: FSMContext):
    login = message.text
    cur.execute("INSERT INTO users (name, chat_id) VALUES (%s, %s)", (login, message.chat.id))
    conn.commit()
    await state.finish()
    await message.reply("Вы успешно зарегистрированы.")
    commands_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    commands_keyboard.add("/start", "/reg", "/add_operation", "/operations", "/delete_operation" )
    await message.reply(f"Добро пожаловать, вот список доступных вам команд:\n"
                        f"/start \n"
                        f"/reg \n"
                        f"/add_operation \n"
                        f"/operations \n"
                        f"/delete_operation \n", reply_markup=commands_keyboard)



@dp.message_handler(commands=["add_operation"])
async def add_operation(message: types.Message):
    cur.execute("SELECT * FROM users WHERE chat_id = %s", (message.chat.id,))
    if not cur.fetchone():
        await message.reply("Вы не зарегистрированы. Пожалуйста, зарегистрируйтесь с помощью команды /reg.")
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("РАСХОД", "ДОХОД")
    await message.reply(f"Выберите тип операции: \n"
                        "РАСХОД \n"
                        "ДОХОД \n", reply_markup=markup)
    await AddOperation.type_operation.set()

@dp.message_handler(state=AddOperation.type_operation)
async def add_operation_type(message: types.Message, state: FSMContext):
    type_operation = message.text
    await state.update_data(type_operation=type_operation)
    await message.reply("Введите сумму операции в рублях:")
    await AddOperation.next()

@dp.message_handler(state=AddOperation.sum_operation)
async def add_operation_sum(message: types.Message, state: FSMContext):
    sum_operation = int(message.text)
    await state.update_data(sum_operation=sum_operation)
    await message.reply("Введите дату операции (в формате YYYY-MM-DD):")
    await AddOperation.next()

@dp.message_handler(state=AddOperation.date_operation)
async def add_operation_date(message: types.Message, state: FSMContext):
    date_operation = message.text
    data = await state.get_data()
    type_operation = data["type_operation"]
    sum_operation = data["sum_operation"]
    cur.execute("INSERT INTO operations (date, sum, chat_id, type_operation) VALUES (%s, %s, %s, %s)",
               (date_operation, sum_operation, message.chat.id, type_operation))
    conn.commit()
    await state.finish()
    await message.reply("Операция добавлена.")


@dp.message_handler(commands=["operations"])
async def operations(message: types.Message):
    cur.execute("SELECT * FROM users WHERE chat_id = %s", (message.chat.id,))
    if not cur.fetchone():
        await message.reply("Вы не зарегистрированы. Пожалуйста, зарегистрируйтесь с помощью команды /reg.")
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("RUB", "EUR", "USD")
    await message.reply(f"Выберите валюту: \n"
                        "RUB\n" 
                        "EUR\n" 
                        "USD", reply_markup=markup)

@dp.message_handler(lambda message: message.text in ["RUB", "EUR", "USD"])
async def operations_currency(message: types.Message):
    currency = message.text
    cur.execute("SELECT * FROM operations WHERE chat_id = %s", (message.chat.id,))
    operations = cur.fetchall()
    for operation in operations:
        id, date, sum, chat_id, type_operation = operation
        if currency != "RUB":
            rate = await get_exchange_rate(currency)
            if rate is None:
                await message.reply("Ошибка получения курса валюты.")
                return
            new_sum = int(sum) / rate
            await message.reply(f"Операция по курсу {currency}: \n"
                                f"ID операции: {id} \n"
                                f"Дата операции: {date} \n"
                                f"Сумма: {new_sum} {currency} \n"
                                f"ID пользователя: {chat_id} \n"
                                f"Вид операции: {type_operation} \n")
        else:
            await message.reply(f"Операция по курсу RUB: \n"
                                f"ID операции: {id} \n"
                                f"Дата операции: {date} \n"
                                f"Сумма: {sum} RUB \n"
                                f"ID пользователя: {chat_id} \n"
                                f"Вид операции: {type_operation} \n")

async def get_exchange_rate(currency):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://195.58.54.159:8000/rate?currency={currency}") as response:
            if response.status == 200:
                data = await response.json()
                return data["rate"]
            elif response.status == 400:
                return None
            elif response.status == 500:
                return None
            else:
                return None

@dp.message_handler(commands=["delete_operation"])
async def delete_operation(message: types.Message):
    cur.execute("SELECT * FROM users WHERE chat_id = %s", (message.chat.id,))
    if not cur.fetchone():
        await message.reply("Вы не зарегистрированы. Пожалуйста, зарегистрируйтесь с помощью команды /reg.")
        return
    await message.reply("Введите идентификатор операции:")
    await DeleteOperation.id_operation.set()

@dp.message_handler(state=DeleteOperation.id_operation)
async def delete_operation_id(message: types.Message, state: FSMContext):
    id_operation = int(message.text)
    cur.execute("SELECT * FROM operations WHERE id = %s AND chat_id = %s", (id_operation, message.chat.id))
    if not cur.fetchone():
        await message.reply("Операция не найдена или не принадлежит вам.")
        return
    cur.execute("DELETE FROM operations WHERE id = %s AND chat_id = %s", (id_operation, message.chat.id))
    conn.commit()
    await state.finish()
    await message.reply("Операция удалена.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)