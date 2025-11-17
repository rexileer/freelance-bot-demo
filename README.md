# Freelance Bot — production-ready demo

> Telegram-экосистема «под ключ»: aiogram-бот для клиентов, Django-админка для команды, отдельный воркер для рассылок и Telethon-парсер, который превращает сообщения из каналов в структурированные заявки. Проект задуман как портфолио-кейс: его README и код можно показывать на собеседовании.

## Почему это интересно работодателю
- **Настоящая архитектура**: четыре Python-сервиса, общее хранилище PostgreSQL, асинхронные коннекторы и docker-compose оркестрация.
- **Готовые продуктовые фичи**: подписки по тематикам, пробный период, реферальная система, пользовательские тексты/кнопки, очередь заявок с медиа-файлами.
- **Бережное отношение к безопасности**: все токены только в `.env`, парсер умеет уходить в «заглушку», логика не зависит от внешних API.

## Архитектура на ладони

```
                    ┌──────────────┐
                    │ Django Admin │  gunicorn + ORM
                    └──────┬───────┘
                           │
                management │ commands (start_bot/start_mailing/start_tg_parser)
                           │
┌────────────┐  updates ┌──▼─────────┐  sync_to_async  ┌────────────┐
│ Telegram   │◀────────▶│ main_bot   │────────────────▶│ PostgreSQL │
└────────────┘          └──┬─────────┘                 └────┬───────┘
                           │                                │
                     sends │ bids                           │
                           │                                │
                    ┌──────▼──────┐                   reads │💾
                    │ mailing_bot │◀───────────────────────┘
                    └──────┬──────┘
                           │ confirmed bids
                    ┌──────▼──────┐  Telethon + keywords
                    │ tg_parser   │─────────────────────┐
                    └─────────────┘                     │
                           ▲                            │
                           └──────────┐   channels      │
                                      └─────────────────┘
```

| Компонент      | Назначение | Как запустить |
| -------------- | ---------- | ------------- |
| `main_bot`     | Aiogram 3, FSM-логика, клавиатуры, работа с БД через `sync_to_async`. | `python manage.py start_bot` или контейнер `main_bot`. |
| `mailing_bot`  | Работает в фоне, раз в 2 секунды проверяет подтверждённые заявки и шлёт медиагруппы подписчикам. | `python manage.py start_mailing`. |
| `tg_parser`    | Telethon-клиент (userbot). Подписан на каналы, ищет ключевые слова, создаёт `Bid`. Может работать в stub-режиме без API ключей. | `python manage.py start_tg_parser`. |
| `django_admin` | Панель управления (tariffs, users, bids, channels, custom texts/buttons, useful materials). | `python manage.py runserver` локально или `gunicorn` в docker-compose. |
| `postgres_db`  | Хранит все сущности (`Users`, `Subscription`, `Tariffs`, `Bid`, `MediaFiles`, `ReferralsTable`, `UsefulMaterials`, `Payments`). | Автоматически через docker-compose. |

## Основные возможности
- **Онбординг и подписки**: выбор тематик, покупка тарифа, пробная подписка на 3 дня, промокоды с % скидкой.
- **Реферальная система**: отслеживание количества приглашённых и начисление % от пополнений.
- **Управление категориями**: пользователь включает/выключает поиск по каждой тематике, ведёт личный blacklist.
- **Создание заявок**: вручную через бота (включая вложения) или автоматически из парсера; заявки проходят модерацию в админке.
- **Рассылка**: медиагруппы до 10 файлов, фильтрация по подпискам/чёрным спискам/переключателю `search_switch`.
- **Гибкие тексты/кнопки**: первое обращение к ключу создаёт запись в БД, дальше админ может поменять текст без деплоя.
- **Полезные материалы**: библиотека ссылок/файлов внутри бота.

## Технологический стек
- Python 3.12, aiogram 3.4, Django 5.1, Telethon 1.37.
- PostgreSQL 15 + `psycopg2-binary`.
- Асинхронные библиотеки: `aiohttp`, `aiofiles`, `loguru` для логов.
- Контейнеризация: Dockerfile + docker-compose (5 сервисов + общий `media` volume).

## Структура репозитория

| Путь | Содержимое |
| --- | --- |
| `bot/` | aiogram-handlers, FSM-фабрики, клавиатуры, коннекторы к ORM. |
| `bot_admin/` | Django проект (settings, urls, wsgi/asgi). |
| `core/` | Модели, админ, management-команды (`start_bot`, `start_mailing`, `start_tg_parser`). |
| `tg_parser/` | Telethon-парсер и его коннектор к БД. |
| `memory-bank/` | Project brief + контекст для следующих итераций. |
| `docker-compose.yaml` | Описание сервисов (main_bot, mailing_bot, tg_parser, django_admin, postgres_db). |
| `env.example` | Документированная .env-матрица. |

## Подготовка окружения
```bash
cp env.example .env
# Обязательные переменные
BOT_TOKEN=...          # токен @BotFather
ADMIN_ID=...           # ваш числовой Telegram ID
SECRET_KEY=...         # Django secret
```
*Parser можно временно отключить, оставив `TG_PARSER_API_ID`/`TG_PARSER_API_HASH` пустыми — `tg_parser` просто засыпает и пишет heartbeat.*

## Запуск в Docker
```bash
docker-compose up -d --build

# Первый запуск: миграции и суперпользователь
docker compose exec django_admin python manage.py migrate
docker compose exec django_admin python manage.py createsuperuser
```

> ⚠️ `docker-compose` описывает `entrypoint.sh` для `main_bot`, но файл в репозитории отсутствует. В проде предполагается скрипт, который выполняет `python manage.py start_bot && python manage.py migrate`. Для локальной работы можно либо:
> - добавить собственный `entrypoint.sh`,
> - либо запустить `docker compose exec main_bot python manage.py start_bot` вручную после поднятия контейнера.

> ℹ️ В репозитории лежит заглушка `dump_file.sql`. Замените её собственным дампом (или отредактируйте), если нужно заполнить базу на старте контейнера.

Админка будет доступна на `http://localhost:${DJANGO_PORT:-8000}/admin/`. Бот и воркеры используют общий том `media`, чтобы расшаривать вложения.

## Запуск без Docker
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export $(grep -v '^#' .env | xargs)  # или используйте direnv
python manage.py migrate
python manage.py createsuperuser

# параллельно в разных терминалах
python manage.py start_bot
python manage.py start_mailing
python manage.py start_tg_parser   # опционально
python manage.py runserver 0.0.0.0:8000
```

## Типичные команды оператора
```bash
# создать дамп (например, для локальной разработки)
python manage.py dumpdata core > dump.json

# обновить тексты/кнопки через админку
python manage.py shell  # можно писать скрипты на ORM
```

## Переменные окружения

| Переменная | Описание |
| ---------- | -------- |
| `BOT_TOKEN` | Токен Telegram-бота (обязательно). |
| `ADMIN_ID` | Telegram ID пользователя, которому бот отправит `/start` при запуске. |
| `SECRET_KEY` | Django secret key. |
| `TG_PARSER_API_ID/HASH` | Креды userbot'а (опционально; без них парсер уходит в ожидание). |
| `DJANGO_PORT` | Проброшенный порт админки (по умолчанию 8000). |
| `PG_PORT` | Порт PostgreSQL на хосте (по умолчанию 5432). |
| `PG_HOST/PG_NAME/PG_USER/PG_PASSWORD` | Внутренние настройки БД (по умолчанию `postgres_db`, `freelance_db`, `postgres`, `qH6~*8tq&`). |
| `DEBUG`, `ALLOWED_HOSTS` | Стандартные Django-переключатели (закомментированы в `.env.example`). |

## Ключевые модели
- `Users`: хранит баланс, статус пробной подписки, переключатель поиска и blacklist тематик.
- `SubjectMatters`: тематики + ключевые слова для парсера.
- `Tariffs`: цена + длительность подписки.
- `Subscription`: M2M с тематиками, указание тарифов/сроков.
- `Bid`: заявка с текстом, медиаконтентом, статусами `is_confirmed`/`is_sent`, датой рассылки.
- `MediaFiles`: путь к файлу, тип (`photo/video/document`), Telegram file_id.
- `ReferralsTable`: связь «кто привёл кого».
- `UsefulMaterials`, `CustomTexts`, `CustomButtons`, `Payments`, `Channels`.

## Поток данных «заявка → пользователь»
1. **Парсер или пользователь** создаёт `Bid`.
2. Модератор в админке подтверждает заявку (`is_confirmed=True`) и выбирает дату рассылки/канал.
3. `mailing_bot` вытаскивает неподтверждённые рассылки, собирает медиагруппу, фильтрует пользователей:
   - подписка содержит нужную тематику,
   - подписка ещё активна (`end_date >= now`),
   - пользователь не выключил поиск и не поместил тематику в blacklist.
4. Отправка в Telegram с обработкой ошибок и повторной попыткой.

## Логи и наблюдаемость
- `loguru` пишет читабельные сообщения о запуске бота, подключении к Telegram и ошибках отправки.
- При необходимости легко прокинуть `LOGURU_LEVEL` через `.env`, либо заменить `print` на structured logging (планируется).

## Ограничения и идеи для развития
- Добавить `entrypoint.sh`, healthchecks и CI (pytest + mypy).
- Подключить реальный эквайринг (сейчас пополнение баланса и платежи работают от имени администратора).
- Поднять мониторинг (Prometheus/Grafana, Sentry) и централизованное логирование.
- Заменить `time.sleep` в `mailing_bot` на планировщик (apscheduler / Celery beat).

## Лицензия
MIT.