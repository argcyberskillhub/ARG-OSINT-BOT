from telegram import Update
from telegram.ext import ContextTypes
from keyboards.main_menu import main_menu


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = """
🛰 <b>ARG OSINT BOT</b>

Welcome!

Choose an option below.

⚡ Fast
🔒 Secure
🌐 Public OSINT
"""

    await update.message.reply_text(
        text,
        parse_mode="HTML",
        reply_markup=main_menu()
    )