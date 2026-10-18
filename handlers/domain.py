from telegram import Update
from telegram.ext import ContextTypes

from WebInfo import (
    telegram_domain_scan,
    telegram_ip_lookup,
    telegram_dns_lookup,
    telegram_whois_lookup,
    telegram_port_scan,
    telegram_subdomain_scan
)


async def domain_input(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_input = update.message.text.strip()

    mode = context.user_data.get("mode")

    if not mode:
        await update.message.reply_text(
            "⚠️ Please select a scan option first using /start"
        )
        return


    await update.message.reply_text(
        "🔍 Scanning started...\nPlease wait."
    )


    try:

        if mode == "domain":

            result = telegram_domain_scan(user_input)


        elif mode == "ip":

            result = telegram_ip_lookup(user_input)


        elif mode == "dns":

            result = telegram_dns_lookup(user_input)


        elif mode == "whois":

            result = telegram_whois_lookup(user_input)


        elif mode == "port":

            result = telegram_port_scan(user_input)


        elif mode == "subdomain":

            result = telegram_subdomain_scan(user_input)


        else:

            result = "❌ Unknown scan type"



        if not result:
            result = "No information found."


        await update.message.reply_text(
    f"🛰 <b>ARG OSINT REPORT</b>\n\n<pre>{result[:3500]}</pre>",
    parse_mode="HTML"
)


    except Exception as e:

        await update.message.reply_text(
            f"❌ Error:\n{e}"
        )


    # clear mode after scan
    context.user_data.clear()