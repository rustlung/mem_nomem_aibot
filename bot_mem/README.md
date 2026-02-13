# bot_mem — бот с памятью

Бот с кратковременным контекстом в SQLite (`data/memory.db`).

- Память по `user_id`: последние N пар (user + assistant), N = `HISTORY_PAIRS_LIMIT` (по умолчанию 5).
- Команды: /start, /help, /reset (очистить свой контекст), /context (кнопка «Показать контекст»).
- Запуск из корня проекта: `python bot_mem/main.py`.
