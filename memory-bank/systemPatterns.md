# System Patterns

## Architecture
- **Monorepo**: Django project (`bot_admin`, `core`) + aiogram bot (`bot/`) + Telethon parser (`tg_parser/`).
- **PostgreSQL** — single relational DB consumed via Django ORM. Async bot code interacts with ORM through `sync_to_async` connectors (`bot.components.connectors.postgres_connector`).
- **Service split**:
  - `main_bot`: handles updates, FSM flows, keyboards, referrals, subscriptions.
  - `mailing_bot`: background loop that polls DB for confirmed bids and push-notifies users (media groups supported).
  - `tg_parser`: Telethon client that mirrors Telegram channels, matches keywords, and emits bids automatically.
  - `django_admin`: RESTless admin interface for all entities + management commands (`start_bot`, `start_mailing`, `start_tg_parser`).

## Key Patterns
- **State orchestration**: aiogram `StatesGroup` factories define multi-step flows (user data, bid creation).
- **Customization layer**: `CustomTexts` + `CustomButtons` tables keep runtime copy of default strings; first access auto-seeds defaults → admins edit without redeploy.
- **Subject-matter targeting**: `Subscription.matters` + `Users.black_list` + `search_switch` toggles; mailing bot filters recipients before sending.
- **Media-safe broadcasts**: `MediaFiles` per bid, `Mailing` worker builds `MediaGroup`, falls back to text if no media.
- **Parser resilience**: Telethon flow tolerates missing API creds (stub mode) + FloodWait retry with exponential sleep; filtering avoids bot spam (`@...bot` regex).

## Operations
- Docker Compose orchestrates identical images with different entrypoints (all copy repo, install deps, run dedicated command).
- Shared `media` volume ensures both admin uploads and bots reuse same files.
- Env-driven behavior: parser auto-disables without `TG_PARSER_*`, referral/promo logic toggled via DB state, admin port is configurable via `DJANGO_PORT`.
