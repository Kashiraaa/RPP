# Импортируем необходимые библиотеки
import asyncio
import asyncpg
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
import requests

# Устанавливаем токен для бота
API_TOKEN_BOT = 'YOUR_API_TOKEN'
bot = Bot(token=API_TOKEN_BOT)
dp = Dispatcher(bot, storage=MemoryStorage())

# URL для обращения к сервисам управления и получения данных о валютах
currency_manager_url = 'http://127.0.0.1:5001'
data_manager_url = 'http://127.0.0.1:5002'

# Создание состояний для формы и конвертации валюты
class Form(StatesGroup):
    currency_name = State()
    currency_rate = State()
    delete_currency_name = State()
    update_currency_name = State()
    update_currency_rate = State()

class ConvertStep(StatesGroup):
    currency_name = State()
    currency_amount = State()

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    # Проверяем является ли пользователь администратором
    user_id = message.from_user.id
    if await is_admin(user_id):
        # Создаем клавиатуру для администратора
        commands_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        commands_keyboard.add("/start", "/manage_currency", "/get_currencies", "/convert")

        # Отправляем сообщение с доступными командами для администратора
        await message.reply(f"Вот команды, которые администратор может использовать: \n"
                            f"/start \n"
                            f"/manage_currency \n"
                            f"/get_currencies \n"
                            f"/convert \n", reply_markup=commands_keyboard)
    else:
        # Создаем клавиатуру для обычного пользователя
        commands_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        commands_keyboard.add("/start", "/get_currencies", "/convert")
        # Отправляем сообщение с доступными командами для пользователя
        await message.reply(f"Вот команды, которые пользователь может использовать: \n"
                            f"/start \n"
                            f"/get_currencies \n"
                            f"/convert \n", reply_markup=commands_keyboard)

# Функция проверки является ли пользователь администратором
async def is_admin(user_id):
    con = await asyncpg.connect(database='microservice_bot', user='Kashira', password='54691452', host='127.0.0.1',port=5432)
    try:
        query = "SELECT 1 FROM admins WHERE chat_id = $1"
        result = await con.fetchrow(query, str(user_id))
        if result:
            return True
        else:
            return False
    finally:
        await con.close()

# Обработчик команды /manage_currency
@dp.message_handler(commands=['manage_currency'])
async def manage_currency_command(message: types.Message):
    # Получаем id пользователя
    user_id = message.from_user.id
    # Проверяем является ли пользователь администратором
    if await is_admin(user_id):
        # Создаем клавиатуру с возможными действиями
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
        keyboard.add(types.KeyboardButton("Добавить валюту"), types.KeyboardButton("Удалить валюту"), types.KeyboardButton("Изменить курс валюты"))
        # Отправляем сообщение с выбором действия
        await message.reply("Выберите вариант, что вам нужно сделать с валютой:", reply_markup=keyboard)
    else:
        await message.reply("У вас недостаточно прав для выполнения данной команды ")

# Обработчик действия "Добавить валюту"
@dp.message_handler(lambda message: message.text == "Добавить валюту")
async def add_currency_step1(message: types.Message):
    await message.reply("Введите название валюты:")
    await Form.currency_name.set()

# Обработчик ввода названия валюты для добавления
@dp.message_handler(state=Form.currency_name)
async def add_currency_step2(message: types.Message, state: FSMContext):
    currency_name = message.text
    data = {'currency_name': currency_name}
    response = requests.post(f'{currency_manager_url}/load', json=data)
    if response.status_code == 400:
        await message.reply("Данная валюта уже есть в базе данных.")
        await state.finish()
        return
    await state.update_data(currency_name=currency_name)
    await message.reply("Введите курс валюты к рублю:")
    await Form.currency_rate.set()

# Обработчик ввода курса валюты для добавления
@dp.message_handler(state=Form.currency_rate)
async def add_currency_step3(message: types.Message, state: FSMContext):
    currency_rate = float(message.text)
    user_data = await state.get_data()
    currency_name = user_data.get('currency_name')
    data = {'currency_name': currency_name, 'currency_rate': currency_rate}
    response = requests.post(f'{currency_manager_url}/load', json=data)
    await message.reply(f"Валюта {currency_name} добавлена с курсом {currency_rate}")
    await state.finish()

# Обработчик действия "Удалить валюту"
@dp.message_handler(lambda message: message.text == "Удалить валюту")
async def delete_currency_step1(message: types.Message):
    await message.reply("Введите название валюты, для удаления из базы:")
    await Form.delete_currency_name.set()

# Обработчик ввода названия валюты для удаления
@dp.message_handler(state=Form.delete_currency_name)
async def delete_currency_step2(message: types.Message, state: FSMContext):
    currency_name = message.text
    data = {'currency_name': currency_name}
    response = requests.post(f'{currency_manager_url}/delete', json=data)
    await message.reply(f"Валюта {currency_name} удалена.")
    await state.finish()

# Обработчик действия "Изменить курс валюты"
@dp.message_handler(lambda message: message.text == "Изменить курс валюты")
async def update_currency_rate_step1(message: types.Message):
    await message.reply("Введите название валюты, ждя изменения курса:")
    await Form.update_currency_name.set()

# Обработчик ввода названия валюты для изменения курса
@dp.message_handler(state=Form.update_currency_name)
async def update_currency_rate_step2(message: types.Message, state: FSMContext):
    currency_name = message.text
    await state.update_data(currency_name=currency_name)
    await message.reply("Введите новый курс валюты к рублю:")
    await Form.update_currency_rate.set()

# Обработчик ввода нового курса валюты для изменения
@dp.message_handler(state=Form.update_currency_rate)
async def update_currency_rate_step3(message: types.Message, state: FSMContext):
    new_currency_rate = float(message.text)
    user_data = await state.get_data()
    currency_name = user_data.get('currency_name')
    data = {'currency_name': currency_name, 'rate': new_currency_rate}
    response = requests.post(f'{currency_manager_url}/update_currency', json=data)
    await message.reply(f"Курс валюты {currency_name} изменен на {new_currency_rate}")
    await state.finish()

# Обработчик команды /get_currencies
@dp.message_handler(commands=['get_currencies'])
async def get_currencies(message: types.Message):
    response = requests.get(f'{data_manager_url}/currencies')
    currencies = response.json()['currencies']
    await message.reply("Сохраненные валюты с курсом к рублю:")
    for currency in currencies:
        await message.reply(f"{currency['currency_name']}: {currency['rate']}")

# Обработчик команды /convert
@dp.message_handler(commands=['convert'])
async def convert_currency(message: types.Message):
    await message.reply("Введите название валюты для конвертации:")
    await ConvertStep.currency_name.set()

# Обработчик ввода названия и суммы для конвертации валюты
@dp.message_handler(state=ConvertStep.currency_name)
async def convert_currency_step1(message: types.Message,state: FSMContext):
    currency_name = message.text
    await state.update_data(currency_name=currency_name)
    await message.reply("Введите сумму для конвертации валюты в рубли:")
    await ConvertStep.currency_amount.set()

# Обработчик ввода суммы и выполнение конвертации
@dp.message_handler(state=ConvertStep.currency_amount)
async def convert_currency_step2(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    currency_name = user_data.get('currency_name')
    amount = float(message.text)
    data = {'currency_name': currency_name, 'amount': amount}
    response = requests.get(f'{data_manager_url}/convert', params=data)
    converted_amount = response.json()['converted_amount']
    await message.reply(f"Сумма {amount} {currency_name} равна {converted_amount} рублям.")
    await state.finish()

# Запуск бота
if __name__ == '__main__':
    async def main():
        await dp.start_polling()
    asyncio.run(main())