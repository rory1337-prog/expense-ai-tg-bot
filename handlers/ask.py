from aiogram import Router, F
from aiogram.types import Message

router = Router()


@router.message(F.text.startswith("/ask"))
async def ask_handler(message: Message):

    question = message.text.replace("/ask", "").strip()

    if not question:
        await message.answer("Ask a finance question.")
        return

    await message.answer(f"Question received: {question}")