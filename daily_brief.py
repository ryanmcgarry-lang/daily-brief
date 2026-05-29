#!/usr/bin/env python3
"""
APAC Daily Brief — fetch market data + news, build HTML report, send by email.

Usage:
    python daily_brief.py              # fetch data and send email
    python daily_brief.py --preview    # save HTML to /tmp and open in browser (no email sent)

Scheduling via cron (runs weekdays at 09:00 UTC — after all APAC markets close):
    crontab -e
    0 9 * * 1-5 /path/to/python /Users/ryanmcgarry/daily_brief/daily_brief.py \
        >> /Users/ryanmcgarry/daily_brief/daily_brief.log 2>&1

SMTP settings are read from .env (copy .env.example and fill in your credentials).
Supported providers:
    Outlook / Hotmail : SMTP_HOST=smtp-mail.outlook.com  SMTP_PORT=587
    Gmail             : SMTP_HOST=smtp.gmail.com         SMTP_PORT=587  (use App Password if 2FA on)
"""

import logging
import os
import smtplib
import sys
import tempfile
import webbrowser
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _require(key: str) -> str:
    val = os.getenv(key, "").strip()
    if not val:
        log.error(f"Missing required env var: {key}  — check your .env file.")
        sys.exit(1)
    return val


def _send_email(html: str, subject: str) -> None:
    smtp_host = _require("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = _require("SMTP_USER")
    smtp_pass = _require("SMTP_PASS")
    email_to  = _require("EMAIL_TO")
    from_name = os.getenv("EMAIL_FROM_NAME", "APAC Daily Brief")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"{from_name} <{smtp_user}>"
    msg["To"]      = email_to
    msg.attach(MIMEText(html, "html", "utf-8"))

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.ehlo()
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)

    log.info(f"Email sent → {email_to}")


def _preview(html: str, date_str: str) -> None:
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".html", prefix=f"apac_brief_{date_str}_",
        delete=False, encoding="utf-8",
    ) as f:
        f.write(html)
        path = f.name
    log.info(f"Preview saved → {path}")
    webbrowser.open(f"file://{path}")


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    preview_mode = "--preview" in sys.argv
    now = datetime.now(timezone.utc)
    log.info(f"Starting — {now.strftime('%Y-%m-%d %H:%M UTC')}")

    import config
    from constituents import CONSTITUENTS
    from data import fetch_equity_performance, fetch_fx_performance, fetch_all_movers, fetch_macro_performance
    from news import fetch_apac_news, fetch_macro_news
    from report import build_html

    log.info(f"Fetching equity data ({len(config.EQUITY_INDICES)} indices)...")
    equity = fetch_equity_performance()
    log.info(f"  {len(equity)} returned")

    log.info(f"Fetching FX data ({len(config.FX_PAIRS)} pairs)...")
    fx = fetch_fx_performance()
    log.info(f"  {len(fx)} returned")

    n_stocks = sum(len(v) for v in CONSTITUENTS.values())
    log.info(f"Fetching index movers ({len(CONSTITUENTS)} indices, {n_stocks} stocks)...")
    movers = fetch_all_movers()
    log.info(f"  {len(movers)} indices with mover data")

    log.info(f"Fetching macro data ({len(config.MACRO_INSTRUMENTS)} instruments)...")
    macro = fetch_macro_performance()
    log.info(f"  {len(macro)} returned")

    log.info("Fetching APAC news...")
    articles = fetch_apac_news()
    log.info(f"  {len(articles)} stories")

    log.info("Fetching macro news...")
    macro_news = fetch_macro_news(seen_titles={a["title"] for a in articles})
    log.info(f"  {len(macro_news)} stories")

    log.info("Building report...")
    html = build_html(equity, fx, movers, articles, now, macro_data=macro, macro_news=macro_news)

    subject  = f"APAC Daily Brief — {now.strftime('%A %-d %B %Y')}"
    date_str = now.strftime("%Y-%m-%d")

    if preview_mode:
        _preview(html, date_str)
    else:
        log.info("Sending email...")
        _send_email(html, subject)

    log.info("Done.")


if __name__ == "__main__":
    main()
