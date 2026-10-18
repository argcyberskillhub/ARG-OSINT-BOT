#!/usr/bin/env python3
# ============================================================
# ARGRecon PRO Telegram Bot
# Uses scanner.py as the shared scanning engine.
# ============================================================

import os
import logging

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from scanner import (
    telegram_help,
    telegram_ip_lookup,
    telegram_dns_lookup,
    telegram_whois_lookup,
    telegram_port_scan,
    telegram_subdomain_scan,
    telegram_passive_subdomain_scan,
    telegram_username_scan,
    telegram_email_scan,
)

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

if not BOT_TOKEN:
    try:
        from config import BOT_TOKEN as CONFIG_TOKEN
        BOT_TOKEN = CONFIG_TOKEN.strip()
    except Exception:
        pass


def argument(update: Update):
    if not update.message:
        return ""
    return " ".join(update.message.text.split()[1:]).strip()


async def safe_reply(update: Update, text: str):
    if update.message:
        # Telegram message limit is ~4096 chars.
        chunks = [text[i:i+3900] for i in range(0, len(text), 3900)]
        for chunk in chunks:
            await update.message.reply_text(
                chunk,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await safe_reply(
        update,
        "🛡 <b>ARGRecon PRO Online</b>\n\n" + telegram_help()
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await safe_reply(update, telegram_help())


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await safe_reply(
        update,
        "🟢 <b>ARGRecon PRO</b>\n"
        "━━━━━━━━━━━━━━━━\n"
        "Status: ONLINE\n"
        "Engine: DNS / WHOIS / IP / OSINT\n"
        "Mode: Educational / Authorized Use"
    )


async def require_arg(update: Update, name: str):
    value = argument(update)
    if not value:
        await safe_reply(update, f"❌ Usage: <b>{name}</b> &lt;value&gt;")
        return None
    return value


async def ip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    value = await require_arg(update, "/ip")
    if value:
        await safe_reply(update, telegram_ip_lookup(value))


async def dns_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    value = await require_arg(update, "/dns")
    if value:
        await safe_reply(update, telegram_dns_lookup(value))


async def whois_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    value = await require_arg(update, "/whois")
    if value:
        await safe_reply(update, telegram_whois_lookup(value))


async def ports_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    value = await require_arg(update, "/ports")
    if value:
        await safe_reply(update, telegram_port_scan(value))


async def subdomain_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    value = await require_arg(update, "/subdomain")
    if value:
        await safe_reply(update, telegram_subdomain_scan(value))


async def passive_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    value = await require_arg(update, "/passive")
    if value:
        await safe_reply(update, telegram_passive_subdomain_scan(value))


async def username_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    value = await require_arg(update, "/username")
    if value:
        await safe_reply(update, telegram_username_scan(value))


async def email_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    value = await require_arg(update, "/email")
    if value:
        await safe_reply(update, telegram_email_scan(value))


async def domain_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    value = await require_arg(update, "/domain")
    if not value:
        return

    text = (
        telegram_dns_lookup(value)
        + "\n\n"
        + telegram_whois_lookup(value)
        + "\n\n"
        + telegram_subdomain_scan(value)
    )
    await safe_reply(update, text)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logging.error(
        "Telegram error: %s",
        context.error,
        exc_info=context.error,
    )


def build_application():
    if not BOT_TOKEN:
        raise RuntimeError(
            "BOT_TOKEN not found. Put it in config.py or set BOT_TOKEN environment variable."
        )

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("status", status_command))

    app.add_handler(CommandHandler("ip", ip_command))
    app.add_handler(CommandHandler("dns", dns_command))
    app.add_handler(CommandHandler("whois", whois_command))
    app.add_handler(CommandHandler("ports", ports_command))
    app.add_handler(CommandHandler("subdomain", subdomain_command))
    app.add_handler(CommandHandler("passive", passive_command))
    app.add_handler(CommandHandler("username", username_command))
    app.add_handler(CommandHandler("email", email_command))
    app.add_handler(CommandHandler("domain", domain_command))

    app.add_error_handler(error_handler)
    return app


if __name__ == "__main__":
    print("ARGRecon PRO Telegram Bot starting...")
    application = build_application()
    application.run_polling(drop_pending_updates=True)
