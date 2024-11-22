from aiogram import Bot
from aiogram.types import BotCommand
from aiogram.types import (KeyboardButton, ReplyKeyboardMarkup)

from lexicon.lexicon import LEXICON_COMMANDS, LEXICON_MENU


# Функция для настройки кнопки Menu бота
async def set_main_menu(bot: Bot):
    main_menu_commands = [BotCommand(
        command=command,
        description=description
    ) for command,
    description in LEXICON_COMMANDS.items()]

    await bot.set_my_commands(main_menu_commands)


def menu_btn() -> ReplyKeyboardMarkup:
    button_1 = KeyboardButton(text=LEXICON_MENU.get("buy"))
    button_2 = KeyboardButton(text=LEXICON_MENU.get("sell"))
    button_3 = KeyboardButton(text=LEXICON_MENU.get("support"))

    # Создаем объект клавиатуры, добавляя в него кнопки
    keyboard = ReplyKeyboardMarkup(keyboard=[[button_1, button_2], [button_3]], resize_keyboard=True)

    return keyboard
