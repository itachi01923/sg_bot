from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_consent_btn() -> InlineKeyboardMarkup:
    button_1 = InlineKeyboardButton(
        text="Да",
        callback_data="yes"
    )
    button_2 = InlineKeyboardButton(
        text="Нет",
        callback_data="no"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_1, button_2]]
    )

    return keyboard
