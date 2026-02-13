"""Handlers for stateless bot: /start, /help, and any text -> OpenAI."""
import logging

from aiogram import Router, F
from aiogram.types import Message

from common.openai_client import chat_completion, SYSTEM_PROMPT

router = Router(name="nomem")
logger = logging.getLogger(__name__)

HELP_TEXT = """Команды:
/start — приветствие
/help — список команд

Любой другой текст — отправляется в GPT, ответ приходит сюда."""


@router.message(F.text, F.text == "/start")
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Привет! Я бот без памяти: каждый запрос обрабатывается отдельно.\n\n"
        + HELP_TEXT
    )


@router.message(F.text, F.text == "/help")
async def cmd_help(message: Message) -> None:
    await message.answer(HELP_TEXT)


@router.message(F.text)
async def on_text(message: Message) -> None:
    if not message.text or not message.text.strip():
        return
    user_id = message.from_user.id if message.from_user else 0
    text_in = message.text.strip()
    logger.info("Получено сообщение от user_id=%s", user_id)
    success, text = chat_completion(text_in, system_prompt=SYSTEM_PROMPT)
    if success:
        logger.info("Ответ отправлен user_id=%s", user_id)
        await message.answer(text)
    else:
        logger.error("Ошибка OpenAI для user_id=%s", user_id)
        await message.answer(text)
