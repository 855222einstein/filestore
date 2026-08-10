# My Telegram File-Store Bot

A file sharing & storage Telegram bot (Pyrogram + MongoDB) with a clone feature:
users can create their own copy of the bot with /clone <token>, running inside the
same process but with their own admin and their own storage channel.

## Features
- Store any file -> get a permanent deep-link (?start=<payload>)
- Batch links: many channel posts behind one link
- Optional force-subscribe gate
- Clone system (/clone, /deleteclone) with per-clone settings, auto-restart on boot
- Admin broadcast + stats
- Optional PROTECT_CONTENT (disable forwarding of delivered files)

## Setup
1. cp .env.example .env  and fill it in.
2. Create a private channel, add the bot as admin, set STORAGE_CHANNEL.
3. pip install -r requirements.txt
4. python -m bot.main

## Deploy
- Heroku / Render: uses Procfile (worker) + runtime.txt.
- Docker: docker build -t filestorebot . && docker run -d --env-file .env filestorebot

## License
MIT
