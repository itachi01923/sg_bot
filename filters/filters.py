from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from config.config import settings


class CheckPrice(BaseFilter):
    async def __call__(self, message: Message) -> bool | dict[str, float]:
        text: str = message.text.replace(",", ".").strip()
        if text.count(".") > 1:
            return False

        try:
            number: float = float(text)
        except ValueError:
            return False

        if number <= 0:
            return False

        return {"price": number}


class IsAdmin(BaseFilter):
    def __init__(self):
        self.admin_id = settings.ADMIN_ID

    async def __call__(self, event: Message | CallbackQuery) -> bool:
        return event.from_user.id == self.admin_id
        # and event.message.chat.id == -1002431701698)
