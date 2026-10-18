from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu():

    keyboard = [

        [InlineKeyboardButton("🌐 Domain Scan", callback_data="domain")],

        [InlineKeyboardButton("🌍 IP Lookup", callback_data="ip")],

        [InlineKeyboardButton("🌐 DNS Lookup", callback_data="dns")],

        [InlineKeyboardButton("📜 WHOIS Lookup", callback_data="whois")],

        [InlineKeyboardButton("🚪 Port Scan", callback_data="port")],

        [InlineKeyboardButton("🔍 Subdomain Scan", callback_data="subdomain")],

        [InlineKeyboardButton("📧 Email Scan", callback_data="email")],

        [InlineKeyboardButton("👤 Username Scan", callback_data="username")],

        [
            InlineKeyboardButton("⚙ Settings", callback_data="settings"),
            InlineKeyboardButton("ℹ Help", callback_data="help")
        ]

    ]

    return InlineKeyboardMarkup(keyboard)