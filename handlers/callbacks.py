from telegram import Update
from telegram.ext import ContextTypes


async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    # DOMAIN
    if query.data == "domain":

        context.user_data["mode"] = "domain"

        await query.edit_message_text(
            "🌐 DOMAIN SCAN\n\n"
            "Send a domain.\n\n"
            "Example:\n"
            "google.com"
        )

    # IP
    elif query.data == "ip":

        context.user_data["mode"] = "ip"

        await query.edit_message_text(
            "🌍 IP LOOKUP\n\n"
            "Send an IP Address.\n\n"
            "Example:\n"
            "8.8.8.8"
        )

    # DNS
    elif query.data == "dns":

        context.user_data["mode"] = "dns"

        await query.edit_message_text(
            "🌐 DNS LOOKUP\n\n"
            "Send a domain.\n\n"
            "Example:\n"
            "google.com"
        )

    # WHOIS
    elif query.data == "whois":

        context.user_data["mode"] = "whois"

        await query.edit_message_text(
            "📜 WHOIS LOOKUP\n\n"
            "Send a domain.\n\n"
            "Example:\n"
            "google.com"
        )

    # PORT
    elif query.data == "port":

        context.user_data["mode"] = "port"

        await query.edit_message_text(
            "🚪 PORT SCAN\n\n"
            "Send Target IP.\n\n"
            "Example:\n"
            "1.1.1.1"
        )

    # SUBDOMAIN
    elif query.data == "subdomain":

        context.user_data["mode"] = "subdomain"

        await query.edit_message_text(
            "🔍 SUBDOMAIN SCAN\n\n"
            "Send a domain.\n\n"
            "Example:\n"
            "google.com"
        )

    elif query.data == "email":

        await query.edit_message_text(
            "📧 Email Scan\n\nComing Soon..."
        )

    elif query.data == "username":

        await query.edit_message_text(
            "👤 Username Scan\n\nComing Soon..."
        )

    elif query.data == "settings":

        await query.edit_message_text(
            "⚙ Settings\n\nComing Soon..."
        )

    elif query.data == "help":

        await query.edit_message_text(
            "ℹ Help\n\nComing Soon..."
        )