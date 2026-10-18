#!/usr/bin/env python3
# ============================================================
# ARGRecon PRO - Advanced Web / OSINT Scanner
# ARG Cyber Skill Hub
#
# Educational / authorized security research only.
# ============================================================

import os
import re
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote

import requests
import whois
import dns.resolver
from colorama import Fore, init

init(autoreset=True)

APP_NAME = "ARGRecon PRO"
VERSION = "2.0"
TIMEOUT = 8

SUBDOMAINS = [
    "www","mail","ftp","api","dev","test","blog","admin","portal",
    "vpn","remote","shop","store","app","mobile","m","staging","stage",
    "beta","demo","support","docs","help","status","cdn","static",
    "assets","images","img","media","ns1","ns2","dns","smtp","pop",
    "imap","webmail","login","auth","secure","dashboard","panel","git",
    "gitlab","devops","internal","api2","api-v1","api-v2","uat","qa",
    "preview","old","new","cloud","files","download","upload"
]

COMMON_PORTS = [
    21,22,23,25,53,80,110,111,135,139,143,443,445,587,993,995,
    1433,1521,2049,2375,3000,3306,3389,5000,5432,5900,6379,
    8000,8080,8443,8888,9200,27017
]

USERNAME_SITES = {
    # ─── Developer / Tech ───
    "GitHub": "https://github.com/{}",
    "GitLab": "https://gitlab.com/{}",
    "Bitbucket": "https://bitbucket.org/{}",
    "Codeberg": "https://codeberg.org/{}",
    "Hugging Face": "https://huggingface.co/{}",
    "Facebook" : "https://facebook.com/{}",
    "Instagram" : "https://instagram.com/{}",
    "Kaggle": "https://www.kaggle.com/{}",
    "Replit": "https://replit.com/@{}",
    "CodePen": "https://codepen.io/{}",
    "Telegram" : "https://Telegram.com/{}",
    "Dev.to": "https://dev.to/{}",
    "Hashnode": "https://hashnode.com/@{}",

    # ─── Social ───
    "Reddit": "https://www.reddit.com/user/{}",
    "X": "https://x.com/{}",
    "Pinterest": "https://www.pinterest.com/{}/",
    "Tumblr": "https://{}.tumblr.com/",
    "Quora": "https://www.quora.com/profile/{}",
    "VK": "https://vk.com/{}",
    "Bluesky": "https://bsky.app/profile/{}",
    "Threads": "https://www.threads.net/@{}",

    # ─── Media ───
    "YouTube": "https://www.youtube.com/@{}",
    "Twitch": "https://www.twitch.tv/{}",
    "Dailymotion": "https://www.dailymotion.com/{}",
    "Vimeo": "https://vimeo.com/{}",
    "SoundCloud": "https://soundcloud.com/{}",
    "Flickr": "https://www.flickr.com/people/{}",

    # ─── Professional / Identity ───
    "LinkedIn": "https://www.linkedin.com/in/{}",
    "About.me": "https://about.me/{}",
    "Gravatar": "https://gravatar.com/{}",
    "ResearchGate": "https://www.researchgate.net/profile/{}",

    # ─── Publishing ───
    "Medium": "https://medium.com/@{}",
    "Substack": "https://{}.substack.com/",
}

HEADERS = {"User-Agent": "ARGRecon-PRO/2.0"}

results = []


# ========================= HELPERS =========================

def clear():
    os.system("cls" if os.name == "nt" else "clear")


def banner():
    clear()
    print(Fore.GREEN + r"""
     _    ____   ____  ____  _____ ____   ___  _   _
    / \  |  _ \ / ___||  _ \| ____/  __| / _ \| \ | |
   / _ \ | |_) | |  _ | |_) |  _| | |   | | | |  \| |
  / ___ \|  _ <| |_| ||  _ <| |___| |__ |_| | |\  |
 /_/   \_\_| \_\\____||_| \_\_____\____| \___/|_| \_|

+------------------------------------------------------+
|        ADVANCED WEB INFORMATION GATHERING TOOL      |
+------------------------------------------------------+
|        ARGRecon PRO v2.0                             |
|        Developed By : ARG Cyber Skill Hub            |
|        Telegram     : T.me/argcyberskillhub01        |
|        Status       : STAY LEGAL | STAY ETHICAL      |
+------------------------------------------------------+
""")


def section(title):
    print(Fore.CYAN + "\n" + "=" * 60)
    print(Fore.CYAN + f"  {title}")
    print(Fore.CYAN + "=" * 60)


def add_result(line):
    results.append(str(line))


def normalize_domain(value):
    value = value.strip().lower()
    value = re.sub(r"^https?://", "", value)
    return value.split("/")[0].strip(".")


def format_value(value):
    if value is None:
        return "N/A"
    if isinstance(value, (list, tuple, set)):
        return ", ".join(str(v) for v in value)
    return str(value)


def safe_text(value):
    return str(value).replace("<", "&lt;").replace(">", "&gt;")


def http_get(url, timeout=TIMEOUT):
    return requests.get(
        url,
        headers=HEADERS,
        timeout=timeout,
        allow_redirects=True
    )


# ========================= IP ==============================

def ip_lookup_data(ip):
    response = requests.get(
        f"http://ip-api.com/json/{quote(ip)}",
        params={
            "fields":
            "status,message,query,country,regionName,city,zip,"
            "lat,lon,isp,org,as,timezone"
        },
        headers=HEADERS,
        timeout=TIMEOUT
    )
    response.raise_for_status()
    return response.json()


def ip_lookup():
    ip = input(Fore.YELLOW + "\n[?] Enter IP: ").strip()

    try:
        data = ip_lookup_data(ip)
        section("IP INFORMATION")

        if data.get("status") != "success":
            print(Fore.RED + f"[!] {data.get('message', 'Lookup failed')}")
            return

        for key in [
            "query","country","regionName","city","zip",
            "lat","lon","isp","org","as","timezone"
        ]:
            line = f"{key}: {data.get(key, 'N/A')}"
            print(Fore.CYAN + line)
            add_result(line)

    except Exception as exc:
        print(Fore.RED + f"[!] IP lookup failed: {exc}")


# ========================= DNS =============================

def resolve_records(domain, record_type):
    answers = dns.resolver.resolve(
        domain, record_type, lifetime=TIMEOUT
    )
    return [str(a).rstrip(".") for a in answers]


def dns_lookup():
    domain = normalize_domain(
        input(Fore.YELLOW + "\n[?] Domain: ")
    )
    section(f"DNS INFORMATION - {domain}")

    for record_type in ["A", "AAAA", "MX", "NS", "CNAME", "TXT"]:
        try:
            values = resolve_records(domain, record_type)
            print(Fore.GREEN + f"\n[{record_type}]")
            for value in values:
                line = f"{record_type}: {value}"
                print(Fore.CYAN + line)
                add_result(line)
        except Exception:
            print(Fore.YELLOW + f"{record_type}: N/A")


# ========================= WHOIS ============================

def whois_data(domain):
    return whois.whois(domain)


def whois_lookup():
    domain = normalize_domain(
        input(Fore.YELLOW + "\n[?] Domain: ")
    )

    try:
        info = whois_data(domain)
        section("WHOIS INFORMATION")

        if not info:
            print(Fore.RED + "[!] No WHOIS data found.")
            return

        for key, value in info.items():
            if value is None:
                continue
            line = f"{key}: {format_value(value)}"
            print(Fore.CYAN + line)
            add_result(line)

    except Exception as exc:
        print(Fore.RED + f"[!] WHOIS failed: {exc}")


# ========================= PORT SCAN ========================

def check_port(target, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.8)
    try:
        return port if sock.connect_ex((target, port)) == 0 else None
    finally:
        sock.close()


def scan_ports(target):
    found = []
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {
            executor.submit(check_port, target, port): port
            for port in COMMON_PORTS
        }
        for future in as_completed(futures):
            port = future.result()
            if port is not None:
                found.append(port)
    return sorted(found)


def port_scan():
    target = input(
        Fore.YELLOW + "\n[?] Authorized target IP/host: "
    ).strip()

    print(Fore.GREEN + "\n[*] Scanning common TCP ports...\n")

    try:
        open_ports = scan_ports(target)

        if not open_ports:
            print(Fore.YELLOW + "[-] No open common ports found.")
            add_result(f"{target}: no open common ports")
            return

        for port in open_ports:
            line = f"[+] {target}:{port} OPEN"
            print(Fore.GREEN + line)
            add_result(line)

        print(Fore.CYAN + f"\n[+] Open ports: {len(open_ports)}")

    except Exception as exc:
        print(Fore.RED + f"[!] Port scan failed: {exc}")


# ========================= SUBDOMAIN ========================

def resolve_host(host):
    try:
        return socket.gethostbyname_ex(host)[2]
    except socket.gaierror:
        return []


def subdomain_scan():
    domain = normalize_domain(
        input(Fore.YELLOW + "\n[?] Domain: ")
    )

    print(Fore.GREEN + "\n[*] Concurrent DNS subdomain scan...\n")

    found = {}

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {
            executor.submit(resolve_host, f"{sub}.{domain}"): sub
            for sub in SUBDOMAINS
        }

        for future in as_completed(futures):
            sub = futures[future]
            ips = future.result()
            if ips:
                found[f"{sub}.{domain}"] = ips

    for host in sorted(found):
        for ip in found[host]:
            line = f"[+] {host} -> {ip}"
            print(Fore.GREEN + line)
            add_result(line)

    print(Fore.CYAN + f"\n[+] Found: {len(found)} subdomain(s)")


def certificate_subdomains(domain):
    """Passive CT lookup using crt.sh. No active scanning."""
    url = "https://crt.sh/"
    try:
        response = requests.get(
            url,
            params={"q": f"%.{domain}", "output": "json"},
            headers=HEADERS,
            timeout=15
        )
        response.raise_for_status()

        names = set()
        for item in response.json():
            for name in str(item.get("name_value", "")).splitlines():
                name = name.strip().lower()
                if name.startswith("*."):
                    name = name[2:]
                if name == domain or name.endswith("." + domain):
                    names.add(name)

        return sorted(names)

    except Exception:
        return []


def passive_subdomain_scan():
    domain = normalize_domain(
        input(Fore.YELLOW + "\n[?] Domain: ")
    )

    print(Fore.GREEN + "\n[*] Passive Certificate Transparency lookup...\n")

    names = certificate_subdomains(domain)

    if not names:
        print(Fore.YELLOW + "[-] No certificate names returned.")
        return

    for name in names:
        line = f"[+] CT: {name}"
        print(Fore.GREEN + line)
        add_result(line)

    print(Fore.CYAN + f"\n[+] Passive names found: {len(names)}")


# ========================= USERNAME =========================

def username_check(site, url_template, username):
    url = url_template.format(quote(username))
    try:
        response = http_get(url)
        return site, response.status_code, response.url
    except requests.RequestException:
        return site, None, url


def username_scan_value(username):
    found = []
    checked = []

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [
            executor.submit(username_check, site, template, username)
            for site, template in USERNAME_SITES.items()
        ]

        for future in as_completed(futures):
            site, status, final_url = future.result()
            checked.append(site)

            if status == 200:
                found.append((site, final_url))
            elif status in (301, 302, 303, 307, 308):
                # Redirects are reported separately, not treated as proof.
                found.append((site, final_url))

    return sorted(found), sorted(checked)


def username_scan():
    username = input(
        Fore.YELLOW + "\n[?] Public username: "
    ).strip()

    if not username:
        print(Fore.RED + "[!] Username cannot be empty.")
        return

    section(f"USERNAME SCAN - {username}")

    found, checked = username_scan_value(username)

    for site, url in found:
        line = f"[+] {site}: {url}"
        print(Fore.GREEN + line)
        add_result(line)

    print(Fore.CYAN + f"\n[+] Sites checked: {len(checked)}")
    print(Fore.CYAN + f"[+] Potential public matches: {len(found)}")
    print(Fore.YELLOW + "[!] HTTP status/redirects are not proof of identity.")


# ========================= EMAIL ============================

EMAIL_RE = re.compile(
    r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
    r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+$"
)


def email_scan_value(email):
    email = email.strip().lower()

    if not EMAIL_RE.fullmatch(email):
        return {
            "valid": False,
            "email": email,
            "reason": "Invalid email format"
        }

    local, domain = email.rsplit("@", 1)

    data = {
        "valid": True,
        "email": email,
        "local": local,
        "domain": domain,
        "domain_ip": None,
        "mx": [],
        "has_mx": False,
    }

    try:
        data["domain_ip"] = socket.gethostbyname(domain)
    except socket.gaierror:
        pass

    try:
        data["mx"] = resolve_records(domain, "MX")
        data["has_mx"] = bool(data["mx"])
    except Exception:
        pass

    return data


def email_scan():
    email = input(
        Fore.YELLOW + "\n[?] Email address: "
    ).strip().lower()

    data = email_scan_value(email)

    section("EMAIL ANALYSIS")

    if not data["valid"]:
        print(Fore.RED + f"[!] {data['reason']}")
        add_result(f"Email: {email} | INVALID")
        return

    print(Fore.GREEN + f"[+] Format: VALID")
    print(Fore.CYAN + f"[+] Local part: {data['local']}")
    print(Fore.CYAN + f"[+] Domain: {data['domain']}")
    add_result(f"Email: {email}")
    add_result("Format: VALID")
    add_result(f"Domain: {data['domain']}")

    if data["domain_ip"]:
        print(Fore.CYAN + f"[+] Domain IP: {data['domain_ip']}")
        add_result(f"Domain IP: {data['domain_ip']}")
    else:
        print(Fore.RED + "[-] Domain does not resolve.")

    if data["has_mx"]:
        print(Fore.GREEN + "\n[+] MX Records:")
        for mx in data["mx"]:
            print(Fore.CYAN + f"    {mx}")
            add_result(f"MX: {mx}")
    else:
        print(Fore.YELLOW + "[-] No MX record found.")
        add_result("MX: NONE")

    print(Fore.YELLOW + "\n[!] This does not verify mailbox ownership or account existence.")


# ========================= TELEGRAM OUTPUT ==================

def telegram_ip_lookup(ip):
    lines = ["🛰 <b>IP INFORMATION</b>", "━━━━━━━━━━━━━━━━"]
    try:
        data = ip_lookup_data(ip)
        if data.get("status") != "success":
            return "\n".join(lines + [
                f"❌ {safe_text(data.get('message', 'Lookup failed'))}"
            ])

        for key in [
            "query","country","regionName","city","zip",
            "lat","lon","isp","org","as","timezone"
        ]:
            lines.append(
                f"🔹 {key}: {safe_text(data.get(key, 'N/A'))}"
            )
    except Exception as exc:
        lines.append(f"❌ IP Error: {safe_text(exc)}")

    return "\n".join(lines)


def telegram_dns_lookup(domain):
    domain = normalize_domain(domain)
    lines = ["🌐 <b>DNS INFORMATION</b>", "━━━━━━━━━━━━━━━━"]

    for record_type in ["A", "AAAA", "MX", "NS", "CNAME", "TXT"]:
        try:
            values = resolve_records(domain, record_type)
            lines.append(f"\n<b>{record_type}</b>")
            for value in values:
                lines.append(f"🔹 {safe_text(value)}")
        except Exception:
            pass

    if len(lines) == 2:
        lines.append("❌ No DNS records returned.")

    return "\n".join(lines)


def telegram_whois_lookup(domain):
    domain = normalize_domain(domain)
    lines = ["📜 <b>WHOIS INFORMATION</b>", "━━━━━━━━━━━━━━━━"]

    try:
        info = whois_data(domain)
        if not info:
            lines.append("❌ No WHOIS data found.")
            return "\n".join(lines)

        for key, value in info.items():
            if value is None:
                continue
            lines.append(
                f"🔹 <b>{safe_text(key)}</b>: {safe_text(format_value(value))}"
            )

    except Exception as exc:
        lines.append(f"❌ WHOIS Error: {safe_text(exc)}")

    return "\n".join(lines)


def telegram_port_scan(target):
    lines = [
        "🚪 <b>PORT SCAN RESULT</b>",
        "━━━━━━━━━━━━━━━━"
    ]

    try:
        open_ports = scan_ports(target)

        if not open_ports:
            lines.append("❌ No open common ports found.")
        else:
            for port in open_ports:
                lines.append(f"✅ {safe_text(target)}:{port} OPEN")

    except Exception as exc:
        lines.append(f"❌ Port scan error: {safe_text(exc)}")

    return "\n".join(lines)


def telegram_subdomain_scan(domain):
    domain = normalize_domain(domain)
    lines = [
        "🔍 <b>SUBDOMAIN RESULT</b>",
        "━━━━━━━━━━━━━━━━"
    ]

    found = {}

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {
            executor.submit(resolve_host, f"{sub}.{domain}"): sub
            for sub in SUBDOMAINS
        }

        for future in as_completed(futures):
            sub = futures[future]
            ips = future.result()
            if ips:
                found[f"{sub}.{domain}"] = ips

    if not found:
        lines.append("❌ No subdomain found.")
    else:
        for host in sorted(found):
            lines.append(
                f"✅ {safe_text(host)} → {safe_text(', '.join(found[host]))}"
            )

    lines.append(f"\n📊 Found: {len(found)}")
    return "\n".join(lines)


def telegram_passive_subdomain_scan(domain):
    domain = normalize_domain(domain)
    lines = [
        "📜 <b>PASSIVE SUBDOMAIN RESULT</b>",
        "━━━━━━━━━━━━━━━━"
    ]

    names = certificate_subdomains(domain)

    if not names:
        lines.append("❌ No certificate names returned.")
    else:
        for name in names:
            lines.append(f"✅ {safe_text(name)}")
        lines.append(f"\n📊 Found: {len(names)}")

    return "\n".join(lines)


def telegram_username_scan(username):
    username = username.strip()
    lines = [
        "👤 <b>USERNAME SCAN</b>",
        "━━━━━━━━━━━━━━━━",
        f"🔎 {safe_text(username)}"
    ]

    try:
        found, checked = username_scan_value(username)

        if not found:
            lines.append("❌ No potential public profile match returned.")
        else:
            for site, url in found:
                lines.append(
                    f"✅ <b>{safe_text(site)}</b>\n{safe_text(url)}"
                )

        lines.append(f"\n📊 Sites checked: {len(checked)}")
        lines.append("⚠️ HTTP results do not prove identity.")

    except Exception as exc:
        lines.append(f"❌ Username error: {safe_text(exc)}")

    return "\n".join(lines)


def telegram_email_scan(email):
    data = email_scan_value(email)
    lines = [
        "📧 <b>EMAIL ANALYSIS</b>",
        "━━━━━━━━━━━━━━━━"
    ]

    if not data["valid"]:
        lines.append(f"❌ {safe_text(data['reason'])}")
        return "\n".join(lines)

    lines.extend([
        "✅ Format: VALID",
        f"🔹 Local: {safe_text(data['local'])}",
        f"🔹 Domain: {safe_text(data['domain'])}",
    ])

    if data["domain_ip"]:
        lines.append(f"🔹 Domain IP: {safe_text(data['domain_ip'])}")
    else:
        lines.append("⚠️ Domain does not resolve.")

    if data["mx"]:
        lines.append("\n<b>MX Records</b>")
        for mx in data["mx"]:
            lines.append(f"🔹 {safe_text(mx)}")
    else:
        lines.append("⚠️ No MX record found.")

    lines.append(
        "\n⚠️ This does not verify mailbox ownership or account existence."
    )

    return "\n".join(lines)


def telegram_help():
    return """🛡 <b>ARGRecon PRO</b>
━━━━━━━━━━━━━━━━
<b>Domain</b>
/domain example.com
/dns example.com
/whois example.com
/subdomain example.com
/passive example.com

<b>Network</b>
/ip 8.8.8.8
/ports 127.0.0.1

<b>OSINT</b>
/username someuser
/email user@example.com

<b>Utility</b>
/help
/status

Use only on authorized targets."""


# ========================= CLI MENU ========================

def menu():
    while True:
        print(Fore.CYAN + """
==============================
       ARGRecon PRO
==============================
[1]  IP Lookup
[2]  DNS Lookup
[3]  WHOIS Lookup
[4]  Port Scan
[5]  DNS Subdomain Scan
[6]  Passive CT Subdomain Scan
[7]  Username Scanner
[8]  Email Scanner
[9]  Save Results
[10] Clear Results
[11] Exit
==============================
""")

        choice = input(Fore.GREEN + "ARGRecon > ").strip()

        if choice == "1":
            ip_lookup()
        elif choice == "2":
            dns_lookup()
        elif choice == "3":
            whois_lookup()
        elif choice == "4":
            port_scan()
        elif choice == "5":
            subdomain_scan()
        elif choice == "6":
            passive_subdomain_scan()
        elif choice == "7":
            username_scan()
        elif choice == "8":
            email_scan()
        elif choice == "9":
            save_results()
        elif choice == "10":
            results.clear()
            print(Fore.GREEN + "[+] Results cleared.")
        elif choice == "11":
            print(Fore.GREEN + "[+] Goodbye.")
            break
        else:
            print(Fore.RED + "[!] Invalid option.")

        input("\nPress Enter to continue...")
        banner()


if __name__ == "__main__":
    banner()
    menu()
