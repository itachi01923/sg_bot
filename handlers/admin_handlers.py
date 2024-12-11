from aiogram import Router, F, Bot
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

from database.repository import UserRepository
from filters.filters import IsAdmin
from keyboards.image_consent_btn import get_consent_btn

router = Router()


class FSMBroadcastForm(StatesGroup):
    send_text = State()
    send_image_consent = State()
    send_image = State()
    send_broadcast_consent = State()


@router.message(
    IsAdmin(),
    Command("broadcast")
)
async def process_start_broadcast(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(FSMBroadcastForm.send_text)
    await message.answer("Напишите сообщение для рассылки: ")


@router.message(
    IsAdmin(),
    StateFilter(FSMBroadcastForm.send_text)
)
async def process_send_test(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    await state.set_state(FSMBroadcastForm.send_image_consent)
    await message.answer("Хотите отправить изображение?", reply_markup=get_consent_btn())


@router.callback_query(
    IsAdmin(),
    StateFilter(FSMBroadcastForm.send_image_consent),
    F.data.in_(["yes", "no"])
)
async def process_consent_image(callback: CallbackQuery, state: FSMContext):
    await state.update_data(image_consent=callback.data)

    if callback.data == "yes":
        await callback.message.answer("Отправьте изображение: ")
        await state.set_state(FSMBroadcastForm.send_image)
    else:
        await callback.message.edit_text("Начать рассылку?", reply_markup=get_consent_btn())
        await state.set_state(FSMBroadcastForm.send_broadcast_consent)


@router.message(
    IsAdmin(),
    F.photo,
    StateFilter(FSMBroadcastForm.send_image),
)
async def process_get_image(message: Message, state: FSMContext):
    await state.update_data(image_id=message.photo[-1].file_id)

    await message.answer("Начать рассылку?", reply_markup=get_consent_btn())
    await state.set_state(FSMBroadcastForm.send_broadcast_consent)


@router.callback_query(
    IsAdmin(),
    StateFilter(FSMBroadcastForm.send_broadcast_consent),
    F.data.in_(["yes", "no"])
)
async def process_consent_image(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await state.update_data(broadcast_consent=callback.data)

    if callback.data == "no":
        await callback.message.answer("Отмена отправки рассылки.")
    else:
        data = await state.get_data()

        text: str = data.get("text")
        image_id: str | None = data.get("image_id")

        await callback.message.answer("Начинаю рассылку. Вот сообщение рассылки.")

        if image_id:
            await callback.message.answer_photo(image_id, caption=text)
        else:
            await callback.message.answer(text)

        users: list = await UserRepository.find_all()
        users_count_in_db: int = len(users)

        await callback.message.answer(f"Найдено пользователей {users_count_in_db}.")
        success_send: int = 0

        for user in users:
            try:
                if image_id:
                    await bot.send_photo(user.user_id, image_id, caption=text)
                else:
                    await bot.send_message(user.user_id, text)
                success_send += 1
            except Exception as e:
                print(e)

        await callback.message.answer(f"Рассылка отправлена {success_send} пользователям.")
