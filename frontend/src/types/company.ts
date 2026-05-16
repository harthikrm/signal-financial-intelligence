export interface Company {
  ticker: string;
  name: string;
  sector?: string | null;
  exchange?: string | null;
  cik?: string | null;
}

export interface MetricsResponse {
  ticker: string;
  data: Record<string, unknown>;
}

export interface PriceSummaryResponse {
  ticker: string;
  last_close?: number | null;
  as_of?: string | null;
}

export interface IndicatorsResponse {
  ticker: string;
  date?: string | null;
  rsi_14?: number | null;
  sma_50?: number | null;
  sma_200?: number | null;
}

export interface PriceSnapshotItem {
  ticker: string;
  name: string;
  sector?: string | null;
  exchange?: string | null;
  logo_url?: string | null;
  last_close?: number | null;
  day_change_pct?: number | null;
}
