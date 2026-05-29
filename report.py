"""Build the HTML email body from market data, index movers, and news articles."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

# ── Colour palette ─────────────────────────────────────────────────────────────
_BG     = "#f1f5f9"
_CARD   = "#ffffff"
_HEADER = "#0f172a"
_GREEN  = "#16a34a"
_RED    = "#dc2626"
_GREY   = "#94a3b8"
_TEXT   = "#1e293b"
_MUTED  = "#64748b"
_BORDER = "#e2e8f0"

_SOURCE_COLORS = {
    "Reuters Asia":             "#2563eb",
    "Reuters Markets":          "#2563eb",
    "CNBC Asia":                "#ea580c",
    "Nikkei Asia":              "#dc2626",
    "FT Asia-Pacific":          "#7c3aed",
    "South China Morning Post": "#d97706",
}


# ── Market summary ─────────────────────────────────────────────────────────────

def _build_summary(equity_data: dict, fx_data: dict, articles: list[dict]) -> str:
    sentences: list[str] = []

    # ── Equity tone ───────────────────────────────────────────────────────────
    daily = [(n, d["daily_pct"]) for n, d in equity_data.items() if d.get("daily_pct") is not None]
    if daily:
        n_up    = sum(1 for _, r in daily if r > 0)
        n_total = len(daily)
        if n_up >= round(n_total * 0.7):
            tone = "broadly advanced"
        elif n_up <= round(n_total * 0.3):
            tone = "broadly declined"
        else:
            tone = "traded mixed"

        best  = max(daily, key=lambda x: x[1])
        worst = min(daily, key=lambda x: x[1])

        b_sign = "+" if best[1]  > 0 else ""
        w_sign = "+" if worst[1] > 0 else ""

        sentences.append(
            f"APAC equities <strong>{tone}</strong>, with {n_up} of {n_total} indices closing higher. "
            f"{best[0]} led gains ({b_sign}{best[1]:.1f}%), while {worst[0]} was the weakest performer "
            f"({w_sign}{worst[1]:.1f}%)."
        )

    # ── FX highlight ──────────────────────────────────────────────────────────
    fx_moves = [(n, d["daily_pct"]) for n, d in fx_data.items() if d.get("daily_pct") is not None]
    if fx_moves:
        mover = max(fx_moves, key=lambda x: abs(x[1]))
        direction = "strengthened" if mover[1] < 0 else "weakened"
        # USD pairs: positive = USD stronger (foreign weaker); AUD/USD inverted
        if mover[0] == "AUD/USD":
            direction = "strengthened" if mover[1] > 0 else "weakened"
            ccy = "AUD"
        elif mover[0] == "DXY":
            direction = "rose" if mover[1] > 0 else "fell"
            ccy = "DXY"
        else:
            ccy = mover[0].split("/")[1]   # e.g. JPY from USD/JPY
            direction = f"{ccy} weakened" if mover[1] > 0 else f"{ccy} strengthened"
            ccy = ""
        sign = "+" if mover[1] > 0 else ""
        level = fx_data[mover[0]].get("level")
        level_str = f" to {_fmt_level(level)}" if level else ""
        sentences.append(
            f"In FX, {mover[0]} moved {sign}{mover[1]:.2f}%{level_str} ({direction})."
            if ccy == "" else
            f"In FX, {mover[0]} moved {sign}{mover[1]:.2f}%{level_str}."
        )

    # ── Top news driver ───────────────────────────────────────────────────────
    if articles:
        top = articles[0]
        pub = f" ({top['published'].strftime('%H:%M UTC')})" if top.get("published") else ""
        sentences.append(f"Key story: {top['title']}{pub}.")

    if not sentences:
        return ""

    body = " ".join(sentences)
    return f"""
  <tr>
    <td style="padding:20px 32px 4px;">
      <div style="background:#f8fafc; border-left:4px solid {_HEADER};
          border-radius:4px; padding:14px 18px;">
        <p style="margin:0 0 4px; font-size:10px; font-weight:700; color:{_MUTED};
            text-transform:uppercase; letter-spacing:1px;">Market Summary</p>
        <p style="margin:0; font-size:13px; color:{_TEXT}; line-height:1.7;">{body}</p>
      </div>
    </td>
  </tr>"""


# ── Formatting helpers ─────────────────────────────────────────────────────────

def _fmt_level(v: Optional[float]) -> str:
    if v is None:
        return "—"
    if v >= 1000:
        return f"{v:,.0f}"
    if v >= 10:
        return f"{v:.2f}"
    if v >= 1:
        return f"{v:.3f}"
    return f"{v:.4f}"


def _pct_td(v: Optional[float]) -> str:
    base = f'padding:9px 14px; text-align:right; font-size:13px; border-bottom:1px solid {_BORDER};'
    if v is None:
        return f'<td style="{base} color:{_GREY};">—</td>'
    color = _GREEN if v >= 0 else _RED
    sign  = "+" if v > 0 else ""
    return f'<td style="{base} color:{color}; font-weight:600;">{sign}{v:.2f}%</td>'


def _bps_td(v: Optional[float]) -> str:
    base = f'padding:9px 14px; text-align:right; font-size:13px; border-bottom:1px solid {_BORDER};'
    if v is None:
        return f'<td style="{base} color:{_GREY};">—</td>'
    color = _GREEN if v >= 0 else _RED
    sign  = "+" if v > 0 else ""
    return f'<td style="{base} color:{color}; font-weight:600;">{sign}{v:.0f}bps</td>'


# ── Performance table ──────────────────────────────────────────────────────────

def _perf_table(data: dict) -> str:
    if not data:
        return f'<p style="color:{_GREY}; font-style:italic; font-size:13px; margin:0;">No data available</p>'

    th = (f'padding:9px 14px; font-size:11px; font-weight:700; color:{_MUTED}; '
          f'text-transform:uppercase; letter-spacing:0.8px; border-bottom:2px solid {_BORDER};')

    header = f"""
      <tr style="background:{_BG};">
        <th style="{th} text-align:left;">Instrument</th>
        <th style="{th} text-align:right;">Level</th>
        <th style="{th} text-align:right;">Daily</th>
        <th style="{th} text-align:right;">1M</th>
        <th style="{th} text-align:right;">YTD</th>
      </tr>"""

    rows = ""
    for i, (name, d) in enumerate(data.items()):
        row_bg = "#f8fafc" if i % 2 == 0 else _CARD
        rows += f"""
      <tr style="background:{row_bg};">
        <td style="padding:9px 14px; font-size:13px; font-weight:500; color:{_TEXT}; border-bottom:1px solid {_BORDER};">{name}</td>
        <td style="padding:9px 14px; text-align:right; font-size:13px; font-family:monospace; color:{_TEXT}; border-bottom:1px solid {_BORDER};">{_fmt_level(d.get("level"))}</td>
        {_pct_td(d.get("daily_pct"))}
        {_pct_td(d.get("1m_pct"))}
        {_pct_td(d.get("ytd_pct"))}
      </tr>"""

    return f"""
    <table width="100%" cellpadding="0" cellspacing="0" border="0"
        style="border-collapse:collapse; border:1px solid {_BORDER}; border-radius:6px; overflow:hidden;">
      <thead>{header}</thead>
      <tbody>{rows}</tbody>
    </table>"""


# ── Index movers table ─────────────────────────────────────────────────────────

def _stock_badge(name: str, contribution: float, stock_pct: float) -> str:
    color  = _GREEN if contribution >= 0 else _RED
    bg     = f"{color}14"
    sign_s = "+" if stock_pct > 0 else ""
    return (
        f'<span style="display:inline-block; background:{bg}; color:{color}; '
        f'padding:3px 9px; border-radius:4px; font-size:11px; font-weight:700; '
        f'margin:2px 4px 2px 0; white-space:nowrap;">'
        f'{name}&nbsp; {sign_s}{stock_pct:.1f}%'
        f'</span>'
    )


def _movers_section(movers_by_index: dict) -> str:
    """
    movers_by_index: {index_name: {"top3": [...], "bottom3": [...]}}
    Each entry: {"name": str, "1m_pct": float}
    """
    if not movers_by_index:
        return f'<p style="color:{_GREY}; font-style:italic; font-size:13px; margin:0;">No data available</p>'

    rows = ""
    for i, (idx_name, movers) in enumerate(movers_by_index.items()):
        top3    = movers.get("top3", [])
        bottom3 = movers.get("bottom3", [])

        if not top3 and not bottom3:
            continue

        row_bg  = "#f8fafc" if i % 2 == 0 else _CARD
        top_badges    = "".join(_stock_badge(s["name"], s["contribution"], s["1m_pct"]) for s in top3)    or f'<span style="color:{_GREY}; font-size:12px;">—</span>'
        bottom_badges = "".join(_stock_badge(s["name"], s["contribution"], s["1m_pct"]) for s in bottom3) or f'<span style="color:{_GREY}; font-size:12px;">—</span>'

        rows += f"""
      <tr style="background:{row_bg};">
        <td style="padding:10px 14px; font-size:13px; font-weight:600; color:{_TEXT};
            border-bottom:1px solid {_BORDER}; white-space:nowrap; vertical-align:top;
            width:18%;">{idx_name}</td>
        <td style="padding:10px 14px; border-bottom:1px solid {_BORDER}; vertical-align:top;">
          <div style="margin-bottom:4px;">
            <span style="font-size:10px; font-weight:700; color:{_MUTED};
                text-transform:uppercase; letter-spacing:0.5px; margin-right:6px;">▲ Top</span>
            {top_badges}
          </div>
          <div>
            <span style="font-size:10px; font-weight:700; color:{_MUTED};
                text-transform:uppercase; letter-spacing:0.5px; margin-right:6px;">▼ Bot</span>
            {bottom_badges}
          </div>
        </td>
      </tr>"""

    if not rows:
        return f'<p style="color:{_GREY}; font-style:italic; font-size:13px; margin:0;">No constituent data available</p>'

    return f"""
    <table width="100%" cellpadding="0" cellspacing="0" border="0"
        style="border-collapse:collapse; border:1px solid {_BORDER}; border-radius:6px; overflow:hidden;">
      <thead>
        <tr style="background:{_BG};">
          <th style="padding:9px 14px; font-size:11px; font-weight:700; color:{_MUTED};
              text-transform:uppercase; letter-spacing:0.8px; border-bottom:2px solid {_BORDER};
              text-align:left;">Index</th>
          <th style="padding:9px 14px; font-size:11px; font-weight:700; color:{_MUTED};
              text-transform:uppercase; letter-spacing:0.8px; border-bottom:2px solid {_BORDER};
              text-align:left;">Top / Bottom 3 Contributors (1M, approx. cap-weighted &middot; pp = index contribution)</th>
        </tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>"""


# ── Sector performance section ────────────────────────────────────────────────

_SECTOR_ABBREV = {
    "Communication Services": "Comm. Services",
    "Consumer Discretionary": "Cons. Discr.",
    "Consumer Staples":       "Cons. Staples",
    "Energy":                 "Energy",
    "Financials":             "Financials",
    "Health Care":            "Health Care",
    "Industrials":            "Industrials",
    "Information Technology": "Info. Tech.",
    "Materials":              "Materials",
    "Real Estate":            "Real Estate",
    "Utilities":              "Utilities",
}


def _sector_section(movers_by_index: dict) -> str:
    """
    Renders a grouped table: one index-header row followed by sector rows (best → worst 1M return).
    Style matches the equity performance table.
    """
    if not movers_by_index:
        return f'<p style="color:{_GREY}; font-style:italic; font-size:13px; margin:0;">No sector data available</p>'

    th = (f'padding:9px 14px; font-size:11px; font-weight:700; color:{_MUTED}; '
          f'text-transform:uppercase; letter-spacing:0.8px; border-bottom:2px solid {_BORDER};')

    header = f"""
      <tr style="background:{_BG};">
        <th style="{th} text-align:left;">Index / Sector</th>
        <th style="{th} text-align:right;">Daily</th>
        <th style="{th} text-align:right;">1M</th>
        <th style="{th} text-align:right;">YTD</th>
        <th style="{th} text-align:right;">Sample Wt.</th>
      </tr>"""

    rows = ""
    for idx_name, data in movers_by_index.items():
        sectors = data.get("sectors", {})
        if not sectors:
            continue

        sorted_sectors = sorted(sectors.items(), key=lambda kv: kv[1]["1m_pct"], reverse=True)

        # Index header row
        rows += f"""
      <tr style="background:{_BG};">
        <td colspan="5" style="padding:7px 14px; font-size:11px; font-weight:700;
            color:{_MUTED}; text-transform:uppercase; letter-spacing:0.8px;
            border-top:2px solid {_BORDER}; border-bottom:1px solid {_BORDER};">
          {idx_name}
        </td>
      </tr>"""

        # Sector rows
        for j, (sector, d) in enumerate(sorted_sectors):
            row_bg = "#f8fafc" if j % 2 == 0 else _CARD
            label  = _SECTOR_ABBREV.get(sector, sector)

            rows += f"""
      <tr style="background:{row_bg};">
        <td style="padding:8px 14px 8px 24px; font-size:13px; color:{_TEXT};
            border-bottom:1px solid {_BORDER};">{label}</td>
        {_pct_td(d.get("daily_pct"))}
        {_pct_td(d.get("1m_pct"))}
        {_pct_td(d.get("ytd_pct"))}
        <td style="padding:8px 14px; text-align:right; font-size:12px;
            color:{_MUTED}; border-bottom:1px solid {_BORDER};">{d["weight"]:.0f}%</td>
      </tr>"""

    return f"""
    <table width="100%" cellpadding="0" cellspacing="0" border="0"
        style="border-collapse:collapse; border:1px solid {_BORDER}; border-radius:6px; overflow:hidden;">
      <thead>{header}</thead>
      <tbody>{rows}</tbody>
    </table>"""


# ── News section ───────────────────────────────────────────────────────────────

def _news_section(articles: list[dict]) -> str:
    if not articles:
        return f'<p style="color:{_GREY}; font-style:italic; font-size:13px; margin:0;">No stories found.</p>'

    items = ""
    for art in articles:
        pub_str  = art["published"].strftime("%H:%M UTC · %d %b") if art["published"] else ""
        clr      = _SOURCE_COLORS.get(art["source"], "#2563eb")
        badge_bg = f"{clr}18"

        title_html = (
            f'<a href="{art["link"]}" style="color:{_TEXT}; text-decoration:none; '
            f'font-size:14px; font-weight:600; line-height:1.45;">{art["title"]}</a>'
            if art["link"]
            else f'<span style="font-size:14px; font-weight:600; color:{_TEXT};">{art["title"]}</span>'
        )
        summary_html = (
            f'<p style="margin:5px 0 0; color:{_MUTED}; font-size:12px; line-height:1.6;">{art["summary"]}</p>'
            if art["summary"] else ""
        )

        items += f"""
      <tr>
        <td style="padding:14px 0; border-bottom:1px solid {_BORDER}; vertical-align:top;">
          <div style="margin-bottom:6px;">
            <span style="display:inline-block; background:{badge_bg}; color:{clr};
                padding:2px 8px; border-radius:4px; font-size:10px; font-weight:700;
                letter-spacing:0.5px; text-transform:uppercase;">{art["source"]}</span>
            <span style="color:{_GREY}; font-size:11px; margin-left:8px;">{pub_str}</span>
          </div>
          {title_html}
          {summary_html}
        </td>
      </tr>"""

    return f'<table width="100%" cellpadding="0" cellspacing="0" border="0">{items}</table>'


# ── Macro section (performance + news combined) ────────────────────────────────

def _macro_section(macro_data: dict, macro_news: list[dict]) -> str:
    th = (f'padding:9px 14px; font-size:11px; font-weight:700; color:{_MUTED}; '
          f'text-transform:uppercase; letter-spacing:0.8px; border-bottom:2px solid {_BORDER};')

    header = f"""
      <tr style="background:{_BG};">
        <th style="{th} text-align:left;">Instrument</th>
        <th style="{th} text-align:right;">Level</th>
        <th style="{th} text-align:right;">Daily</th>
        <th style="{th} text-align:right;">1M</th>
        <th style="{th} text-align:right;">YTD</th>
      </tr>"""

    rows = ""
    for i, (name, d) in enumerate(macro_data.items()):
        row_bg   = "#f8fafc" if i % 2 == 0 else _CARD
        is_yield = d.get("is_yield", False)
        level    = d.get("level")

        level_str = (
            f'{_fmt_level(level)}%' if is_yield and level is not None
            else _fmt_level(level)
        )
        daily_td = _bps_td(d.get("daily_pct")) if is_yield else _pct_td(d.get("daily_pct"))
        m1_td    = _bps_td(d.get("1m_pct"))    if is_yield else _pct_td(d.get("1m_pct"))
        ytd_td   = _bps_td(d.get("ytd_pct"))   if is_yield else _pct_td(d.get("ytd_pct"))

        rows += f"""
      <tr style="background:{row_bg};">
        <td style="padding:9px 14px; font-size:13px; font-weight:500; color:{_TEXT};
            border-bottom:1px solid {_BORDER};">{name}</td>
        <td style="padding:9px 14px; text-align:right; font-size:13px;
            font-family:monospace; color:{_TEXT}; border-bottom:1px solid {_BORDER};">{level_str}</td>
        {daily_td}{m1_td}{ytd_td}
      </tr>"""

    perf_table = f"""
    <table width="100%" cellpadding="0" cellspacing="0" border="0"
        style="border-collapse:collapse; border:1px solid {_BORDER}; border-radius:6px; overflow:hidden;">
      <thead>{header}</thead>
      <tbody>{rows}</tbody>
    </table>""" if rows else ""

    # Macro news (compact — no summary, just headline + source + time)
    news_html = ""
    if macro_news:
        items = ""
        for art in macro_news:
            pub_str = art["published"].strftime("%H:%M UTC · %d %b") if art.get("published") else ""
            clr     = _SOURCE_COLORS.get(art["source"], "#2563eb")
            badge_bg = f"{clr}18"
            title_html = (
                f'<a href="{art["link"]}" style="color:{_TEXT}; text-decoration:none; '
                f'font-size:13px; font-weight:600;">{art["title"]}</a>'
                if art["link"]
                else f'<span style="font-size:13px; font-weight:600; color:{_TEXT};">{art["title"]}</span>'
            )
            items += f"""
        <tr>
          <td style="padding:10px 0; border-bottom:1px solid {_BORDER}; vertical-align:top;">
            <span style="display:inline-block; background:{badge_bg}; color:{clr};
                padding:2px 8px; border-radius:4px; font-size:10px; font-weight:700;
                letter-spacing:0.5px; text-transform:uppercase;">{art["source"]}</span>
            <span style="color:{_GREY}; font-size:11px; margin-left:8px;">{pub_str}</span>
            <br style="line-height:4px;">
            {title_html}
          </td>
        </tr>"""

        news_html = f"""
    <p style="margin:18px 0 8px; font-size:11px; font-weight:700; color:{_MUTED};
        text-transform:uppercase; letter-spacing:1px;">Global Macro News</p>
    <table width="100%" cellpadding="0" cellspacing="0" border="0">{items}</table>"""

    return f"""
  <tr>
    <td style="padding:24px 32px 20px;">
      <h2 style="margin:0 0 14px; font-size:12px; font-weight:700; color:{_MUTED};
          text-transform:uppercase; letter-spacing:1.2px; padding-bottom:8px;
          border-bottom:2px solid {_BORDER};">Global Macro</h2>
      {perf_table}
      {news_html}
    </td>
  </tr>
  <tr><td style="height:1px; background:{_BORDER};"></td></tr>"""


# ── Section wrapper ────────────────────────────────────────────────────────────

def _section(heading: str, body: str) -> str:
    return f"""
  <tr>
    <td style="padding:24px 32px 20px;">
      <h2 style="margin:0 0 14px; font-size:12px; font-weight:700; color:{_MUTED};
          text-transform:uppercase; letter-spacing:1.2px; padding-bottom:8px;
          border-bottom:2px solid {_BORDER};">{heading}</h2>
      {body}
    </td>
  </tr>
  <tr><td style="height:1px; background:{_BORDER};"></td></tr>"""


# ── Public entry point ─────────────────────────────────────────────────────────

def build_html(
    equity_data:   dict,
    fx_data:       dict,
    movers_data:   dict,
    articles:      list[dict],
    generated_at:  datetime,
    macro_data:    dict | None = None,
    macro_news:    list[dict] | None = None,
) -> str:
    date_str = generated_at.strftime("%A %-d %B %Y")
    time_str = generated_at.strftime("%H:%M UTC")
    n_news   = len(articles)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>APAC Daily Brief — {date_str}</title>
</head>
<body style="margin:0; padding:0; background:{_BG};
    font-family:'Segoe UI',Helvetica,Arial,sans-serif; -webkit-font-smoothing:antialiased;">

<table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:{_BG};">
<tr><td align="center" style="padding:24px 16px;">

<table width="660" cellpadding="0" cellspacing="0" border="0"
    style="max-width:660px; width:100%; background:{_CARD}; border-radius:10px;
    overflow:hidden; box-shadow:0 4px 20px rgba(0,0,0,0.09);">

  <!-- HEADER -->
  <tr>
    <td style="background:{_HEADER}; padding:28px 32px 22px;">
      <p style="margin:0 0 6px; color:#475569; font-size:10px; font-weight:700;
          letter-spacing:2px; text-transform:uppercase;">IMC Trading &nbsp;·&nbsp; APAC Macro</p>
      <h1 style="margin:0 0 4px; color:#f8fafc; font-size:26px; font-weight:800;
          letter-spacing:-0.5px;">APAC Daily Brief</h1>
      <p style="margin:0; color:#94a3b8; font-size:13px;">{date_str} &nbsp;·&nbsp; Generated {time_str}</p>
    </td>
  </tr>

  {_build_summary(equity_data, fx_data, articles)}

  {_section("APAC Equity Performance", _perf_table(equity_data))}
  {_macro_section(macro_data or {}, macro_news or [])}
  {_section("FX Snapshot", _perf_table(fx_data))}
  {_section(f"Top News &mdash; Asia Pacific &nbsp;({n_news} stories)", _news_section(articles))}
  {_section("Index Contributors &mdash; Top / Bottom 3 (1M, Cap-Weighted)", _movers_section(movers_data))}
  {_section("Sector Performance &mdash; GICS Level 1 (1M, Approx. Cap-Weighted)", _sector_section(movers_data))}

  <!-- FOOTER -->
  <tr>
    <td style="background:#f8fafc; padding:18px 32px; border-top:1px solid {_BORDER};">
      <p style="margin:0; color:{_MUTED}; font-size:11px; line-height:1.7;">
        Generated at <strong>{time_str}</strong> &nbsp;·&nbsp;
        Market data: Yahoo Finance, stooq.com &nbsp;·&nbsp;
        News: Reuters, CNBC, Nikkei Asia, FT, SCMP
      </p>
      <p style="margin:4px 0 0; color:{_GREY}; font-size:10px;">
        Contributors ranked by approximate cap-weighted 1M contribution. For internal research purposes only. Not investment advice.
      </p>
    </td>
  </tr>

</table>
</td></tr>
</table>
</body>
</html>"""
