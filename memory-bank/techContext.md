# Tech Context

## Languages & Frameworks
- Python 3.12 (multi-service stack).
- Django 5.1 (admin site, ORM, management commands).
- Aiogram 3.4 (bot update handling, FSM, keyboards).
- Telethon 1.37 (parser / userbot).

## Dependencies & Tooling
- `requirements.txt` pins async stack (aiohttp, magic-filter), utility libs (`loguru`, `python-dotenv`), DB driver (`psycopg2-binary`), media handling (`pillow`).
- Dockerfile installs deps once; every service in docker-compose reuses the same image.
- Postgres 15 Alpine container seeded by `dump_file.sql` (if present) + `.env` credentials.
- Shared volume `media` surfaces attachments for both Django admin and bots.

## Configuration & Secrets
- `.env` required values: `BOT_TOKEN`, `ADMIN_ID`, `SECRET_KEY`; parser keys optional (`TG_PARSER_API_ID/HASH`).
- Database defaults: host `postgres_db`, db `freelance_db`, user `postgres`, password `qH6~*8tq&` (dev only).
- Flags: `DJANGO_PORT`, `PG_PORT`, optional `DEBUG`, `ALLOWED_HOSTS`.

## Execution Modes
- **Local dev**: `python manage.py migrate && python manage.py start_bot` etc. Use `pyenv`/`poetry` if desired.
- **Containers**: `docker-compose up --build` brings up main_bot, mailing_bot, parser, admin, postgres.
- **CI/CD hooks**: not defined yet; manual deploy expected.
