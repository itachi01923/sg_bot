from aiogram.filters import BaseFilter
from aiogram.types import Message


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
