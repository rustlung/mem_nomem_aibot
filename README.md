# Mem / NoMem AI Bot

Два Telegram-бота на aiogram 3+ и OpenAI (одна модель для обоих).

- **bot_nomem** — бот без памяти (stateless): каждый запрос обрабатывается отдельно.
- **bot_mem** — бот с памятью: контекст в SQLite (`data/memory.db`), последние N пар сообщений на пользователя.

## Требования

- Python 3.10+
- Один виртуальное окружение и один `.env` в корне проекта.
- SQLite — из стандартной библиотеки Python (отдельно не ставится).

## Установка

1. Перейдите в корень проекта:

   ```bash
   cd mem_nomem_aibot
   ```

2. Создайте виртуальное окружение и активируйте его:

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

   (На Linux/macOS: `source venv/bin/activate`.)

3. Установите зависимости:

   ```bash
   pip install -r requirements.txt
   ```

4. Настройте окружение:

   ```bash
   copy .env.example .env
   ```

   Отредактируйте `.env`: укажите `BOT_NOMEM_TOKEN`, `BOT_MEM_TOKEN`, `OPENAI_API_KEY`. По желанию: `OPENAI_MODEL` (по умолчанию `gpt-4`), `HISTORY_PAIRS_LIMIT` для bot_mem (по умолчанию 5).

## Запуск обоих ботов (две консоли)

В корне проекта с активированным venv запустите **два процесса в двух консолях**.

**Консоль 1 — бот без памяти:**

```bash
python bot_nomem/main.py
```

**Консоль 2 — бот с памятью:**

```bash
python bot_mem/main.py
```

- В первой консоли: логи `[INFO] bot_nomem: ...`, бот отвечает на сообщения без истории.
- Во второй: логи `[INFO] bot_mem: ...`, при первом запуске создаётся `data/` и `data/memory.db`, бот хранит контекст и команды /reset, /context.

## Структура проекта

```
root/
  data/                 (создаётся автоматически, memory.db)
  requirements.txt
  .env.example
  README.md
  common/
    config.py
    logging_setup.py
    openai_client.py
    db.py
    memory_repo.py
  bot_nomem/
    main.py
    handlers.py
  bot_mem/
    main.py
    handlers.py
```

## Логирование и ошибки

- Единый формат логов: `[INFO] bot_nomem: ...`, `[ERROR] bot_mem: ...`.
- Логи отражают поток: старт, получение сообщения, запрос к OpenAI, запись в БД, ответы, ошибки.
- Ошибки OpenAI и БД: пользователю — короткое вежливое сообщение, без stacktrace; детали — в консоль.
