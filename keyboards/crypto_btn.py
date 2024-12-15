from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from database.repository import CryptoRepository
from database.schemas import CryptoResponse


async def get_crypto_btn(key: str = "", is_active: bool = True) -> InlineKeyboardMarkup:
    crypto_list: list[CryptoResponse] = await CryptoRepository.find_all(is_active=is_active)

    buttons: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text=crypto.title, callback_data=f"{key}_{crypto.symbol}")]
        for crypto in crypto_list
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)
