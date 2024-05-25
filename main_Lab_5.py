import asyncio
import asyncpg
from aiogram import Bot, Dispatcher, \
   types
from aiogram.contrib.fsm_storage.memory import \
   MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, \
   State


API_TOKEN_BOT = '7020693852:AAEWBJM_7GRjWa_AAc2CZuiyffvwlK2Do9M'
bot = Bot(token=API_TOKEN_BOT)
dp = Dispatcher(bot, storage=MemoryStorage())


class Form(StatesGroup):
   currency_name = State()
   currency_rate = State()
   delete_currency_name = State()
   update_currency_name = State()
   update_currency_rate = State()


class ConvertStep(StatesGroup):
   currency_name = State()
   currency_amount = State()

@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
   user_id = message.from_user.id
   if await is_admin(user_id):
       commands_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
       commands_keyboard.add("/start", "/manage_currency", "/get_currencies", "/convert")

       await message.reply(f"Вот команды, которые администратор может использовать: \n"
                           f"/start \n"
                           f"/manage_currency \n"
                           f"/get_currencies \n"
                           f"/convert \n", reply_markup=commands_keyboard)
   else:
       commands_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
       commands_keyboard.add("/start", "/get_currencies", "/convert")
       await message.reply(f"Вот команды, которые пользователь может использовать: \n"
                           f"/start \n"
                           f"/get_currencies \n"
                           f"/convert \n", reply_markup=commands_keyboard)

async def is_admin(user_id):
   con = await asyncpg.connect(database='bot_database', user='Kashira', password='54691452', host='127.0.0.1',port=5432)
   try:
       query = "SELECT 1 FROM admins WHERE chat_id = $1"
       result = await con.fetchrow(query, str(user_id))
       if result:
           return True
       else:
           return False
   finally:
       await con.close()


@dp.message_handler(commands=['manage_currency'])
async def manage_currency_command(message: types.Message):
   user_id = message.from_user.id
   if await is_admin(user_id):
       keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
       keyboard.add(types.KeyboardButton("Добавить валюту"), types.KeyboardButton("Удалить валюту"), types.KeyboardButton("Изменить курс валюты"))
       await message.reply("Выберите вариант, что вам нужно сделать с валютой:", reply_markup=keyboard)
   else:
       await message.reply("У вас недостаточно прав для выполнения данной команды ")



@dp.message_handler(lambda message: message.text == "Добавить валюту")
async def add_currency_step1(message: types.Message):
   await message.reply("Введите название валюты:")
   await Form.currency_name.set()


@dp.message_handler(state=Form.currency_name)
async def add_currency_step2(message: types.Message, state: FSMContext):
   currency_name = message.text
   if await is_currency_exists(currency_name):
       await message.reply("Данная валюта уже есть в базе данных.")
       await state.finish()
       return
   await state.update_data(currency_name=currency_name)
   await message.reply("Введите курс валюты к рублю:")
   await Form.currency_rate.set()

@dp.message_handler(state=Form.currency_rate)
async def add_currency_step3(message: types.Message, state: FSMContext):
   currency_rate = float(message.text)
   user_data = await state.get_data()
   currency_name = user_data.get('currency_name')
   await save_currency_to_db(currency_name, currency_rate)
   await message.reply(f"Валюта {currency_name} добавлена с курсом {currency_rate}")
   await state.finish()

async def is_currency_exists(currency_name):
   con = await asyncpg.connect(database='bot_database', user='Kashira', password='54691452', host='127.0.0.1', port=5432)
   try:
       query = "SELECT currency_name FROM currencies WHERE currency_name = $1"
       result = await con.fetch(query, currency_name)
       return bool(result)
   finally:
       await con.close()


async def save_currency_to_db(currency_name, currency_rate):
   con = await asyncpg.connect(database='bot_database', user='Kashira', password='54691452', host='127.0.0.1', port=5432)
   try:
       query = "INSERT INTO currencies (currency_name, rate) VALUES ($1, $2)"
       await con.execute(query, currency_name, currency_rate)
   finally:
       await con.close()



@dp.message_handler(lambda message: message.text == "Удалить валюту")
async def delete_currency_step1(
       message: types.Message):
   await message.reply("Введите название валюты, для удаления из базы:")
   await Form.delete_currency_name.set()



@dp.message_handler(state=Form.delete_currency_name)
async def delete_currency_step2(message: types.Message, state: FSMContext):
   currency_name = message.text
   await delete_currency_from_db(currency_name)
   await message.reply(f"Валюта {currency_name} удалена.")
   await state.finish()



async def delete_currency_from_db(currency_name):
   con = await asyncpg.connect(database='bot_database', user='Kashira', password='54691452', host='127.0.0.1', port=5432)
   try:
       query = "DELETE FROM currencies WHERE currency_name = $1"
       await con.execute(query, currency_name)
   finally:
       await con.close()

@dp.message_handler(lambda message: message.text == "Изменить курс валюты")
async def update_currency_rate_step1(message: types.Message):
   await message.reply("Введите название валюты, ждя изменения курса:")
   await Form.update_currency_name.set()


@dp.message_handler(state=Form.update_currency_name)
async def update_currency_rate_step2(message: types.Message, state: FSMContext):
   currency_name = message.text
   await state.update_data(currency_name=currency_name)
   await message.reply("Введите новый курс валюты к рублю:")
   await Form.update_currency_rate.set()



@dp.message_handler(state=Form.update_currency_rate)
async def update_currency_rate_step3(message: types.Message, state: FSMContext):
   new_currency_rate = float(message.text)
   user_data = await state.get_data()
   currency_name = user_data.get('currency_name')
   await update_currency_rate_in_db(currency_name, new_currency_rate)
   await message.reply(f"Курс валюты {currency_name} изменен на {new_currency_rate}")
   await state.finish()



async def update_currency_rate_in_db(currency_name, new_currency_rate):
   con = await asyncpg.connect(database='bot_database', user='Kashira', password='54691452', host='127.0.0.1',port=5432)
   try:
       query = "UPDATE currencies SET rate = $1 WHERE currency_name = $2"
       await con.execute(query, new_currency_rate, currency_name)
   finally:
       await con.close()



@dp.message_handler(commands=['get_currencies'])
async def get_currencies(message: types.Message):
   con = await asyncpg.connect(database='bot_database', user='Kashira', password='54691452', host='127.0.0.1', port=5432)
   try:
       query = "SELECT currency_name, rate FROM currencies"
       currencies = await con.fetch(query)
       if not currencies:
           await message.reply("Валюты в базе данных отсутсвуют")
       else:
           response = "Сохраненные валюты с курсом к рублю:\n"
           for currency in currencies:
               response += f"{currency['currency_name']}: {currency['rate']}\n"
           await message.reply(response)
   finally:
       await con.close()



@dp.message_handler(commands=['convert'])
async def convert_currency(message: types.Message):
   await message.reply("Введите название валюты для конвертации:")
   await ConvertStep.currency_name.set()



@dp.message_handler(state=ConvertStep.currency_name)
async def convert_currency_step1(message: types.Message,state: FSMContext):
   currency_name = message.text
   await state.update_data(currency_name=currency_name)
   await message.reply("Введите сумму для конвертации валюты в рубли:")
   await ConvertStep.currency_amount.set()



@dp.message_handler(state=ConvertStep.currency_amount)
async def convert_currency_step2(message: types.Message, state: FSMContext):
   user_data = await state.get_data()
   currency_name = user_data.get('currency_name')
   try:
       amount = float(message.text)
       rate = await get_currency_rate(currency_name)

       if rate is not None:
           rate_float = float(rate)
           converted_amount = amount * rate_float
           await message.reply(f"Сумма {amount} {currency_name} равна {converted_amount} рублям.")
       else:
           await message.reply(f"Ошибка при конвертации. Попробуйте снова.")
   except ValueError:
       await message.reply("Формат должен состоять из чисел. Введите ЧИСЛОВОЕ значение.")
   await state.finish()


async def get_currency_rate(currency_name):
   con = await asyncpg.connect(database='bot_database', user='Kashira', password='54691452', host='127.0.0.1',port=5432)
   try:
       query = "SELECT rate FROM currencies WHERE currency_name = $1"
       rate = await con.fetchval(query, currency_name)
       return rate
   finally:
       await con.close()

if __name__ == '__main__':
   async def main():
       await dp.start_polling()
   asyncio.run(main())
