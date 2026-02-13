"""Entry point for stateless Telegram bot (no memory)."""
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher

from common.config import BOT_NOMEM_TOKEN, validate_bot_nomem_config
from common.logging_setup import setup_logging
from bot_nomem.handlers import router


def main() -> None:
    log = setup_logging("bot_nomem")
    validate_bot_nomem_config()
    bot = Bot(token=BOT_NOMEM_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    async def run() -> None:
        try:
            log.info("Старт бота bot_nomem (stateless)")
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
