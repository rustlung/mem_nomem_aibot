"""Handlers for bot with memory: /start, /help, /reset, /context (inline button), text -> OpenAI + save."""
import logging

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from common.openai_client import chat_completion_with_messages, SYSTEM_PROMPT
from common.memory_repo import add_message, get_context, clear_user

router = Router(name="mem")
logger = logging.getLogger(__name__)

# Telegram message length limit
TELEGRAM_MAX_LEN = 4096


HELP_TEXT = """Команды:
/start — приветствие
/help — список команд
/reset — очистить историю диалога (только у вас)
/context — кнопка «Показать контекст»: просмотр сохранённого диалога

Любой другой текст — ответ с учётом истории, ответ сохраняется в память."""


CALLBACK_SHOW_CONTEXT = "show_context"


def _build_messages(user_id: int, new_user_text: str) -> list[dict[str, str]]:
    """[system, ...last 2*N messages from DB..., new user message]. No extra metadata."""
    out = [{"role": "system", "content": SYSTEM_PROMPT}]
    history = get_context(user_id)
    for m in history:
        out.append({"role": m["role"], "content": m["content"]})
    out.append({"role": "user", "content": new_user_text})
    return out


def _format_context_for_display(history: list[dict]) -> str:
    """Format as 'User: ...\n\nAssistant: ...'."""
    lines = []
    role_labels = {"user": "User", "assistant": "Assistant"}
    for m in history:
        label = role_labels.get(m["role"], m["role"])
        lines.append(f"{label}: {m['content']}")
    return "\n\n".join(lines) if lines else ""


def _chunk_text(text: str, max_len: int = TELEGRAM_MAX_LEN - 100) -> list[str]:
    """Split text into chunks not exceeding max_len. Prefer split at \n\n."""
    if len(text) <= max_len:
        return [text] if text else []
    chunks = []
    remainder = text
    while remainder:
        if len(remainder) <= max_len:
            chunks.append(remainder)
            break
        block = remainder[:max_len]
        last_break = block.rfind("\n\n")
        if last_break > max_len // 2:
            chunks.append(remainder[: last_break + 2].rstrip())
            remainder = remainder[last_break + 2 :].lstrip()
        else:
            chunks.append(block)
            remainder = remainder[max_len:]
    return chunks


@router.message(F.text, F.text == "/start")
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Привет! Я бот с памятью: помню последние сообщения в диалоге.\n\n"
        + HELP_TEXT
    )


@router.message(F.text, F.text == "/help")
async def cmd_help(message: Message) -> None:
    await message.answer(HELP_TEXT)


@router.message(F.text, F.text == "/reset")
async def cmd_reset(message: Message) -> None:
    user_id = message.from_user.id if message.from_user else 0
    try:
        clear_user(user_id)
        logger.info("Контекст очищен для user_id=%s", user_id)
        await message.answer("История диалога очищена.")
    except Exception:
        logger.exception("Ошибка при сбросе контекста для user_id=%s", user_id)
        await message.answer("Не удалось очистить историю. Попробуйте позже.")


@router.message(F.text, F.text == "/context")
async def cmd_context(message: Message) -> None:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Показать контекст", callback_data=CALLBACK_SHOW_CONTEXT)]
    ])
    await message.answer("Нажмите кнопку, чтобы увидеть текущий контекст диалога:", reply_markup=keyboard)


@router.callback_query(F.data == CALLBACK_SHOW_CONTEXT)
async def on_show_context(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id if callback.from_user else 0
    try:
        history = get_context(user_id)
        if not history:
            await callback.message.answer("Контекст пуст. Напишите что-нибудь, чтобы начать диалог.")
            await callback.answer()
            return
        text = _format_context_for_display(history)
        if len(text) > TELEGRAM_MAX_LEN:
            chunks = _chunk_text(text)
            if len(chunks) > 5:
                # Too many chunks: show last part only
                tail = "\n\n".join(chunks[-2:]) if len(chunks) >= 2 else chunks[-1]
                if len(tail) > TELEGRAM_MAX_LEN - 80:
                    tail = tail[-(TELEGRAM_MAX_LEN - 80) :]
                await callback.message.answer("Контекст длинный, показана последняя часть.\n\n" + tail)
            else:
                for chunk in chunks:
                    await callback.message.answer(chunk)
        else:
            await callback.message.answer(text)
        logger.info("Контекст показан user_id=%s", user_id)
    except Exception as e:
        logger.exception("Ошибка при чтении БД для показа контекста: %s", e)
        await callback.message.answer("Не удалось загрузить контекст. Попробуйте позже.")
    await callback.answer()


@router.message(F.text)
async def on_text(message: Message) -> None:
    if not message.text or not message.text.strip():
        return
    user_id = message.from_user.id if message.from_user else 0
    text_in = message.text.strip()
    logger.info("Получено сообщение от user_id=%s", user_id)
    try:
        messages = _build_messages(user_id, text_in)
        success, reply = chat_completion_with_messages(messages)
        if success:
            add_message(user_id, "user", text_in)
            add_message(user_id, "assistant", reply)
            logger.info("Запись в БД и ответ отправлен user_id=%s", user_id)
            await message.answer(reply)
        else:
            logger.error("Ошибка OpenAI для user_id=%s", user_id)
            await message.answer(reply)
    except Exception as e:
        logger.exception("Ошибка при обработке сообщения (БД или OpenAI): %s", e)
        await message.answer("Произошла ошибка. Попробуйте позже.")
