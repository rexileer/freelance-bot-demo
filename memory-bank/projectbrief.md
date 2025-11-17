# Project Brief – Freelance Bot Demo

## Mission
- Showcase a production-style Telegram ecosystem: customer acquisition bot, Django back office, automated mailings, and an optional parser that converts Telegram chatter into structured bids.
- Provide recruiters or hiring managers with tangible proof of backend + bot engineering skills (async Python, Django ORM, integrations, ops).

## Scope
- **Channels**: inbound bot (`aiogram 3`), Django admin (CRUD for tariffs, texts, bids), scheduled mailing worker, Telethon parser (stub-friendly).
- **Core flows**: subscription sales, promo codes, referral accounting, subject-matter targeting, bid ingestion (manual + parser), media-rich broadcasts.
- **Runtime**: containerized stack (Dockerfile + docker-compose) wired to PostgreSQL 15, shipping management commands for standalone execution.

## Out of Scope
- Payment acquiring integrations (mocked balance/promo flows only).
- Multi-tenant or multi-language productization.
- Advanced observability (basic logging only) and high availability.

## Success Criteria
- Fresh environment can be bootstrapped via `docker-compose` with only `.env` secrets.
- Recruiter can read README + Memory Bank to understand architecture without diving into code.
- Demo remains safe: no secrets committed, parser degrades gracefully when API keys absent.
