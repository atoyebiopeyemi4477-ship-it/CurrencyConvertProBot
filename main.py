import logging
import os
import re

import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_URL = "https://api.frankfurter.app/latest"

# Matches things like: "100 USD to EUR", "100USD EUR", "10 usd in ngn"
CONVERT_PATTERN = re.compile(
    r"^\s*([\d,.]+)\s*([a-zA-Z]{3})\s*(?:to|in|->|=)?\s*([a-zA-Z]{3})\s*$"
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "👋 Welcome to Currency Convert Pro!\n\n"
        "Send me a message like:\n"
        "`100 USD to EUR`\n"
        "`50 GBP NGN`\n\n"
        "Or use: /convert <amount> <from> <to>\n"
        "Example: /convert 100 USD EUR",
        parse_mode="Markdown",
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Usage:\n"
        "/convert 100 USD EUR\n"
        "or just type: 100 USD to EUR\n\n"
        "Rates provided by the European Central Bank via frankfurter.app"
    )


def get_conversion(amount: float, from_currency: str, to_currency: str):
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()
    params = {"amount": amount, "from": from_currency, "to": to_currency}
    response = requests.get(API_URL, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    rate_result = data["rates"].get(to_currency)
    return rate_result


async def convert_and_reply(update: Update, amount_str: str, from_cur: str, to_cur: str):
    try:
        amount = float(amount_str.replace(",", ""))
    except ValueError:
        await update.message.reply_text("⚠️ Couldn't read that amount. Try: 100 USD to EUR")
        return

    try:
        result = get_conversion(amount, from_cur, to_cur)
    except requests.RequestException:
        await update.message.reply_text("⚠️ Currency service is unavailable right now. Try again shortly.")
        return
    except (KeyError, ValueError):
        result = None

    if result is None:
        await update.message.reply_text(
            f"⚠️ Couldn't convert {from_cur.upper()} to {to_cur.upper()}. "
            "Check the currency codes (e.g. USD, EUR, GBP, NGN) and try again."
        )
        return

    await update.message.reply_text(
        f"💱 {amount:,.2f} {from_cur.upper()} = {result:,.2f} {to_cur.upper()}"
    )


async def convert_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    args = context.args
    if len(args) != 3:
        await update.message.reply_text("Usage: /convert 100 USD EUR")
        return
    amount_str, from_cur, to_cur = args
    await convert_and_reply(update, amount_str, from_cur, to_cur)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    match = CONVERT_PATTERN.match(text)
    if not match:
        await update.message.reply_text(
            "I didn't understand that. Try: `100 USD to EUR`",
            parse_mode="Markdown",
        )
        return
    amount_str, from_cur, to_cur = match.groups()
    await convert_and_reply(update, amount_str, from_cur, to_cur)


def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN environment variable is not set.")

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("convert", convert_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("Bot starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
