"""
Top ~20 constituents per APAC index for movers and sector analysis.
All individual stock tickers use Yahoo Finance format (.T, .HK, .SS, .SZ, .KS, .AX, .TW).
Ordered roughly by market-cap weight within each index.
Sector field uses GICS Level 1 classification.
"""

CONSTITUENTS: dict[str, list[dict]] = {

    # ── Japan ──────────────────────────────────────────────────────────────────
    # TOPIX is cap-weighted; Nikkei 225 is price-weighted — top names differ slightly.

    "Nikkei 225": [
        {"name": "Fast Retailing",   "ticker": "9983.T",  "sector": "Consumer Discretionary"},
        {"name": "Tokyo Electron",   "ticker": "8035.T",  "sector": "Information Technology"},
        {"name": "SoftBank Group",   "ticker": "9984.T",  "sector": "Communication Services"},
        {"name": "Keyence",          "ticker": "6861.T",  "sector": "Information Technology"},
        {"name": "Fanuc",            "ticker": "6954.T",  "sector": "Industrials"},
        {"name": "Sony Group",       "ticker": "6758.T",  "sector": "Consumer Discretionary"},
        {"name": "Shin-Etsu Chem",   "ticker": "4063.T",  "sector": "Materials"},
        {"name": "KDDI",             "ticker": "9433.T",  "sector": "Communication Services"},
        {"name": "Toyota Motor",     "ticker": "7203.T",  "sector": "Consumer Discretionary"},
        {"name": "Mitsubishi UFJ",   "ticker": "8306.T",  "sector": "Financials"},
        {"name": "Recruit Holdings", "ticker": "6098.T",  "sector": "Industrials"},
        {"name": "Daiichi Sankyo",   "ticker": "4568.T",  "sector": "Health Care"},
        {"name": "Advantest",        "ticker": "6857.T",  "sector": "Information Technology"},
        {"name": "Disco",            "ticker": "6146.T",  "sector": "Information Technology"},
        {"name": "Hitachi",          "ticker": "6501.T",  "sector": "Industrials"},
        {"name": "Nintendo",         "ticker": "7974.T",  "sector": "Communication Services"},
        {"name": "Honda Motor",      "ticker": "7267.T",  "sector": "Consumer Discretionary"},
        {"name": "Murata Mfg",       "ticker": "6981.T",  "sector": "Information Technology"},
        {"name": "Terumo",           "ticker": "4543.T",  "sector": "Health Care"},
        {"name": "Olympus",          "ticker": "7733.T",  "sector": "Health Care"},
    ],

    "TOPIX": [
        {"name": "Toyota Motor",     "ticker": "7203.T",  "sector": "Consumer Discretionary"},
        {"name": "Sony Group",       "ticker": "6758.T",  "sector": "Consumer Discretionary"},
        {"name": "Keyence",          "ticker": "6861.T",  "sector": "Information Technology"},
        {"name": "Mitsubishi UFJ",   "ticker": "8306.T",  "sector": "Financials"},
        {"name": "Recruit Holdings", "ticker": "6098.T",  "sector": "Industrials"},
        {"name": "SoftBank Group",   "ticker": "9984.T",  "sector": "Communication Services"},
        {"name": "Fast Retailing",   "ticker": "9983.T",  "sector": "Consumer Discretionary"},
        {"name": "Tokyo Electron",   "ticker": "8035.T",  "sector": "Information Technology"},
        {"name": "Shin-Etsu Chem",   "ticker": "4063.T",  "sector": "Materials"},
        {"name": "NTT",              "ticker": "9432.T",  "sector": "Communication Services"},
        {"name": "Sumitomo MUFG",    "ticker": "8316.T",  "sector": "Financials"},
        {"name": "Hitachi",          "ticker": "6501.T",  "sector": "Industrials"},
        {"name": "KDDI",             "ticker": "9433.T",  "sector": "Communication Services"},
        {"name": "Honda Motor",      "ticker": "7267.T",  "sector": "Consumer Discretionary"},
        {"name": "Daiichi Sankyo",   "ticker": "4568.T",  "sector": "Health Care"},
        {"name": "Fanuc",            "ticker": "6954.T",  "sector": "Industrials"},
        {"name": "Mizuho Financial", "ticker": "8411.T",  "sector": "Financials"},
        {"name": "Nomura Holdings",  "ticker": "8604.T",  "sector": "Financials"},
        {"name": "Nintendo",         "ticker": "7974.T",  "sector": "Communication Services"},
        {"name": "Murata Mfg",       "ticker": "6981.T",  "sector": "Information Technology"},
    ],

    # ── China ──────────────────────────────────────────────────────────────────

    "CSI 300": [
        {"name": "Kweichow Moutai",  "ticker": "600519.SS", "sector": "Consumer Staples"},
        {"name": "CATL",             "ticker": "300750.SZ", "sector": "Industrials"},
        {"name": "BYD",              "ticker": "002594.SZ", "sector": "Consumer Discretionary"},
        {"name": "China Merch. Bank","ticker": "600036.SS", "sector": "Financials"},
        {"name": "Ping An Insurance","ticker": "601318.SS", "sector": "Financials"},
        {"name": "LONGi Green",      "ticker": "601012.SS", "sector": "Information Technology"},
        {"name": "ICBC",             "ticker": "601398.SS", "sector": "Financials"},
        {"name": "China Const. Bank","ticker": "601939.SS", "sector": "Financials"},
        {"name": "Wuliangye",        "ticker": "000858.SZ", "sector": "Consumer Staples"},
        {"name": "Midea Group",      "ticker": "000333.SZ", "sector": "Consumer Discretionary"},
        {"name": "Zijin Mining",     "ticker": "601899.SS", "sector": "Materials"},
        {"name": "Agri. Bank China", "ticker": "601288.SS", "sector": "Financials"},
        {"name": "Yangtze Power",    "ticker": "600900.SS", "sector": "Utilities"},
        {"name": "Luxshare",         "ticker": "002475.SZ", "sector": "Information Technology"},
        {"name": "Sungrow Power",    "ticker": "300274.SZ", "sector": "Industrials"},
        {"name": "Jiangsu Hengrui",  "ticker": "600276.SS", "sector": "Health Care"},
        {"name": "China Life",       "ticker": "601628.SS", "sector": "Financials"},
        {"name": "Haier Smart Home", "ticker": "600690.SS", "sector": "Consumer Discretionary"},
        {"name": "CNOOC",            "ticker": "600938.SS", "sector": "Energy"},
        {"name": "Bank of Comms",    "ticker": "601328.SS", "sector": "Financials"},
    ],

    "Shanghai Comp": [
        {"name": "Kweichow Moutai",  "ticker": "600519.SS", "sector": "Consumer Staples"},
        {"name": "ICBC",             "ticker": "601398.SS", "sector": "Financials"},
        {"name": "China Const. Bank","ticker": "601939.SS", "sector": "Financials"},
        {"name": "Ping An Insurance","ticker": "601318.SS", "sector": "Financials"},
        {"name": "Agri. Bank China", "ticker": "601288.SS", "sector": "Financials"},
        {"name": "Bank of China",    "ticker": "601988.SS", "sector": "Financials"},
        {"name": "Yangtze Power",    "ticker": "600900.SS", "sector": "Utilities"},
        {"name": "CNOOC",            "ticker": "600938.SS", "sector": "Energy"},
        {"name": "LONGi Green",      "ticker": "601012.SS", "sector": "Information Technology"},
        {"name": "China Life",       "ticker": "601628.SS", "sector": "Financials"},
        {"name": "China Merch. Bank","ticker": "600036.SS", "sector": "Financials"},
        {"name": "Zijin Mining",     "ticker": "601899.SS", "sector": "Materials"},
        {"name": "Jiangsu Hengrui",  "ticker": "600276.SS", "sector": "Health Care"},
        {"name": "China Pacific Ins","ticker": "601601.SS", "sector": "Financials"},
        {"name": "China Shenhua",    "ticker": "601088.SS", "sector": "Energy"},
        {"name": "Haier Smart Home", "ticker": "600690.SS", "sector": "Consumer Discretionary"},
        {"name": "China Railway",    "ticker": "601390.SS", "sector": "Industrials"},
        {"name": "Bank of Comms",    "ticker": "601328.SS", "sector": "Financials"},
    ],

    # ── Hong Kong ──────────────────────────────────────────────────────────────

    "Hang Seng": [
        {"name": "HSBC",             "ticker": "0005.HK",  "sector": "Financials"},
        {"name": "AIA Group",        "ticker": "1299.HK",  "sector": "Financials"},
        {"name": "Tencent",          "ticker": "0700.HK",  "sector": "Communication Services"},
        {"name": "Alibaba",          "ticker": "9988.HK",  "sector": "Consumer Discretionary"},
        {"name": "BYD",              "ticker": "1211.HK",  "sector": "Consumer Discretionary"},
        {"name": "Xiaomi",           "ticker": "1810.HK",  "sector": "Information Technology"},
        {"name": "Meituan",          "ticker": "3690.HK",  "sector": "Consumer Discretionary"},
        {"name": "China Const. Bank","ticker": "0939.HK",  "sector": "Financials"},
        {"name": "CNOOC",            "ticker": "0883.HK",  "sector": "Energy"},
        {"name": "ICBC",             "ticker": "1398.HK",  "sector": "Financials"},
        {"name": "Bank of China",    "ticker": "3988.HK",  "sector": "Financials"},
        {"name": "Ping An Insurance","ticker": "2318.HK",  "sector": "Financials"},
        {"name": "Sun Hung Kai",     "ticker": "0016.HK",  "sector": "Real Estate"},
        {"name": "Link REIT",        "ticker": "0823.HK",  "sector": "Real Estate"},
        {"name": "CK Hutchison",     "ticker": "0001.HK",  "sector": "Industrials"},
        {"name": "BOC Hong Kong",    "ticker": "2388.HK",  "sector": "Financials"},
        {"name": "China Life",       "ticker": "2628.HK",  "sector": "Financials"},
        {"name": "Galaxy Entertain.","ticker": "0027.HK",  "sector": "Consumer Discretionary"},
    ],

    # ── South Korea ────────────────────────────────────────────────────────────

    "KOSPI": [
        {"name": "Samsung Elec.",    "ticker": "005930.KS", "sector": "Information Technology"},
        {"name": "SK Hynix",         "ticker": "000660.KS", "sector": "Information Technology"},
        {"name": "LG Energy Sol.",   "ticker": "373220.KS", "sector": "Industrials"},
        {"name": "Samsung SDI",      "ticker": "006400.KS", "sector": "Industrials"},
        {"name": "Hyundai Motor",    "ticker": "005380.KS", "sector": "Consumer Discretionary"},
        {"name": "Kia",              "ticker": "000270.KS", "sector": "Consumer Discretionary"},
        {"name": "POSCO Holdings",   "ticker": "005490.KS", "sector": "Materials"},
        {"name": "Celltrion",        "ticker": "068270.KS", "sector": "Health Care"},
        {"name": "Kakao",            "ticker": "035720.KS", "sector": "Communication Services"},
        {"name": "NAVER",            "ticker": "035420.KS", "sector": "Communication Services"},
        {"name": "KB Financial",     "ticker": "105560.KS", "sector": "Financials"},
        {"name": "Shinhan Financial","ticker": "055550.KS", "sector": "Financials"},
        {"name": "Samsung Bio",      "ticker": "207940.KS", "sector": "Health Care"},
        {"name": "LG Chem",          "ticker": "051910.KS", "sector": "Materials"},
        {"name": "SK Telecom",       "ticker": "017670.KS", "sector": "Communication Services"},
    ],

    # ── Australia ──────────────────────────────────────────────────────────────

    "ASX 200": [
        {"name": "BHP Group",        "ticker": "BHP.AX",  "sector": "Materials"},
        {"name": "Commonwealth Bank","ticker": "CBA.AX",  "sector": "Financials"},
        {"name": "CSL",              "ticker": "CSL.AX",  "sector": "Health Care"},
        {"name": "ANZ",              "ticker": "ANZ.AX",  "sector": "Financials"},
        {"name": "Westpac",          "ticker": "WBC.AX",  "sector": "Financials"},
        {"name": "NAB",              "ticker": "NAB.AX",  "sector": "Financials"},
        {"name": "Macquarie Group",  "ticker": "MQG.AX",  "sector": "Financials"},
        {"name": "Fortescue",        "ticker": "FMG.AX",  "sector": "Materials"},
        {"name": "Wesfarmers",       "ticker": "WES.AX",  "sector": "Consumer Discretionary"},
        {"name": "Rio Tinto",        "ticker": "RIO.AX",  "sector": "Materials"},
        {"name": "Woodside Energy",  "ticker": "WDS.AX",  "sector": "Energy"},
        {"name": "Goodman Group",    "ticker": "GMG.AX",  "sector": "Real Estate"},
        {"name": "Transurban",       "ticker": "TCL.AX",  "sector": "Industrials"},
        {"name": "Telstra",          "ticker": "TLS.AX",  "sector": "Communication Services"},
        {"name": "Aristocrat",       "ticker": "ALL.AX",  "sector": "Consumer Discretionary"},
        {"name": "Santos",           "ticker": "STO.AX",  "sector": "Energy"},
        {"name": "REA Group",        "ticker": "REA.AX",  "sector": "Communication Services"},
        {"name": "Wisetech",         "ticker": "WTC.AX",  "sector": "Information Technology"},
    ],

    # ── Taiwan ─────────────────────────────────────────────────────────────────

    "TAIEX": [
        {"name": "TSMC",             "ticker": "2330.TW", "sector": "Information Technology"},
        {"name": "Hon Hai",          "ticker": "2317.TW", "sector": "Information Technology"},
        {"name": "MediaTek",         "ticker": "2454.TW", "sector": "Information Technology"},
        {"name": "Delta Electronics","ticker": "2308.TW", "sector": "Information Technology"},
        {"name": "UMC",              "ticker": "2303.TW", "sector": "Information Technology"},
        {"name": "Largan Precision", "ticker": "3008.TW", "sector": "Information Technology"},
        {"name": "ASE Technology",   "ticker": "3711.TW", "sector": "Information Technology"},
        {"name": "Formosa Plastics", "ticker": "1301.TW", "sector": "Materials"},
        {"name": "Cathay Financial", "ticker": "2882.TW", "sector": "Financials"},
        {"name": "Fubon Financial",  "ticker": "2881.TW", "sector": "Financials"},
        {"name": "Chunghwa Telecom", "ticker": "2412.TW", "sector": "Communication Services"},
        {"name": "Mega Financial",   "ticker": "2886.TW", "sector": "Financials"},
        {"name": "Novatek",          "ticker": "3034.TW", "sector": "Information Technology"},
        {"name": "Catcher Tech",     "ticker": "2474.TW", "sector": "Information Technology"},
        {"name": "Wiwynn",           "ticker": "6669.TW", "sector": "Information Technology"},
    ],
}
