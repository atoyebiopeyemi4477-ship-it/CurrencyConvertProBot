# Currency Convert Pro Bot

A free Telegram bot that converts between currencies using live ECB rates
(via [frankfurter.app](https://frankfurter.app) — no API key required).

## Commands
- `/start` — welcome message
- `/help` — usage instructions
- `/convert 100 USD EUR` — convert 100 USD to EUR
- Or just type naturally: `100 USD to EUR`

## Local setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set your bot token as an environment variable:
   ```bash
   export BOT_TOKEN=your_token_here
   ```
3. Run it:
   ```bash
   python main.py
   ```

## Deploy on Railway

1. Push this project to a GitHub repo.
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub repo.
3. Select your repo.
4. In Railway, go to your service → **Variables** → add:
   - `BOT_TOKEN` = the token you got from @BotFather
5. Railway will detect the `Procfile` and run `python main.py` as a worker.
6. Once deployed, message your bot on Telegram — it should respond immediately.

## Notes
- This bot uses long polling (`run_polling`), so no webhook or public URL is needed.
- Make sure the Railway service type is a **worker**, not a web service (it doesn't listen on a port).
