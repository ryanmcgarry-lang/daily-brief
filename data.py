"""Market data fetching — equity indices (Yahoo Finance), FX, and index movers."""
from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta
from typing import Optional

import pandas as pd
import yfinance as yf

from config import EQUITY_INDICES, FX_PAIRS, MACRO_INSTRUMENTS

log = logging.getLogger(__name__)

_START_DATE = (date(date.today().year, 1, 1) - timedelta(days=10)).strftime("%Y-%m-%d")


# ── Per-ticker fetcher ─────────────────────────────────────────────────────────

def _fetch_close_yahoo(yf_ticker: str) -> Optional[pd.Series]:
    """Close price series via yfinance."""
    try:
        hist = yf.Ticker(yf_ticker).history(start=_START_DATE, auto_adjust=True)
        if hist.empty:
            return None
        s = hist["Close"].dropna()
        if s.index.tz is not None:
            s.index = s.index.tz_convert("UTC").tz_localize(None)
        return s
    except Exception as e:
        log.debug(f"Yahoo fetch failed — {yf_ticker}: {e}")
        return None


# ── Performance calculator ─────────────────────────────────────────────────────

def _calc_perf(series: Optional[pd.Series]) -> Optional[dict]:
    if series is None or len(series) < 2:
        return None

    today     = date.today()
    today_ts  = pd.Timestamp(today)
    current   = float(series.iloc[-1])
    prev      = float(series.iloc[-2])

    cutoff_1m = today_ts - pd.DateOffset(months=1)
    prior_1m  = series[series.index <= cutoff_1m]
    price_1m  = float(prior_1m.iloc[-1]) if not prior_1m.empty else float(series.iloc[0])

    this_year = series[series.index.year == today.year]
    price_ytd = float(this_year.iloc[0]) if not this_year.empty else float(series.iloc[0])

    def _pct(new: float, old: float) -> Optional[float]:
        return round((new - old) / old * 100, 2) if old != 0 else None

    return {
        "level":     round(current, 2),
        "daily_pct": _pct(current, prev),
        "1m_pct":    _pct(current, price_1m),
        "ytd_pct":   _pct(current, price_ytd),
    }


# ── Batch fetcher (Yahoo-only, used for FX and constituents) ──────────────────

def _fetch_batch(ticker_map: dict[str, str]) -> dict[str, dict]:
    """Fetch {name: yf_ticker} concurrently."""
    results: dict[str, dict] = {}

    def _work(name: str, ticker: str):
        return name, _calc_perf(_fetch_close_yahoo(ticker))

    with ThreadPoolExecutor(max_workers=16) as pool:
        futs = {pool.submit(_work, n, t): n for n, t in ticker_map.items()}
        for fut in as_completed(futs):
            try:
                name, data = fut.result()
                if data:
                    results[name] = data
                else:
                    log.warning(f"No data for {name} ({ticker_map[name]})")
            except Exception as e:
                log.error(f"Worker error: {e}")

    return {n: results[n] for n in ticker_map if n in results}


# ── Yield change calculator (bps instead of %) ────────────────────────────────

def _calc_yield_change(series: Optional[pd.Series]) -> Optional[dict]:
    if series is None or len(series) < 2:
        return None

    today     = date.today()
    today_ts  = pd.Timestamp(today)
    current   = float(series.iloc[-1])
    prev      = float(series.iloc[-2])

    cutoff_1m = today_ts - pd.DateOffset(months=1)
    prior_1m  = series[series.index <= cutoff_1m]
    price_1m  = float(prior_1m.iloc[-1]) if not prior_1m.empty else float(series.iloc[0])

    this_year = series[series.index.year == today.year]
    price_ytd = float(this_year.iloc[0]) if not this_year.empty else float(series.iloc[0])

    def _bps(new: float, old: float) -> float:
        return round((new - old) * 100, 1)

    return {
        "level":     round(current, 3),
        "daily_pct": _bps(current, prev),
        "1m_pct":    _bps(current, price_1m),
        "ytd_pct":   _bps(current, price_ytd),
        "is_yield":  True,
    }


# ── Public data functions ──────────────────────────────────────────────────────

def fetch_equity_performance() -> dict:
    """Fetch index-level performance for all configured equity indices."""
    results: dict[str, dict] = {}

    def _work(name: str, meta: dict):
        return name, _calc_perf(_fetch_close_yahoo(meta["ticker"]))

    with ThreadPoolExecutor(max_workers=8) as pool:
        futs = {pool.submit(_work, n, m): n for n, m in EQUITY_INDICES.items()}
        for fut in as_completed(futs):
            try:
                name, data = fut.result()
                if data:
                    results[name] = data
                else:
                    log.warning(f"No data for {name}")
            except Exception as e:
                log.error(f"Equity worker error: {e}")

    return {n: results[n] for n in EQUITY_INDICES if n in results}


def fetch_fx_performance() -> dict:
    return _fetch_batch(FX_PAIRS)


def fetch_macro_performance() -> dict:
    """Fetch S&P, oil, DXY, US 10yr, JGB 10yr. Yields return bps changes."""
    results: dict[str, dict] = {}

    def _work(name: str, meta: dict):
        series = _fetch_close_yahoo(meta["ticker"])
        if meta["type"] == "yield":
            return name, _calc_yield_change(series)
        return name, _calc_perf(series)

    with ThreadPoolExecutor(max_workers=8) as pool:
        futs = {pool.submit(_work, n, m): n for n, m in MACRO_INSTRUMENTS.items()}
        for fut in as_completed(futs):
            try:
                name, data = fut.result()
                if data:
                    results[name] = data
                else:
                    log.warning(f"No macro data for {name}")
            except Exception as e:
                log.error(f"Macro worker error: {e}")

    return {n: results[n] for n in MACRO_INSTRUMENTS if n in results}


def _fetch_constituent(name: str, ticker: str) -> tuple[str, Optional[dict], Optional[float]]:
    """Return (name, perf_dict, market_cap). market_cap may be None if unavailable."""
    series = _fetch_close_yahoo(ticker)
    perf   = _calc_perf(series)
    cap: Optional[float] = None
    try:
        info = yf.Ticker(ticker).fast_info
        cap  = getattr(info, "market_cap", None)
    except Exception:
        pass
    return name, perf, cap


def fetch_all_movers() -> dict[str, dict]:
    """
    For each index in CONSTITUENTS, return the top 3 and bottom 3 stocks by
    approximate cap-weighted 1M contribution (weight × 1m_pct).

    Returns:
        {
          "Nikkei 225": {
            "top3":    [{"name": ..., "1m_pct": ..., "contribution": ..., "weight": ...}, ...],
            "bottom3": [...],
          },
          ...
        }
    """
    from constituents import CONSTITUENTS

    # Build a flat {compound_key: ticker} map for a single concurrent batch
    all_tickers: dict[str, str] = {}
    for idx_name, stocks in CONSTITUENTS.items():
        for s in stocks:
            all_tickers[f"{idx_name}||{s['name']}"] = s["ticker"]

    log.info(f"  Fetching {len(all_tickers)} constituent prices + market caps...")

    # Concurrent fetch of price history AND market cap per stock
    raw: dict[str, tuple[Optional[dict], Optional[float]]] = {}

    def _work(compound_key: str, ticker: str):
        _, perf, cap = _fetch_constituent(compound_key, ticker)
        return compound_key, perf, cap

    with ThreadPoolExecutor(max_workers=16) as pool:
        futs = {pool.submit(_work, k, t): k for k, t in all_tickers.items()}
        for fut in as_completed(futs):
            try:
                key, perf, cap = fut.result()
                raw[key] = (perf, cap)
            except Exception as e:
                log.error(f"Constituent worker error: {e}")

    results: dict[str, dict] = {}
    for idx_name, stocks in CONSTITUENTS.items():
        entries = []
        for s in stocks:
            key        = f"{idx_name}||{s['name']}"
            perf, cap  = raw.get(key, (None, None))
            if perf and perf.get("1m_pct") is not None:
                entries.append({
                    "name":       s["name"],
                    "ticker":     s["ticker"],
                    "daily_pct":  perf.get("daily_pct"),
                    "1m_pct":     perf["1m_pct"],
                    "ytd_pct":    perf.get("ytd_pct"),
                    "cap":        cap,
                })

        # Compute cap weights; fall back to equal-weight if caps unavailable
        caps        = [e["cap"] for e in entries if e["cap"] and e["cap"] > 0]
        total_cap   = sum(caps) if caps else 0.0
        use_caps    = total_cap > 0 and len(caps) >= len(entries) // 2

        perf_list = []
        for e in entries:
            if use_caps and e["cap"] and e["cap"] > 0:
                weight = e["cap"] / total_cap
            else:
                weight = 1.0 / len(entries) if entries else 0.0
            contribution = round(weight * e["1m_pct"], 3)
            perf_list.append({
                "name":         e["name"],
                "1m_pct":       e["1m_pct"],
                "contribution": contribution,
                "weight":       round(weight * 100, 1),
            })

        perf_list.sort(key=lambda x: x["contribution"], reverse=True)

        # ── Sector aggregation (cap-weighted return per GICS Level 1 sector) ──
        sector_buckets: dict[str, dict] = {}
        for e in entries:
            sec = s_meta["sector"] if (s_meta := next(
                (s for s in stocks if s["name"] == e["name"]), None
            )) else "Unknown"
            b = sector_buckets.setdefault(sec, {
                "cap": 0.0, "wd": 0.0, "w1m": 0.0, "wytd": 0.0,
                "cap_d": 0.0, "cap_ytd": 0.0,
            })
            cap_i = e["cap"] if (e["cap"] and e["cap"] > 0 and use_caps) else (
                total_cap / len(entries) if total_cap else 1.0
            )
            b["cap"]  += cap_i
            b["w1m"]  += cap_i * e["1m_pct"]
            if e["daily_pct"] is not None:
                b["wd"]    += cap_i * e["daily_pct"]
                b["cap_d"] += cap_i
            if e["ytd_pct"] is not None:
                b["wytd"]    += cap_i * e["ytd_pct"]
                b["cap_ytd"] += cap_i

        sectors: dict[str, dict] = {}
        for sec, b in sector_buckets.items():
            if b["cap"] > 0:
                sectors[sec] = {
                    "daily_pct": round(b["wd"]   / b["cap_d"],   2) if b["cap_d"]   > 0 else None,
                    "1m_pct":    round(b["w1m"]  / b["cap"],     2),
                    "ytd_pct":   round(b["wytd"] / b["cap_ytd"], 2) if b["cap_ytd"] > 0 else None,
                    "weight":    round(b["cap"]  / (total_cap if total_cap else b["cap"]) * 100, 1),
                }

        results[idx_name] = {
            "top3":    perf_list[:3],
            "bottom3": perf_list[-3:] if len(perf_list) >= 3 else list(reversed(perf_list)),
            "sectors": sectors,
        }

    return results
