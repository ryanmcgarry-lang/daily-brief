"""All configuration: market tickers, news feeds, APAC keyword filter."""

# ── Equity indices ────────────────────────────────────────────────────────────
# source: "yahoo" = yfinance | "stooq" = stooq.com CSV (for tickers Yahoo lacks)
EQUITY_INDICES = {
    "Nikkei 225":    {"ticker": "^N225",     "source": "yahoo", "country": "Japan"},
    "TOPIX":         {"ticker": "1308.T",    "source": "yahoo", "country": "Japan"},   # Nikko AM TOPIX ETF ≈ index level
    "CSI 300":       {"ticker": "000300.SS", "source": "yahoo", "country": "China"},
    "Shanghai Comp": {"ticker": "000001.SS", "source": "yahoo", "country": "China"},
    "Hang Seng":     {"ticker": "^HSI",      "source": "yahoo", "country": "Hong Kong"},
    "KOSPI":         {"ticker": "^KS11",     "source": "yahoo", "country": "South Korea"},
    "ASX 200":       {"ticker": "^AXJO",     "source": "yahoo", "country": "Australia"},
    "TAIEX":         {"ticker": "^TWII",     "source": "yahoo", "country": "Taiwan"},
}

# ── FX pairs (yfinance tickers) ────────────────────────────────────────────────
FX_PAIRS = {
    "USD/JPY":  "USDJPY=X",
    "USD/CNY":  "USDCNY=X",
    "AUD/USD":  "AUDUSD=X",
    "USD/KRW":  "USDKRW=X",
    "USD/TWD":  "USDTWD=X",
}

# ── Macro instruments ──────────────────────────────────────────────────────────
# type "index"/"commodity"/"fx" → pct changes; type "yield" → bps changes
MACRO_INSTRUMENTS = {
    "S&P 500":    {"ticker": "^GSPC",    "type": "index"},
    "WTI Crude":  {"ticker": "CL=F",     "type": "commodity"},
    "Brent Crude":{"ticker": "BZ=F",     "type": "commodity"},
    "DXY":        {"ticker": "DX-Y.NYB", "type": "fx"},
    "US 10yr":    {"ticker": "^TNX",     "type": "yield"},
    # JGB 10yr yield is not available on Yahoo Finance.
    # To add it: sign up for a free FRED API key and use series IRLTLT01JPM156N.
}

# ── Macro news keywords ────────────────────────────────────────────────────────
# Stories matching these are surfaced in the Macro section, not the APAC section.
MACRO_NEWS_KEYWORDS = [
    # US Federal Reserve
    "federal reserve", "fomc", "jerome powell", "fed rate",
    "fed funds rate", "us rate hike", "us rate cut", "us monetary policy",
    # US economic data
    "nonfarm payroll", "us cpi", "us inflation", "us pce",
    "us gdp", "us jobs report", "us unemployment",
    "treasury yield", "us 10-year", "us 10yr", "us bond yield",
    # Oil & energy
    "opec", "oil price", "crude oil", "brent crude", "wti crude",
    "oil output", "oil supply", "energy prices",
    # Dollar
    "dollar index", "dxy", "us dollar rally", "dollar strengthened",
    "dollar weakened", "dollar rose", "dollar fell", "greenback",
    # Global macro
    "global growth", "global recession", "imf forecast", "world bank",
    "global inflation", "g20 summit", "g7 summit",
    # Risk sentiment
    "risk-off", "risk off", "safe haven", "flight to quality",
    "global selloff", "market rout", "vix spike",
]

# ── News RSS feeds ─────────────────────────────────────────────────────────────
NEWS_FEEDS = [
    {"name": "Reuters Asia",             "url": "https://feeds.reuters.com/reuters/AsiaNews"},
    {"name": "Reuters Markets",          "url": "https://feeds.reuters.com/reuters/businessNews"},
    {"name": "CNBC Asia",                "url": "https://www.cnbc.com/id/19832390/device/rss/rss.html"},
    {"name": "Nikkei Asia",              "url": "https://asia.nikkei.com/rss/feed/nar"},
    {"name": "FT Asia-Pacific",          "url": "https://www.ft.com/rss/home/asia-pacific"},
    {"name": "South China Morning Post", "url": "https://www.scmp.com/rss/2/feed"},
]

# ── APAC relevance keyword filter ─────────────────────────────────────────────
APAC_KEYWORDS = [
    # Countries & regions
    "japan", "china", "korea", "australia", "taiwan", "hong kong", "singapore",
    "indonesia", "malaysia", "thailand", "vietnam", "philippines", "new zealand",
    "asia", "pacific", "apac", "asean",
    # Indices & markets
    "nikkei", "topix", "hang seng", "kospi", "asx", "shanghai", "shenzhen",
    "taiex", "csi", "hsi",
    # Central banks
    "boj", "pboc", "rba", "rbnz", "bank of japan", "people's bank of china",
    "reserve bank of australia", "bank of korea",
    # Currencies
    "yen", "yuan", "renminbi", "won", "baht", "ringgit", "rupiah",
    "jpy", "cny", "cnh", "krw", "aud",
    # Key themes
    "tariff", "semiconductor", "rare earth", "trade war",
    "taiwan strait", "south china sea",
]
