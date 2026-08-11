export type MetricCategory =
  | "Profitability"
  | "Growth"
  | "Efficiency"
  | "Liquidity"
  | "Cash Flow"
  | "Valuation"
  | "Price";

export interface MetricDefinition {
  key: string;
  label: string;
  category: MetricCategory;
  unit: string;
  description: string;
}

export const METRICS: MetricDefinition[] = [
  {
    "key": "revenue",
    "label": "Revenue",
    "category": "Growth",
    "unit": "$",
    "description": "Total company sales for the period."
  },
  {
    "key": "gross_profit",
    "label": "Gross profit",
    "category": "Profitability",
    "unit": "$",
    "description": "Revenue minus cost of goods sold."
  },
  {
    "key": "operating_income",
    "label": "Operating income",
    "category": "Profitability",
    "unit": "$",
    "description": "Profit from core operations before interest and taxes."
  },
  {
    "key": "net_income",
    "label": "Net income",
    "category": "Profitability",
    "unit": "$",
    "description": "Bottom-line profit after all expenses and taxes."
  },
  {
    "key": "gross_margin",
    "label": "Gross margin",
    "category": "Profitability",
    "unit": "%",
    "description": "Gross profit as a percent of revenue."
  },
  {
    "key": "operating_margin",
    "label": "Operating margin",
    "category": "Profitability",
    "unit": "%",
    "description": "Operating income as a percent of revenue."
  },
  {
    "key": "net_margin",
    "label": "Net margin",
    "category": "Profitability",
    "unit": "%",
    "description": "Net income as a percent of revenue."
  },
  {
    "key": "revenue_growth",
    "label": "Revenue growth",
    "category": "Growth",
    "unit": "%",
    "description": "Year-over-year change in revenue."
  },
  {
    "key": "revenue_ttm",
    "label": "Revenue (TTM)",
    "category": "Growth",
    "unit": "$",
    "description": "Trailing twelve months revenue sum."
  },
  {
    "key": "gross_profit_ttm",
    "label": "Gross profit (TTM)",
    "category": "Growth",
    "unit": "$",
    "description": "Trailing twelve months gross profit."
  },
  {
    "key": "net_income_ttm",
    "label": "Net income (TTM)",
    "category": "Growth",
    "unit": "$",
    "description": "Trailing twelve months net income."
  },
  {
    "key": "fcf_ttm",
    "label": "Free cash flow (TTM)",
    "category": "Cash Flow",
    "unit": "$",
    "description": "Trailing twelve months free cash flow."
  },
  {
    "key": "gross_margin_ttm",
    "label": "Gross margin (TTM)",
    "category": "Profitability",
    "unit": "%",
    "description": "TTM gross profit divided by TTM revenue."
  },
  {
    "key": "net_margin_ttm",
    "label": "Net margin (TTM)",
    "category": "Profitability",
    "unit": "%",
    "description": "TTM net income divided by TTM revenue."
  },
  {
    "key": "fcf_margin_ttm",
    "label": "FCF margin (TTM)",
    "category": "Cash Flow",
    "unit": "%",
    "description": "TTM free cash flow divided by TTM revenue."
  },
  {
    "key": "ebitda",
    "label": "EBITDA",
    "category": "Profitability",
    "unit": "$",
    "description": "Earnings before interest, taxes, depreciation and amortization proxy."
  },
  {
    "key": "free_cash_flow",
    "label": "Free cash flow",
    "category": "Cash Flow",
    "unit": "$",
    "description": "Operating cash flow minus capital expenditures."
  },
  {
    "key": "operating_cash_flow",
    "label": "Operating cash flow",
    "category": "Cash Flow",
    "unit": "$",
    "description": "Cash generated from operating activities."
  },
  {
    "key": "capex",
    "label": "Capital expenditures",
    "category": "Cash Flow",
    "unit": "$",
    "description": "Cash spent on property, plant, and equipment."
  },
  {
    "key": "rd_expense",
    "label": "R&D expense",
    "category": "Efficiency",
    "unit": "$",
    "description": "Research and development spending."
  },
  {
    "key": "roe",
    "label": "Return on equity",
    "category": "Profitability",
    "unit": "%",
    "description": "Net income divided by shareholders equity."
  },
  {
    "key": "roa",
    "label": "Return on assets",
    "category": "Profitability",
    "unit": "%",
    "description": "Net income divided by total assets."
  },
  {
    "key": "asset_turnover",
    "label": "Asset turnover",
    "category": "Efficiency",
    "unit": "x",
    "description": "Revenue divided by average total assets."
  },
  {
    "key": "interest_coverage",
    "label": "Interest coverage",
    "category": "Liquidity",
    "unit": "x",
    "description": "Operating income divided by interest expense."
  },
  {
    "key": "current_ratio",
    "label": "Current ratio",
    "category": "Liquidity",
    "unit": "x",
    "description": "Current assets divided by current liabilities."
  },
  {
    "key": "debt_to_equity",
    "label": "Debt to equity",
    "category": "Liquidity",
    "unit": "x",
    "description": "Total debt divided by total equity."
  },
  {
    "key": "net_debt",
    "label": "Net debt",
    "category": "Liquidity",
    "unit": "$",
    "description": "Total debt minus cash and equivalents."
  },
  {
    "key": "total_assets",
    "label": "Total assets",
    "category": "Liquidity",
    "unit": "$",
    "description": "Sum of resources owned by the company."
  },
  {
    "key": "current_assets",
    "label": "Current assets",
    "category": "Liquidity",
    "unit": "$",
    "description": "Assets expected to convert to cash within a year."
  },
  {
    "key": "total_liabilities",
    "label": "Total liabilities",
    "category": "Liquidity",
    "unit": "$",
    "description": "Obligations owed to creditors."
  },
  {
    "key": "current_liabilities",
    "label": "Current liabilities",
    "category": "Liquidity",
    "unit": "$",
    "description": "Obligations due within a year."
  },
  {
    "key": "total_equity",
    "label": "Total equity",
    "category": "Liquidity",
    "unit": "$",
    "description": "Shareholders residual claim on assets."
  },
  {
    "key": "cash",
    "label": "Cash & equivalents",
    "category": "Liquidity",
    "unit": "$",
    "description": "Cash and short-term liquid investments."
  },
  {
    "key": "total_debt",
    "label": "Total debt",
    "category": "Liquidity",
    "unit": "$",
    "description": "Interest-bearing obligations."
  },
  {
    "key": "shares_outstanding",
    "label": "Shares outstanding",
    "category": "Valuation",
    "unit": "",
    "description": "Common shares issued and outstanding."
  },
  {
    "key": "eps_diluted",
    "label": "EPS (diluted)",
    "category": "Valuation",
    "unit": "$",
    "description": "Net income per diluted share."
  },
  {
    "key": "interest_expense",
    "label": "Interest expense",
    "category": "Cash Flow",
    "unit": "$",
    "description": "Cost of borrowed funds."
  },
  {
    "key": "da",
    "label": "D&A",
    "category": "Cash Flow",
    "unit": "$",
    "description": "Depreciation and amortization add-back for EBITDA bridge."
  },
  {
    "key": "prior_revenue",
    "label": "Prior period revenue",
    "category": "Growth",
    "unit": "$",
    "description": "Revenue from the immediately prior comparable period."
  },
  {
    "key": "period_end",
    "label": "Period end",
    "category": "Growth",
    "unit": "",
    "description": "As-of date for the financial statement row."
  },
  {
    "key": "fiscal_year",
    "label": "Fiscal year",
    "category": "Growth",
    "unit": "",
    "description": "Company fiscal year label."
  },
  {
    "key": "pe_ratio",
    "label": "P/E ratio",
    "category": "Valuation",
    "unit": "x",
    "description": "Price divided by earnings per share."
  },
  {
    "key": "ev_to_ebitda",
    "label": "EV / EBITDA",
    "category": "Valuation",
    "unit": "x",
    "description": "Enterprise value relative to EBITDA."
  },
  {
    "key": "price_to_sales",
    "label": "Price / sales",
    "category": "Valuation",
    "unit": "x",
    "description": "Market cap divided by revenue."
  },
  {
    "key": "price_to_fcf",
    "label": "Price / FCF",
    "category": "Valuation",
    "unit": "x",
    "description": "Equity value relative to free cash flow."
  },
  {
    "key": "dividend_yield",
    "label": "Dividend yield",
    "category": "Valuation",
    "unit": "%",
    "description": "Annual dividend divided by price."
  },
  {
    "key": "payout_ratio",
    "label": "Payout ratio",
    "category": "Valuation",
    "unit": "%",
    "description": "Dividends as a share of earnings."
  },
  {
    "key": "beta",
    "label": "Beta",
    "category": "Price",
    "unit": "x",
    "description": "Sensitivity of returns to the broad market."
  },
  {
    "key": "market_cap",
    "label": "Market cap",
    "category": "Valuation",
    "unit": "$",
    "description": "Shares outstanding times price."
  },
  {
    "key": "enterprise_value",
    "label": "Enterprise value",
    "category": "Valuation",
    "unit": "$",
    "description": "Equity plus net debt preferred EV definition."
  },
  {
    "key": "week_52_high",
    "label": "52-week high",
    "category": "Price",
    "unit": "$",
    "description": "Highest trade over the last year."
  },
  {
    "key": "week_52_low",
    "label": "52-week low",
    "category": "Price",
    "unit": "$",
    "description": "Lowest trade over the last year."
  },
  {
    "key": "avg_volume_30d",
    "label": "Avg volume (30d)",
    "category": "Price",
    "unit": "",
    "description": "Average daily shares traded."
  },
  {
    "key": "short_interest_pct",
    "label": "Short interest",
    "category": "Price",
    "unit": "%",
    "description": "Short shares as percent of float."
  },
  {
    "key": "institutional_holding_pct",
    "label": "Institutional ownership",
    "category": "Valuation",
    "unit": "%",
    "description": "Percent held by institutions."
  },
  {
    "key": "insider_holding_pct",
    "label": "Insider ownership",
    "category": "Valuation",
    "unit": "%",
    "description": "Percent held by insiders."
  },
  {
    "key": "revenue_cagr_3y",
    "label": "Revenue CAGR (3y)",
    "category": "Growth",
    "unit": "%",
    "description": "Compound annual revenue growth."
  },
  {
    "key": "ebitda_margin",
    "label": "EBITDA margin",
    "category": "Profitability",
    "unit": "%",
    "description": "EBITDA divided by revenue."
  },
  {
    "key": "fcf_yield",
    "label": "FCF yield",
    "category": "Valuation",
    "unit": "%",
    "description": "Free cash flow divided by enterprise value."
  },
  {
    "key": "net_debt_to_ebitda",
    "label": "Net debt / EBITDA",
    "category": "Liquidity",
    "unit": "x",
    "description": "Leverage versus EBITDA generation."
  },
  {
    "key": "master_signal",
    "label": "Master signal",
    "category": "Price",
    "unit": "",
    "description": "Signal composite regime label from fundamentals + trend."
  },
  {
    "key": "working_capital",
    "label": "Working capital",
    "category": "Liquidity",
    "unit": "$",
    "description": "Current assets minus current liabilities."
  },
  {
    "key": "rsi_14",
    "label": "RSI (14)",
    "category": "Price",
    "unit": "",
    "description": "Relative strength index momentum oscillator."
  },
  {
    "key": "sma_50",
    "label": "SMA (50)",
    "category": "Price",
    "unit": "$",
    "description": "50-day simple moving average of price."
  },
  {
    "key": "sma_200",
    "label": "SMA (200)",
    "category": "Price",
    "unit": "$",
    "description": "200-day simple moving average of price."
  }
];

export function metricByKey(key: string): MetricDefinition | undefined {
  return METRICS.find((m) => m.key === key);
}
