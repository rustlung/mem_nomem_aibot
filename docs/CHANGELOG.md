# Changelog

## [Unreleased]

### Added
- Проект с двумя ботами (aiogram 3+, OpenAI), общий venv и .env.
- Общие модули: `common/config.py`, `common/logging_setup.py`, `common/openai_client.py`, `common/db.py`, `common/memory_repo.py`.
- **bot_nomem**: stateless-бот — /start, /help, любой текст → OpenAI (system + user) → ответ; обработка таймаутов и ошибок API.
- **bot_mem**: бот с памятью в SQLite (`data/memory.db`): контекст на user_id, последние N пар (user/assistant), N из `HISTORY_PAIRS_LIMIT` (дефолт 5). Команды: /start, /help, /reset, /context (InlineKeyboard «Показать контекст»). Ответы через `chat_completion_with_messages` с историей; все исключения логируются, пользователю — короткое сообщение без stacktrace.
