from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_exchange_btn() -> InlineKeyboardMarkup:
    big_button_1 = InlineKeyboardButton(
        text='Покупаю крипту⬅️',
        callback_data='buy'
    )

    big_button_2 = InlineKeyboardButton(
        text='Продаю крипту➡️',
        callback_data='sell'
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[big_button_1], [big_button_2]]
    )
    return keyboard


def get_exchange_crypto_list_btn() -> InlineKeyboardMarkup:
    button_1 = InlineKeyboardButton(
        text='Bitcoin',
        callback_data='btc'
    )
    button_2 = InlineKeyboardButton(
        text='Litecoin',
        callback_data='ltc'
    )
    button_3 = InlineKeyboardButton(
        text='USDT(trc20)',
        callback_data='usdt'
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1], [button_2], [button_3]]
    )

    return keyboard


def get_price_type_method_btn() -> InlineKeyboardMarkup:
    button_1 = InlineKeyboardButton(
        text='В RUB (например 1000)',
        callback_data='rub_type'
    )
    button_2 = InlineKeyboardButton(
        text='В USDT (например 10.25)',
        callback_data='usdt_type'
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1], [button_2]]
    )

    return keyboard
