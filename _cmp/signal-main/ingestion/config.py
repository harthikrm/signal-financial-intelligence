import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# ── Date Range ─────────────────────────────────────────────────────────────
DATE_FROM = "2021-05-01"
DATE_TO   = datetime.today().strftime("%Y-%m-%d")

# Weight recent periods highest in all queries
PERIOD_PREFERENCE = {
    "annual_priority":    ["2025", "2024", "2023", "2022", "2021"],
    "quarterly_priority": ["2026-Q1", "2025-Q4", "2025-Q3", "2025-Q2",
                           "2025-Q1", "2024-Q4", "2024-Q3"],
    "weight_recent_years": True,
}

# ── 70 Companies ───────────────────────────────────────────────────────────
COMPANIES = [
    # AI & Semiconductors
    {"ticker": "NVDA",  "name": "NVIDIA Corporation",          "sector": "AI & Semiconductors",    "exchange": "NASDAQ", "cik": "0001045810"},
    {"ticker": "AMD",   "name": "Advanced Micro Devices",      "sector": "AI & Semiconductors",    "exchange": "NASDAQ", "cik": "0000002488"},
    {"ticker": "INTC",  "name": "Intel Corporation",           "sector": "AI & Semiconductors",    "exchange": "NASDAQ", "cik": "0000050863"},
    {"ticker": "QCOM",  "name": "QUALCOMM Incorporated",       "sector": "AI & Semiconductors",    "exchange": "NASDAQ", "cik": "0000804328"},
    {"ticker": "AVGO",  "name": "Broadcom Inc.",               "sector": "AI & Semiconductors",    "exchange": "NASDAQ", "cik": "0001730168"},
    {"ticker": "MU",    "name": "Micron Technology",           "sector": "AI & Semiconductors",    "exchange": "NASDAQ", "cik": "0000723125"},
    {"ticker": "AMAT",  "name": "Applied Materials",           "sector": "AI & Semiconductors",    "exchange": "NASDAQ", "cik": "0000796343"},
    # Cloud & Infrastructure
    {"ticker": "AMZN",  "name": "Amazon.com",                  "sector": "Cloud & Infrastructure", "exchange": "NASDAQ", "cik": "0001018724"},
    {"ticker": "MSFT",  "name": "Microsoft Corporation",       "sector": "Cloud & Infrastructure", "exchange": "NASDAQ", "cik": "0000789019"},
    {"ticker": "GOOGL", "name": "Alphabet Inc.",               "sector": "Cloud & Infrastructure", "exchange": "NASDAQ", "cik": "0001652044"},
    {"ticker": "ORCL",  "name": "Oracle Corporation",          "sector": "Cloud & Infrastructure", "exchange": "NYSE",   "cik": "0001341439"},
    {"ticker": "CRM",   "name": "Salesforce",                  "sector": "Cloud & Infrastructure", "exchange": "NYSE",   "cik": "0001108524"},
    {"ticker": "NOW",   "name": "ServiceNow",                  "sector": "Cloud & Infrastructure", "exchange": "NYSE",   "cik": "0001373715"},
    {"ticker": "NET",   "name": "Cloudflare",                  "sector": "Cloud & Infrastructure", "exchange": "NYSE",   "cik": "0001477333"},
    # Cybersecurity
    {"ticker": "CRWD",  "name": "CrowdStrike",                 "sector": "Cybersecurity",          "exchange": "NASDAQ", "cik": "0001535527"},
    {"ticker": "PANW",  "name": "Palo Alto Networks",          "sector": "Cybersecurity",          "exchange": "NASDAQ", "cik": "0001327567"},
    {"ticker": "FTNT",  "name": "Fortinet",                    "sector": "Cybersecurity",          "exchange": "NASDAQ", "cik": "0001262039"},
    {"ticker": "ZS",    "name": "Zscaler",                     "sector": "Cybersecurity",          "exchange": "NASDAQ", "cik": "0001713683"},
    {"ticker": "S",     "name": "SentinelOne",                 "sector": "Cybersecurity",          "exchange": "NYSE",   "cik": "0001816812"},
    {"ticker": "OKTA",  "name": "Okta",                        "sector": "Cybersecurity",          "exchange": "NASDAQ", "cik": "0001660134"},
    {"ticker": "TENB",  "name": "Tenable Holdings",            "sector": "Cybersecurity",          "exchange": "NASDAQ", "cik": "0001660280"},
    # Electric Vehicles & Energy
    {"ticker": "TSLA",  "name": "Tesla",                       "sector": "EV & Energy",            "exchange": "NASDAQ", "cik": "0001318605"},
    {"ticker": "GM",    "name": "General Motors",              "sector": "EV & Energy",            "exchange": "NYSE",   "cik": "0001467858"},
    {"ticker": "F",     "name": "Ford Motor Company",          "sector": "EV & Energy",            "exchange": "NYSE",   "cik": "0000037996"},
    {"ticker": "RIVN",  "name": "Rivian Automotive",           "sector": "EV & Energy",            "exchange": "NASDAQ", "cik": "0001874178"},
    {"ticker": "NEE",   "name": "NextEra Energy",              "sector": "EV & Energy",            "exchange": "NYSE",   "cik": "0000753308"},
    {"ticker": "ENPH", "name": "Enphase Energy",               "sector": "EV & Energy",            "exchange": "NASDAQ", "cik": "0001463101"},
    {"ticker": "FSLR",  "name": "First Solar",                 "sector": "EV & Energy",            "exchange": "NASDAQ", "cik": "0001274494"},
    # Financial Technology
    {"ticker": "V",     "name": "Visa Inc.",                   "sector": "FinTech",                "exchange": "NYSE",   "cik": "0001403161"},
    {"ticker": "MA",    "name": "Mastercard",                  "sector": "FinTech",                "exchange": "NYSE",   "cik": "0001141391"},
    {"ticker": "PYPL",  "name": "PayPal",                      "sector": "FinTech",                "exchange": "NASDAQ", "cik": "0001633917"},
    {"ticker": "SQ",    "name": "Block (Square)",              "sector": "FinTech",                "exchange": "NYSE",   "cik": "0001512673"},
    {"ticker": "AFRM",  "name": "Affirm Holdings",             "sector": "FinTech",                "exchange": "NASDAQ", "cik": "0001820953"},
    {"ticker": "HOOD",  "name": "Robinhood",                   "sector": "FinTech",                "exchange": "NASDAQ", "cik": "0001783879"},
    {"ticker": "COIN",  "name": "Coinbase",                    "sector": "FinTech",                "exchange": "NASDAQ", "cik": "0001679788"},
    # Biotech & Genomics
    {"ticker": "MRNA",  "name": "Moderna",                     "sector": "Biotech & Genomics",     "exchange": "NASDAQ", "cik": "0001682852"},
    {"ticker": "BNTX",  "name": "BioNTech",                    "sector": "Biotech & Genomics",     "exchange": "NASDAQ", "cik": "0001776197"},
    {"ticker": "ILMN",  "name": "Illumina",                    "sector": "Biotech & Genomics",     "exchange": "NASDAQ", "cik": "0001110803"},
    {"ticker": "VRTX",  "name": "Vertex Pharmaceuticals",      "sector": "Biotech & Genomics",     "exchange": "NASDAQ", "cik": "0000875320"},
    {"ticker": "REGN",  "name": "Regeneron Pharmaceuticals",   "sector": "Biotech & Genomics",     "exchange": "NASDAQ", "cik": "0000872589"},
    {"ticker": "ALNY",  "name": "Alnylam Pharmaceuticals",     "sector": "Biotech & Genomics",     "exchange": "NASDAQ", "cik": "0001178670"},
    {"ticker": "BIIB",  "name": "Biogen",                      "sector": "Biotech & Genomics",     "exchange": "NASDAQ", "cik": "0000875045"},
    # Space & Defense
    {"ticker": "LMT",   "name": "Lockheed Martin",             "sector": "Space & Defense",        "exchange": "NYSE",   "cik": "0000936468"},
    {"ticker": "RTX",   "name": "RTX Corporation",             "sector": "Space & Defense",        "exchange": "NYSE",   "cik": "0000101830"},
    {"ticker": "NOC",   "name": "Northrop Grumman",            "sector": "Space & Defense",        "exchange": "NYSE",   "cik": "0001133421"},
    {"ticker": "LHX",   "name": "L3Harris Technologies",       "sector": "Space & Defense",        "exchange": "NYSE",   "cik": "0000202058"},
    {"ticker": "RKLB",  "name": "Rocket Lab USA",              "sector": "Space & Defense",        "exchange": "NASDAQ", "cik": "0001819989"},
    {"ticker": "TDG",   "name": "TransDigm Group",             "sector": "Space & Defense",        "exchange": "NYSE",   "cik": "0001260221"},
    {"ticker": "HEI",   "name": "HEICO Corporation",           "sector": "Space & Defense",        "exchange": "NYSE",   "cik": "0000046619"},
    # Consumer & Retail
    {"ticker": "WMT",   "name": "Walmart",                     "sector": "Consumer & Retail",      "exchange": "NYSE",   "cik": "0000104169"},
    {"ticker": "TGT",   "name": "Target",                      "sector": "Consumer & Retail",      "exchange": "NYSE",   "cik": "0000027419"},
    {"ticker": "COST",  "name": "Costco",                      "sector": "Consumer & Retail",      "exchange": "NASDAQ", "cik": "0000909832"},
    {"ticker": "SHOP",  "name": "Shopify",                     "sector": "Consumer & Retail",      "exchange": "NYSE",   "cik": "0001594805"},
    {"ticker": "MELI",  "name": "MercadoLibre",                "sector": "Consumer & Retail",      "exchange": "NASDAQ", "cik": "0001099590"},
    {"ticker": "DG",    "name": "Dollar General",              "sector": "Consumer & Retail",      "exchange": "NYSE",   "cik": "0000029534"},
    {"ticker": "HD",    "name": "Home Depot",                  "sector": "Consumer & Retail",      "exchange": "NYSE",   "cik": "0000354950"},
    # Media & Streaming
    {"ticker": "NFLX",  "name": "Netflix",                     "sector": "Media & Streaming",      "exchange": "NASDAQ", "cik": "0001065280"},
    {"ticker": "DIS",   "name": "Walt Disney",                 "sector": "Media & Streaming",      "exchange": "NYSE",   "cik": "0001001039"},
    {"ticker": "PARA",  "name": "Paramount Global",            "sector": "Media & Streaming",      "exchange": "NASDAQ", "cik": "0000813828"},
    {"ticker": "WBD",   "name": "Warner Bros. Discovery",      "sector": "Media & Streaming",      "exchange": "NASDAQ", "cik": "0000049196"},
    {"ticker": "SPOT",  "name": "Spotify",                     "sector": "Media & Streaming",      "exchange": "NYSE",   "cik": "0001639920"},
    {"ticker": "LYV",   "name": "Live Nation Entertainment",   "sector": "Media & Streaming",      "exchange": "NYSE",   "cik": "0001335258"},
    {"ticker": "IHRT",  "name": "iHeartMedia",                 "sector": "Media & Streaming",      "exchange": "NASDAQ", "cik": "0001400891"},
    # Traditional Finance
    {"ticker": "JPM",   "name": "JPMorgan Chase",              "sector": "Traditional Finance",    "exchange": "NYSE",   "cik": "0000019617"},
    {"ticker": "GS",    "name": "Goldman Sachs",               "sector": "Traditional Finance",    "exchange": "NYSE",   "cik": "0000886982"},
    {"ticker": "BLK",   "name": "BlackRock",                   "sector": "Traditional Finance",    "exchange": "NYSE",   "cik": "0001364742"},
    {"ticker": "MS",    "name": "Morgan Stanley",              "sector": "Traditional Finance",    "exchange": "NYSE",   "cik": "0000895421"},
    {"ticker": "NDAQ",  "name": "Nasdaq Inc.",                 "sector": "Traditional Finance",    "exchange": "NASDAQ", "cik": "0001120193"},
    {"ticker": "SCHW",  "name": "Charles Schwab",              "sector": "Traditional Finance",    "exchange": "NYSE",   "cik": "0000316888"},
    {"ticker": "BRK.B", "name": "Berkshire Hathaway",          "sector": "Traditional Finance",    "exchange": "NYSE",   "cik": "0001067983"},
]

TICKERS = [c["ticker"] for c in COMPANIES]

# Logos are served by Logo.dev using ticker symbols directly.
# URL format: https://img.logo.dev/ticker/{TICKER}?token={TOKEN}
# No domain mapping needed. Token stored in LOGO_DEV_TOKEN env var.

# ── TradingView Symbol Map ─────────────────────────────────────────────────
TRADINGVIEW_SYMBOLS = {c["ticker"]: f"{c['exchange']}:{c['ticker']}"
                       for c in COMPANIES}
# Special case
TRADINGVIEW_SYMBOLS["BRK.B"] = "NYSE:BRK.B"

# ── Financial Company XBRL Overrides ──────────────────────────────────────
FINANCIAL_COMPANIES = ["JPM", "GS", "MS", "BLK", "SCHW", "BRK.B"]

XBRL_OVERRIDES = {
    "JPM":   {"revenue": ["InterestAndDividendIncomeOperating",
                           "RevenuesNetOfInterestExpense"]},
    "GS":    {"revenue": ["RevenuesNetOfInterestExpense"]},
    "MS":    {"revenue": ["RevenuesNetOfInterestExpense"]},
    "BLK":   {"revenue": ["RevenueFromContractWithCustomerExcludingAssessedTax",
                           "Revenues"]},
    "SCHW":  {"revenue": ["InterestAndDividendIncomeOperating"]},
    "BRK.B": {"revenue": ["Revenues",
                           "RevenueFromContractWithCustomerExcludingAssessedTax"]},
}

# ── XBRL Fallback Chains ───────────────────────────────────────────────────
XBRL_FALLBACK_CHAINS = {
    "revenue": [
        "Revenues",
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "RevenueFromContractWithCustomerIncludingAssessedTax",
        "SalesRevenueNet",
        "SalesRevenueGoodsNet",
        "RevenueFromContractWithCustomer",
        "InterestAndDividendIncomeOperating",
        "RevenuesNetOfInterestExpense",
    ],
    "gross_profit": ["GrossProfit", "GrossProfitLoss"],
    "operating_income": [
        "OperatingIncomeLoss",
        "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
    ],
    "net_income": [
        "NetIncomeLoss",
        "NetIncomeLossAvailableToCommonStockholdersBasic",
        "ProfitLoss",
    ],
    "rd_expense": [
        "ResearchAndDevelopmentExpense",
        "ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost",
    ],
    "capex": [
        "PaymentsToAcquirePropertyPlantAndEquipment",
        "CapitalExpendituresIncurredButNotYetPaid",
        "PaymentsForCapitalImprovements",
    ],
    "operating_cash_flow": [
        "NetCashProvidedByUsedInOperatingActivities",
        "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations",
    ],
    "total_assets": ["Assets", "AssetsNet"],
    "current_assets": ["AssetsCurrent"],
    "total_liabilities": ["Liabilities"],
    "current_liabilities": ["LiabilitiesCurrent"],
    "total_equity": [
        "StockholdersEquity",
        "StockholdersEquityAttributableToParent",
        "PartnersCapital",
    ],
    "cash": [
        "CashAndCashEquivalentsAtCarryingValue",
        "CashCashEquivalentsAndShortTermInvestments",
    ],
    "total_debt": [
        "LongTermDebt",
        "LongTermDebtAndCapitalLeaseObligations",
        "DebtAndCapitalLeaseObligations",
    ],
    "short_term_debt": [
        "ShortTermBorrowings",
        "DebtCurrent",
        "LongTermDebtCurrent",
    ],
    "shares_outstanding": [
        "WeightedAverageNumberOfSharesOutstandingBasic",
        "CommonStockSharesOutstanding",
    ],
    "eps_basic": ["EarningsPerShareBasic"],
    "eps_diluted": ["EarningsPerShareDiluted"],
    "interest_expense": [
        "InterestExpense",
        "InterestAndDebtExpense",
    ],
    "income_tax_expense": ["IncomeTaxExpenseBenefit"],
    "depreciation_amortization": [
        "DepreciationDepletionAndAmortization",
        "DepreciationAndAmortization",
    ],
}

# ── Rate Limiting ──────────────────────────────────────────────────────────
EDGAR_RATE_LIMIT_SLEEP  = 0.1   # 10 req/sec max
POLYGON_RATE_LIMIT_SLEEP = 12.0  # 5 req/min max (free tier)

# ── SEC EDGAR Headers (Rule-3 amendment 2026-05-13) ────────────────────────
# - User-Agent email read from EDGAR_USER_AGENT_EMAIL env var (was hardcoded)
# - Host header removed; requests auto-sets it per URL, and we now hit both
#   data.sec.gov and www.sec.gov (see edgar_client.py BROWSE_URL split)
EDGAR_HEADERS = {
    "User-Agent": f"Signal/1.0 ({os.getenv('EDGAR_USER_AGENT_EMAIL', 'harthikmallichetty@gmail.com')})",
    "Accept-Encoding": "gzip, deflate",
}

# ── Chunking ───────────────────────────────────────────────────────────────
CHUNK_SIZE_TOKENS    = 512
CHUNK_OVERLAP_TOKENS = 50
MAX_CHUNK_K          = 7
DEFAULT_CHUNK_K      = 5

# ── LLM (Rule-3 amendment 2026-05-13 — env-driven, see plan amendments log) ──
LLM_MAX_TOKENS       = 1500
LLM_MODEL_PRODUCTION = os.getenv("LLM_MODEL_PRODUCTION", "gpt-4o-mini")
LLM_MODEL_LOCAL      = os.getenv("LLM_MODEL_LOCAL", "ollama/llama3")
