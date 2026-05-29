"""
RSS news aggregation for APAC markets.
Articles are ranked by a composite score: market-impact keywords × 0.7 + recency × 0.3.
Pure chronological ordering is replaced by this market-relevance score so that
BOJ rate decisions, GDP prints, and tariff announcements surface before general Asia coverage.
"""
from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from typing import Optional

import feedparser

from config import APAC_KEYWORDS, MACRO_NEWS_KEYWORDS, NEWS_FEEDS

log = logging.getLogger(__name__)

# ── Impact scoring tiers ───────────────────────────────────────────────────────
# Each tier: (base_score, [keywords]).  Score = max across all matching tiers.

_IMPACT_TIERS = [
    (12, ["rate hike", "rate cut", "emergency cut", "emergency rate",
          "interest rate decision", "benchmark rate", "policy rate announcement"]),
    (10, ["boj decision", "pboc decision", "rba decision", "bok decision",
          "bank of japan", "monetary policy statement",
          "quantitative easing", "yield curve control", "ycc"]),
    (8,  ["gdp", "consumer price index", "cpi", "pmi reading",
          "industrial production", "trade balance",
          "unemployment rate", "jobs report", "payrolls"]),
    (7,  ["tariff", "trade war", "trade deal", "sanctions", "export ban",
          "tech ban", "chip ban", "semiconductor restriction", "import duties"]),
    (6,  ["intervention", "currency intervention", "fx intervention",
          "yen intervention", "fx reserve", "stimulus package", "fiscal stimulus",
          "devaluation", "revaluation", "bond purchase", "bond buying",
          "record high", "record low", "all-time high", "circuit breaker",
          "flash crash", "market crash", "equity rout", "bond rout"]),
    (5,  ["earnings beat", "earnings miss", "profit warning", "guidance cut",
          "revenue miss", "revenue beat", "quarterly results",
          "results beat", "results miss"]),
    (4,  ["central bank", "monetary policy", "interest rate", "rate path",
          "rate outlook", "hawkish", "dovish",
          "valuation", "overvalued", "undervalued", "bubble"]),
    (3,  ["inflation", "growth outlook", "pmi", "gdp growth",
          "stock market", "equity market", "bond market", "capital markets",
          "index performance", "market performance", "market rally", "market selloff",
          "ipo", "listing", "fundraising", "fund raise"]),
    (2,  ["acquisition", "merger", "takeover", "restructuring", "layoffs", "job cuts",
          "profit warning", "profit growth", "net profit", "operating profit",
          "net revenue", "quarterly earnings", "annual earnings",
          "dividend cut", "dividend hike", "share buyback", "stock buyback"]),
    (1,  ["stock upgrade", "stock downgrade", "analyst upgrade", "analyst downgrade",
          "credit rating", "sovereign rating", "rating cut", "rating upgrade",
          "price target", "broker note", "initiates coverage"]),
]

_SPECIFIC_MARKETS = [
    "nikkei", "topix", "kospi", "hang seng", "asx 200",
    "taiex", "csi 300", "shanghai composite",
]
_GENERIC_MARKETS = [
    "japan", "china", "korea", "australia", "taiwan",
    "hong kong", "singapore", "indonesia",
]

# Articles must contain at least one of these to pass the financial-context gate.
# Prevents geographic APAC matches on sports, crime, accidents, etc.
_MARKET_CONTEXT_KEYWORDS = [
    # Markets & instruments
    "stock", "stocks", "equity", "equities", "index", "indices", "market", "markets",
    "share", "shares", "bond", "bonds", "yield", "yields", "futures", "options",
    "commodity", "commodities", "etf", "trading", "investor", "investors",
    # Macro & economic data
    "economy", "economic", "gdp", "growth", "inflation", "deflation",
    "cpi", "pmi", "unemployment", "jobs", "payrolls", "trade balance",
    "current account", "fiscal", "deficit", "surplus",
    # Monetary policy
    "central bank", "interest rate", "rate hike", "rate cut", "monetary policy",
    "quantitative easing", "qe", "tapering", "boj", "pboc", "rba", "rbnz",
    "bank of japan", "bank of korea", "bank of england", "fed", "federal reserve",
    "hawkish", "dovish", "yield curve",
    # Trade & geopolitics with market impact
    "tariff", "tariffs", "sanctions", "trade war", "trade deal", "export ban",
    "import", "supply chain", "semiconductor", "chip", "rare earth",
    "currency", "currencies", "forex", "fx", "yen", "yuan", "renminbi",
    "devaluation", "revaluation", "intervention",
    # Corporate finance
    "earnings", "revenue", "profit", "loss", "ipo", "listing", "merger",
    "acquisition", "restructuring", "layoffs", "guidance", "outlook",
    "dividend", "buyback", "debt", "bankruptcy",
    # Geopolitical / risk events with direct market implications
    "military", "conflict", "tensions", "strait", "blockade", "invasion",
    "stimulus", "spending", "budget", "reform", "regulation", "policy",
]


def _impact_score(text: str) -> float:
    """Return the highest matching impact tier score, or 0 if none match."""
    score = 0.0
    for tier_score, keywords in _IMPACT_TIERS:
        if any(kw in text for kw in keywords):
            score = max(score, float(tier_score))
    return score


def _score(art: dict) -> float:
    """Composite market-impact score for ranking. Higher = more market-moving."""
    text = (art["title"] + " " + art.get("summary", "")).lower()

    impact = _impact_score(text)

    # Bonus for naming specific indices / countries (capped at +6)
    spec  = sum(1 for m in _SPECIFIC_MARKETS if m in text)
    gen   = sum(1 for m in _GENERIC_MARKETS  if m in text)
    market_bonus = min(spec * 2 + gen * 1, 6)

    # Recency: 0–5 points decaying over 24 h (tiebreaker only, not a primary driver)
    recency = 0.0
    if art.get("published"):
        age_h = (datetime.now(timezone.utc) - art["published"]).total_seconds() / 3600
        if   age_h < 2:   recency = 5.0
        elif age_h < 6:   recency = 3.0
        elif age_h < 12:  recency = 2.0
        elif age_h < 24:  recency = 1.0

    return (impact + market_bonus) * 0.85 + recency * 0.15


# ── Public function ────────────────────────────────────────────────────────────

def fetch_apac_news(max_per_feed: int = 20, max_total: int = 10) -> list[dict]:
    """
    Pull RSS feeds, filter for APAC relevance, rank by market-impact score.
    Returns up to max_total articles, highest impact first.
    """
    articles: list[dict] = []
    seen: set[str] = set()

    for feed_meta in NEWS_FEEDS:
        try:
            parsed = feedparser.parse(feed_meta["url"])
            for entry in parsed.entries[:max_per_feed]:
                title = entry.get("title", "").strip()
                if not title or title in seen:
                    continue

                summary = _strip_html(
                    entry.get("summary", entry.get("description", ""))
                )[:400]

                combined = (title + " " + summary).lower()
                if not any(kw in combined for kw in APAC_KEYWORDS):
                    continue
                if not any(kw in combined for kw in _MARKET_CONTEXT_KEYWORDS):
                    continue
                if _impact_score(combined) == 0:
                    continue

                published: Optional[datetime] = None
                tp = entry.get("published_parsed")
                if tp:
                    try:
                        published = datetime(*tp[:6], tzinfo=timezone.utc)
                    except Exception:
                        pass

                articles.append({
                    "title":     title,
                    "summary":   summary,
                    "link":      entry.get("link", ""),
                    "source":    feed_meta["name"],
                    "published": published,
                })
                seen.add(title)

        except Exception as e:
            log.warning(f"Feed unavailable — {feed_meta['name']}: {e}")

    articles.sort(key=_score, reverse=True)
    return articles[:max_total]


def fetch_macro_news(seen_titles: set[str] | None = None, max_total: int = 5) -> list[dict]:
    """
    Pull macro-relevant stories (Fed, oil, DXY, global growth) from the same RSS feeds.
    Excludes any titles already in the APAC news section to avoid duplication.
    """
    seen = set(seen_titles) if seen_titles else set()
    articles: list[dict] = []

    for feed_meta in NEWS_FEEDS:
        try:
            parsed = feedparser.parse(feed_meta["url"])
            for entry in parsed.entries[:30]:
                title = entry.get("title", "").strip()
                if not title or title in seen:
                    continue

                summary = _strip_html(
                    entry.get("summary", entry.get("description", ""))
                )[:400]

                combined = (title + " " + summary).lower()
                if not any(kw in combined for kw in MACRO_NEWS_KEYWORDS):
                    continue
                if _impact_score(combined) == 0:
                    continue

                published: Optional[datetime] = None
                tp = entry.get("published_parsed")
                if tp:
                    try:
                        published = datetime(*tp[:6], tzinfo=timezone.utc)
                    except Exception:
                        pass

                articles.append({
                    "title":     title,
                    "summary":   summary,
                    "link":      entry.get("link", ""),
                    "source":    feed_meta["name"],
                    "published": published,
                })
                seen.add(title)

        except Exception as e:
            log.warning(f"Feed unavailable — {feed_meta['name']}: {e}")

    articles.sort(key=_score, reverse=True)
    return articles[:max_total]


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text).strip()
