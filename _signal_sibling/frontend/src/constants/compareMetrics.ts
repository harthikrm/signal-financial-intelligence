export interface CompareMetricRow {
  key: string;
  label: string;
  unit: string;
  higherIsBetter: boolean;
}

export const COMPARE_METRIC_ROWS: CompareMetricRow[] = [
  { key: "market_cap", label: "Market Cap", unit: "$", higherIsBetter: true },
  { key: "revenue_ttm", label: "Revenue TTM", unit: "$", higherIsBetter: true },
  {
    key: "revenue_growth",
    label: "Revenue Growth YoY%",
    unit: "%",
    higherIsBetter: true,
  },
  {
    key: "gross_margin_ttm",
    label: "Gross Margin%",
    unit: "%",
    higherIsBetter: true,
  },
  {
    key: "operating_margin",
    label: "Operating Margin%",
    unit: "%",
    higherIsBetter: true,
  },
  { key: "net_margin", label: "Net Margin%", unit: "%", higherIsBetter: true },
  { key: "eps_diluted", label: "EPS TTM", unit: "$", higherIsBetter: true },
  { key: "pe_ratio", label: "P/E Ratio", unit: "x", higherIsBetter: false },
  { key: "ev_to_ebitda", label: "EV/EBITDA", unit: "x", higherIsBetter: false },
  { key: "fcf_ttm", label: "FCF TTM", unit: "$", higherIsBetter: true },
  { key: "roe", label: "Return on Equity", unit: "%", higherIsBetter: true },
  {
    key: "debt_to_equity",
    label: "Debt-to-Equity",
    unit: "x",
    higherIsBetter: false,
  },
];
