"""OpenAI client wrapper: one model, timeouts and errors handled, minimal tokens."""
import logging

from openai import OpenAI
from openai import APITimeoutError, APIConnectionError, APIStatusError

from common.config import OPENAI_API_KEY, OPENAI_MODEL

logger = logging.getLogger(__name__)

# Default timeout in seconds
DEFAULT_TIMEOUT = 60.0
# Max chars per message content before sending to OpenAI (minimize tokens)
MAX_CHARS = 4000

# Single short system prompt for both bots
SYSTEM_PROMPT = "You are a helpful assistant. Reply concisely."


def _truncate(text: str, max_len: int = MAX_CHARS) -> str:
    """Trim message content to max_len; suffix if truncated."""
    if len(text) <= max_len:
        return text
    return text[: max_len - 20].rstrip() + "\n… (обрезано)"


def get_client() -> OpenAI:
    """Return configured OpenAI client."""
    return OpenAI(api_key=OPENAI_API_KEY or None)


def chat_completion(
    user_message: str,
    system_prompt: str | None = None,
    model: str | None = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> tuple[bool, str]:
    """
    Send user message to OpenAI and return (success, text).
    On error: (False, user-friendly message); errors are logged.
    """
    prompt = system_prompt or SYSTEM_PROMPT
    content = _truncate(user_message)
    client = get_client()
    model = model or OPENAI_MODEL or "gpt-4"
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": content},
            ],
            timeout=timeout,
        )
        text = (
            response.choices[0].message.content
            if response.choices and response.choices[0].message
            else ""
        )
        return True, text.strip() or "Нет ответа от модели."
    except APITimeoutError as e:
        logger.error("OpenAI timeout: %s", e)
        return False, "Сервис ответил слишком долго. Попробуйте позже."
    except APIConnectionError as e:
        logger.error("OpenAI connection error: %s", e)
        return False, "Ошибка соединения с сервисом. Проверьте интернет и попробуйте снова."
    except APIStatusError as e:
        logger.error("OpenAI API error (status): %s", e)
        return False, "Временная ошибка сервиса. Попробуйте позже."
    except Exception as e:
        logger.exception("OpenAI unexpected error: %s", e)
        return False, "Произошла ошибка при запросе. Попробуйте позже."


def _truncate_messages(messages: list[dict[str, str]]) -> list[dict[str, str]]:
    """Ensure each message content is at most MAX_CHARS (for API)."""
    return [{"role": m["role"], "content": _truncate(m["content"])} for m in messages]


def chat_completion_with_messages(
    messages: list[dict[str, str]],
    model: str | None = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> tuple[bool, str]:
    """
    Send pre-built messages (e.g. system + history + user) to OpenAI.
    messages: list of {"role": "system"|"user"|"assistant", "content": "..."}
    Content is truncated to MAX_CHARS per message. Returns (success, assistant_reply_or_error_message).
    """
    trimmed = _truncate_messages(messages)
    client = get_client()
    model = model or OPENAI_MODEL or "gpt-4"
    try:
        response = client.chat.completions.create(
            model=model,
            messages=trimmed,
            timeout=timeout,
        )
        text = (
            response.choices[0].message.content
            if response.choices and response.choices[0].message
            else ""
        )
        return True, text.strip() or "Нет ответа от модели."
    except APITimeoutError as e:
        logger.error("OpenAI timeout: %s", e)
        return False, "Сервис ответил слишком долго. Попробуйте позже."
    except APIConnectionError as e:
        logger.error("OpenAI connection error: %s", e)
        return False, "Ошибка соединения с сервисом. Проверьте интернет и попробуйте снова."
    except APIStatusError as e:
        logger.error("OpenAI API error (status): %s", e)
        return False, "Временная ошибка сервиса. Попробуйте позже."
    except Exception as e:
        logger.exception("OpenAI unexpected error: %s", e)
        return False, "Произошла ошибка при запросе. Попробуйте позже."
