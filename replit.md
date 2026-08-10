# SHUKLAMUSIC (Stranger Music Bot)

A Telegram Music Player bot that plays music in Telegram voice chats. Built with Python using Pyrogram and Py-Tgcalls.

## Setup

This is a background worker bot — it has no web frontend.

### Required Environment Variables
Set these in the Secrets/Environment Variables panel:
- `API_ID` — Telegram API ID
- `API_HASH` — Telegram API Hash
- `BOT_TOKEN` — Telegram Bot Token
- `MONGO_DB_URI` — MongoDB connection URI
- `OWNER_ID` — Telegram user ID of the bot owner
- `LOGGER_ID` — Telegram group/channel ID for logging
- `STRING_SESSION` — Pyrogram session string for the userbot assistant

### Optional
- `STRING_SESSION2` through `STRING_SESSION7` — additional session strings
- `HEROKU_APP_NAME`, `HEROKU_API_KEY` — for Heroku deployments
- `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET` — for Spotify support

## Running

```bash
python3 -m SHUKLAMUSIC
```

## User Preferences
