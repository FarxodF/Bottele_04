from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

bot = Bot(token='KEY')
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


inline_kb = InlineKeyboardMarkup(row_width=2)
inline_btn_calories = InlineKeyboardButton('Рассчитать норму калорий', callback_data='calories')
inline_btn_formulas = InlineKeyboardButton('Формулы расчёта', callback_data='formulas')
inline_kb.add(inline_btn_calories, inline_btn_formulas)


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    main_menu_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    main_menu_kb.add(types.KeyboardButton('Рассчитать'))
    main_menu_kb.add(types.KeyboardButton('Информация'))
    main_menu_kb.add(types.KeyboardButton('Купить'))
    await message.reply("Добро пожаловать! Выберите опцию:", reply_markup=main_menu_kb)


@dp.message_handler(text='Рассчитать')
async def main_menu(message: types.Message):
    await message.reply("Выберите опцию:", reply_markup=inline_kb)


@dp.callback_query_handler(text='formulas')
async def get_formulas(call: types.CallbackQuery):
    formula_text = (
        "Формула Миффлина-Сан Жеора:\n"
        "Для мужчин: 10 \\вес + 6.25 \\рост - 5 \\возраст + 5 \n"
        "Для женщин: 10 \\вес + 6.25 \\рост - 5 \\возраст - 161 ")
    await call.message.reply(formula_text)


@dp.callback_query_handler(text='calories')
async def set_age(call: types.CallbackQuery):
    await call.message.reply("Введите свой возраст:")
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.reply("Введите свой рост:")
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    await state.update_data(growth=message.text)
    await message.reply("Введите свой вес:")
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def send_calories(message: types.Message, state: FSMContext):
    await state.update_data(weight=message.text)
    data = await state.get_data()

    age = int(data['age'])
    growth = int(data['growth'])
    weight = int(data['weight'])

    calories = 10 * weight + 6.25 * growth - 5 * age - 161

    await message.reply(f"Ваша норма калорий: {calories} ккал в день.")
    await state.finish()


product_kb = InlineKeyboardMarkup(row_width=2)
product_kb.add(InlineKeyboardButton('Product1', callback_data='product_buying'),
               InlineKeyboardButton('Product2', callback_data='product_buying'),
               InlineKeyboardButton('Product3', callback_data='product_buying'),
               InlineKeyboardButton('Product4', callback_data='product_buying')
               )


@dp.message_handler(text='Купить')
async def get_buying_list(message: types.Message):
    products = [("Product1", "описание 1", 100),
                ("Product2", "описание 2", 200),
                ("Product3", "описание 3", 300),
                ("Product4", "описание 4", 400)
                ]

    for name, desc, price in products:
        await message.reply(f"Название: {name} | Описание: {desc} | Цена: {price}")
        await message.reply("Выберите продукт для покупки:", reply_markup=product_kb)


@dp.callback_query_handler(text='product_buying')
async def send_confirm_message(call: types.CallbackQuery):
    await call.message.reply("Вы успешно приобрели продукт!")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
