from datetime import datetime, timedelta

from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (CallbackQuery, Message)

from keyboards.exchange_btn import get_exchange_crypto_list_btn, get_price_type_method_btn, get_back_btn
from keyboards.main_menu import menu_btn
from lexicon.lexicon import LEXICON, LEXICON_MENU
from services.services import CMCHTTPClient
from pathlib import Path
from aiogram.types import FSInputFile

router = Router()

current_path = Path().resolve()
image_path: str = str(current_path / "images/logo.jpg")

# Создаем "базу данных" пользователей
user_dict: dict[int, datetime] = {}
last_used = {}

# Время задержки для повторного использования команды (в минутах)
COOLDOWN = 0

cmc_client = CMCHTTPClient(
    base_url="https://pro-api.coinmarketcap.com",
)


class FSMFillForm(StatesGroup):
    select_operation = State()  # Состояние ожидания выбора действия
    select_crypto = State()  # Состояние ожидания выбора криптовалюты
    select_price_method = State()  # Состояние ожидания выбора криптовалюты
    fill_price = State()  # Состояние ожидания ввода цены


# Start

@router.message(
    CommandStart(),
    lambda message: message.chat.type == 'private',
)
async def process_start_command(message: Message, state: FSMContext):
    """
    Start bot by command /start.
    Send welcome message and set menu buttons.

    :param message:
    :param state:
    :return:
    """
    image = FSInputFile(image_path)

    await message.answer_photo(photo=image, caption=LEXICON["/start"], reply_markup=menu_btn())
    await state.clear()


# Select buy/sell

@router.message(
    F.text.in_([LEXICON_MENU.get("buy"), LEXICON_MENU.get("sell")]),
    lambda message: message.chat.type == 'private',
)
async def process_method_sent(message: Message, state: FSMContext):
    """
    Хендлер срабатывает при нажатии кнопок купить или продать.
    Текст на который он срабатывает, берется из лексикона.

    В машину состояния записывается операция покупки/продажи.
    И после устанавливает машин состояния на выбор криптовалюты.
    И отправляет текст с кнопками выбора криптовалюты.

    :param message:
    :param state:
    :return:
    """
    await state.clear()
    await state.set_state(FSMFillForm.select_operation)

    if message.text == LEXICON_MENU.get("buy"):
        await state.update_data(operation="buy")
        text = "Выберите криптовалюту для покупки:"
    else:
        await state.update_data(operation="sell")
        text = "Выберите криптовалюту для продажи:"

    await state.set_state(FSMFillForm.select_crypto)

    await message.answer(
        text=text,
        reply_markup=get_exchange_crypto_list_btn()
    )


# Select Crypto

@router.callback_query(
    StateFilter(FSMFillForm.select_crypto),
    F.data.in_(["usdt", "ltc", "btc"]),
    lambda message: message.message.chat.type == 'private'
)
async def process_crypto_sent(callback: CallbackQuery, state: FSMContext):
    """
    Устанавливает выбранную криптовалюту в машину состояний.

    Если operation == buy, то отправляет кнопку с выбором метода оплаты
    и ставит машину состояние на ожидание выбора метода оплаты,
    а если operation == sell, то отправляет текст и ставит машину состояния на ожидания ввода суммы.

    :param callback:
    :param state:
    :return:
    """
    await state.update_data(crypto=callback.data)
    data = await state.get_data()

    if data["operation"] == "buy":
        await callback.message.edit_text(
            text="Выберете способ указания суммы",
            reply_markup=get_price_type_method_btn()
        )

        await state.set_state(FSMFillForm.select_price_method)
    else:
        await callback.message.edit_text(
            text=f"Укажите количество продаваемой криптовалюты {data.get("crypto").upper()}:",
            reply_markup=get_back_btn()
        )

        await state.set_state(FSMFillForm.fill_price)


@router.message(
    StateFilter(FSMFillForm.select_crypto),
    lambda message: message.chat.type == 'private',
)
async def warning_not_crypto(message: Message):
    """
    Срабатывает при не правильном выборе криптовалюты.

    :param message:
    :return:
    """
    await message.answer(
        text='Пожалуйста, пользуйтесь кнопками при выборе криптовалюты\n\n'
             'Если вы хотите прервать - отправьте команду /start',
        reply_markup=get_exchange_crypto_list_btn()
    )


# Select pay

@router.callback_query(
    StateFilter(FSMFillForm.select_price_method),
    F.data.in_(["usdt_type", "rub_type"]),
    lambda message: message.message.chat.type == 'private'
)
async def process_price_type_method_sent(callback: CallbackQuery, state: FSMContext):
    await state.update_data(price_method=callback.data)

    if callback.data == "rub_type":
        text: str = "Укажите сумму в рублях: "
    else:
        text: str = "Укажите сумму в крипте: "

    await callback.message.edit_text(
        text=text,
        reply_markup=get_back_btn()
    )
    await state.set_state(FSMFillForm.fill_price)


@router.message(
    StateFilter(FSMFillForm.select_crypto),
    lambda message: message.chat.type == 'private'
)
async def warning_not_price_type(message: Message):
    await message.answer(
        text='Пожалуйста, пользуйтесь кнопками при выборе метода оплаты\n\n'
             'Если вы хотите прервать - отправьте команду /start',
        reply_markup=get_price_type_method_btn()
    )


@router.message(
    StateFilter(FSMFillForm.fill_price),
    lambda x: x.text.isdigit() and 0 <= float(x.text) <= 100_000,
    lambda message: message.chat.type == 'private'
)
async def process_price_sent(message: Message, state: FSMContext, bot: Bot):
    user_id = message.from_user.id
    now = datetime.now()

    # Проверка времени последнего использования команды
    if user_id in last_used:
        elapsed_time = now - last_used[user_id]
        if elapsed_time < timedelta(minutes=COOLDOWN):
            remaining_time = (timedelta(minutes=COOLDOWN) -
                              elapsed_time).seconds
            await message.reply(
                f"Вы сможете использовать эту команду снова через {remaining_time // 60} минут(ы) и {remaining_time % 60} секунд.")
            await state.clear()

            return

    await state.update_data(price=message.text)

    data = await state.get_data()
    image = FSInputFile(image_path)
    crypto: str = data.get("crypto").upper()
    price_by_unit: float = float(await cmc_client.get_currency(crypto))
    count_and_price: float = float(data.get("price"))

    if data.get("method") == "buy":
        price_method: str = data.get("price_method")

        price_by_unit += 7

        if price_method == "rub_type":
            payment = count_and_price
            crypto_count = float(payment) / price_by_unit
        else:
            crypto_count = count_and_price
            payment = crypto_count * price_by_unit

        text: str = LEXICON["buy_answer"].format(
            crypto_count=crypto_count,
            crypto=crypto,
            price_by_unit=price_by_unit,
            payment=payment
        )
    else:
        payment = count_and_price
        price_by_unit -= 7
        get_price = price_by_unit * payment

        text: str = LEXICON["sell_answer"].format(get_price=get_price, payment=payment, crypto=crypto)

    await message.answer_photo(photo=image, caption=text)

    price_method: str = data.get("price_method")

    text = f"""ВНИМАНИЕ ВНИМАНИЕ!!! Новый запрос!!\n
Пользователь: <a href="tg://user?id={message.from_user.id}">{message.from_user.id} : {message.from_user.first_name} {message.from_user.last_name}</a>
Хочет: {"купить" if data.get("method") == "buy" else "продать"}
Крипта: {crypto}
Метод: {price_method}
Курс: {price_by_unit}
Сумма: {data.get("price")}
"""

    await bot.send_message(str(-1002431701698), text)
    await state.clear()
    last_used[user_id] = now


@router.message(
    StateFilter(FSMFillForm.fill_price),
    lambda message: message.chat.type == 'private'
)
async def warning_not_price(message: Message):
    await message.answer(
        text='Сумма должна быть целым числом от 0 до 10_000\n\n'
             'Попробуйте еще раз\n\nЕсли вы хотите прервать '
             '- отправьте команду /start'
    )


# Back

@router.callback_query(
    StateFilter(FSMFillForm.select_price_method),
    F.data.in_(["back"]),
    lambda message: message.message.chat.type == 'private'
)
async def process_back_to_select_crypto(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.set_state(FSMFillForm.select_operation)

    if data["operation"] == "buy":
        text: str = "Выберите криптовалюту для покупки:"
    else:
        text: str = "Выберите криптовалюту для продажи:"

    await state.set_state(FSMFillForm.select_crypto)

    await callback.message.edit_text(
        text=text,
        reply_markup=get_exchange_crypto_list_btn()
    )


@router.callback_query(
    StateFilter(FSMFillForm.fill_price),
    F.data.in_(["back"]),
    lambda message: message.message.chat.type == 'private'
)
async def process_back_to_select_price_method(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.set_state(FSMFillForm.select_operation)

    if data["operation"] == "buy":
        await callback.message.edit_text(
            text="Выберете способ указания суммы",
            reply_markup=get_price_type_method_btn()
        )

        await state.set_state(FSMFillForm.select_price_method)
    else:
        await callback.message.edit_text(
            text="Выберите криптовалюту для продажи:",
            reply_markup=get_exchange_crypto_list_btn()
        )

        await state.set_state(FSMFillForm.select_crypto)
