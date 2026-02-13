"""Entry point for Telegram bot with memory (SQLite)."""
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher

from common.config import BOT_MEM_TOKEN, validate_bot_mem_config
from common.logging_setup import setup_logging
from common.db import init_db
from bot_mem.handlers import router


def main() -> None:
    log = setup_logging("bot_mem")
    validate_bot_mem_config()
    try:
        init_db()
        log.info("БД инициализирована")
    except Exception as e:
        log.exception("Ошибка инициализации БД: %s", e)
        sys.exit(1)

    bot = Bot(token=BOT_MEM_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    async def run() -> None:
        try:
            log.info("Старт бота bot_mem (с памятью)")
            await dp.start_polling(bot)
        except Exception as e:
            log.exception("Bot crashed: %s", e)
            raise
        finally:
            await bot.session.close()

    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        log.info("Остановка по Ctrl+C")
    except Exception as e:
        log.exception("Fatal: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
