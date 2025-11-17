# Progress Snapshot

## Implemented
- Aiogram bot with FSM handlers for onboarding, subscription selection, referrals, useful materials, bid submission.
- Django admin + models for all core entities; management commands to launch bot, mailing worker, parser.
- Mailing worker delivering media-rich bids to subscribers respecting search switches and blacklists.
- Telethon parser with keyword-based routing and Telegram author lookup + FloodWait handling.
- Docker Compose topology (main bot, mailing bot, parser, admin, Postgres) + shared media volume.

## In Flight
- README rewrite with detailed technical pitch (current task).

## Known Gaps / Risks
- `entrypoint.sh` referenced in docker-compose but absent in repo — either needs creation or README must highlight custom entry command.
- No automated tests or CI.
- Payments are placeholders; README should warn recruiters.
