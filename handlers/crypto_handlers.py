from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

from database.repository import CryptoRepository
from database.schemas import CryptoResponse, CryptoBase
from filters.filters import IsAdmin, CheckPrice
from keyboards.crypto_btn import get_crypto_btn
from keyboards.image_consent_btn import get_consent_btn
from lexicon.lexicon import LEXICON_HELP
from services.services import CMCHTTPClient
from utils.number import round_number

router = Router()

cmc_client = CMCHTTPClient()


class FSMCryptoAddForm(StatesGroup):
    send_symbol = State()
    send_title = State()
    send_percent = State()
    send_consent = State()


class FSMCryptoUpdateForm(StatesGroup):
    send_percent = State()


@router.message(
    IsAdmin(),
    Command("help"),
)
async def help_handler(message: Message):
    await message.answer(LEXICON_HELP)


@router.message(
    IsAdmin(),
    Command("course")
)
async def send_course_info(message: Message, state: FSMContext):
    await state.clear()

    all_crypto: list[CryptoResponse] = await CryptoRepository.find_all()
    text: str = ""

    for crypto_in in all_crypto:
        price: int = round_number(await cmc_client.get_currency(crypto_in.symbol), 0)
        text += f"{crypto_in.symbol} - {crypto_in.title} - {crypto_in.percent}% - {price} (+{round_number(price + ((price * crypto_in.percent) / 100), 0)}, -{round_number(price - ((price * crypto_in.percent) / 100), 0)})\n\n"

    await message.answer(text)


@router.message(
    IsAdmin(),
    Command("crypto_add")
)
async def start_process_add_crypto(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(FSMCryptoAddForm.send_symbol)
    await message.answer("Отправьте символ криптовалюты: ")


@router.message(
    IsAdmin(),
    StateFilter(FSMCryptoAddForm.send_symbol)
)
async def get_crypto_symbol(message: Message, state: FSMContext):
    symbol: str = message.text.upper()
    res: str | None = await cmc_client.check_crypto(symbol)

    if res:
        await state.update_data(symbol=symbol)
        await state.set_state(FSMCryptoAddForm.send_title)
        await message.answer("Отправьте название крипты: ")
    else:
        await message.answer("Криптовалюты под таким именем не существует.\nОтправьте название заново: ")


@router.message(
    IsAdmin(),
    StateFilter(FSMCryptoAddForm.send_title),
)
async def get_crypto_symbol(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(FSMCryptoAddForm.send_percent)
    await message.answer("Отправьте проценты: ")


@router.message(
    IsAdmin(),
    StateFilter(FSMCryptoAddForm.send_percent),
    CheckPrice()
)
async def get_crypto_symbol(message: Message, state: FSMContext, price: float):
    percent: int = int(price)

    await state.update_data(percent=percent)
    await state.set_state(FSMCryptoAddForm.send_consent)

    data = await state.get_data()

    await message.answer("Добавить новую крипту?\n"
                         f"Символ - {data.get("symbol")}\n"
                         f"Имя - {data.get("title")}\n"
                         f"Процент - {data.get("percent")}%\n",
                         reply_markup=get_consent_btn())


@router.callback_query(
    IsAdmin(),
    StateFilter(FSMCryptoAddForm.send_consent),
    F.data.in_(["yes", "no"])
)
async def get_consent(callback: CallbackQuery, state: FSMContext):
    if callback.data == "no":
        await callback.message.answer("Отмена.")
    else:
        data = await state.get_data()
        crypto: CryptoBase = CryptoBase(
            symbol=data.get("symbol"),
            title=data.get("title"),
            percent=data.get("percent"),
            is_active=True
        )

        new_crypto: CryptoResponse = await CryptoRepository.insert_data(crypto)

        await callback.message.answer("Криптовалюта была успешна добавлена.")

    await state.clear()


@router.message(
    IsAdmin(),
    Command("crypto_delete")
)
async def get_btn_list_for_delete(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Выберите криптовалюты для удаления: ", reply_markup=await get_crypto_btn(key="delete"))


@router.callback_query(
    IsAdmin(),
    F.data.startswith("delete_")
)
async def delete_crypro(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    symbol = callback.data.split("_", 1)[-1]
    res: bool = await CryptoRepository.delete_data(symbol=symbol)

    if res:
        await callback.message.edit_text(f"{symbol} был удален!")
    else:
        await callback.message.edit_text(f"{symbol}  не был удален!")


@router.message(
    IsAdmin(),
    Command("crypto_edit")
)
async def get_btn_list_for_delete(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Выберите криптовалюты для изменения процента: ",
                         reply_markup=await get_crypto_btn(key="edit"))
    await state.set_state(FSMCryptoUpdateForm.send_percent)


@router.callback_query(
    IsAdmin(),
    F.data.startswith("edit_"),
    StateFilter(FSMCryptoUpdateForm.send_percent)
)
async def delete_crypro(callback: CallbackQuery, state: FSMContext):
    symbol = callback.data.split("_", 1)[-1]

    await state.update_data(symbol=symbol)
    await state.set_state(FSMCryptoUpdateForm.send_percent)
    await callback.message.edit_text("Отправьте новый процент: ")


@router.message(
    IsAdmin(),
    StateFilter(FSMCryptoUpdateForm.send_percent),
    CheckPrice()
)
async def get_crypto_symbol(message: Message, state: FSMContext, price: float):
    percent: int = int(price)
    data = await state.get_data()

    await CryptoRepository.update_data(data.get("symbol"), percent)
    await message.answer("Успешно было изменено.")
