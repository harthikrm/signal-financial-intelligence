import { useMemo } from "react";

import { getTradingViewSymbol } from "../../constants/companies";
import { METRICS } from "../../constants/metrics";
import { useIndicators } from "../../hooks/useIndicators";
import { useMetrics } from "../../hooks/useMetrics";
import { usePriceSnapshot } from "../../hooks/usePriceSnapshot";
import { usePriceSummary } from "../../hooks/usePriceSummary";
import { useAppStore } from "../../store/appStore";
import TechnicalPanel from "./TechnicalPanel";
import TradingViewWidget from "./TradingViewWidget";
import { DataFreshness } from "../ui/DataFreshness";
import { ErrorMessage } from "../ui/ErrorMessage";
import { MetricTooltip } from "../ui/MetricTooltip";
import { Spinner } from "../ui/Spinner";

function fmtVal(v: unknown, unit: string): string {
  if (v == null || v === "") return "—";
  if (typeof v === "number") {
    if (unit === "%") return `${v.toFixed(2)}%`;
    if (unit === "$") {
      if (Math.abs(v) >= 1e9) return `$${(v / 1e9).toFixed(2)}B`;
      if (Math.abs(v) >= 1e6) return `$${(v / 1e6).toFixed(2)}M`;
      return `$${v.toLocaleString(undefined, { maximumFractionDigits: 2 })}`;
    }
    if (unit === "x") return `${v.toFixed(2)}x`;
    return String(v);
  }
  return String(v);
}

export function ExploreView() {
  const activeTicker = useAppStore((s) => s.activeTicker);
  const setActiveTicker = useAppStore((s) => s.setActiveTicker);
  const { data: snap, isLoading: snapLoading, error: snapErr, exchangeByTicker } =
    usePriceSnapshot();
  const { data: m, isLoading: mLoading, error: mErr } = useMetrics(activeTicker);
  const { data: px } = usePriceSummary(activeTicker);
  const { data: ind } = useIndicators(activeTicker);

  const tradingViewSymbol = useMemo(() => {
    if (!activeTicker) return null;
    const exchange = exchangeByTicker[activeTicker];
    if (!exchange) return null;
    return getTradingViewSymbol(activeTicker, exchange);
  }, [activeTicker, exchangeByTicker]);

  const gridMetrics = useMemo(() => {
    if (!m?.data) return [];
    const keys = new Set(Object.keys(m.data));
    return METRICS.filter(
      (def) =>
        keys.has(def.key) &&
        !["period_end", "period_type", "fiscal_year", "form", "ticker"].includes(
          def.key
        )
    ).slice(0, 24);
  }, [m]);

  return (
    <div
      style={{
        display: "flex",
        height: "100%",
        minHeight: 0,
        gap: 16,
        padding: "12px 16px",
      }}
    >
      <div
        style={{
          width: 280,
          flexShrink: 0,
          border: "0.5px solid var(--border)",
          borderRadius: 12,
          overflowY: "auto",
          background: "var(--bg-secondary)",
        }}
      >
        {snapLoading && (
          <div style={{ padding: 16 }}>
            <Spinner />
          </div>
        )}
        {snapErr && (
          <div style={{ padding: 12 }}>
            <ErrorMessage />
          </div>
        )}
        {snap?.map((row) => (
          <button
            key={row.ticker}
            type="button"
            onClick={() => setActiveTicker(row.ticker)}
            style={{
              width: "100%",
              display: "flex",
              alignItems: "center",
              gap: 10,
              padding: "10px 12px",
              border: "none",
              borderBottom: "0.5px solid var(--border)",
              background:
                activeTicker === row.ticker ? "var(--bg-tertiary)" : "transparent",
              cursor: "pointer",
              textAlign: "left",
            }}
          >
            {row.logo_url ? (
              <img src={row.logo_url} alt="" width={24} height={24} style={{ borderRadius: 4 }} />
            ) : (
              <div
                style={{
                  width: 24,
                  height: 24,
                  borderRadius: 4,
                  background: "var(--bg-tertiary)",
                }}
              />
            )}
            <div>
              <div style={{ fontWeight: 600, fontSize: 13 }}>{row.ticker}</div>
              <div
                style={{
                  fontSize: 11,
                  color: "var(--text-tertiary)",
                  maxWidth: 200,
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  whiteSpace: "nowrap",
                }}
              >
                {row.name}
              </div>
            </div>
          </button>
        ))}
      </div>

      <div style={{ flex: 1, minWidth: 0, display: "flex", flexDirection: "column" }}>
        {!activeTicker && (
          <p style={{ color: "var(--text-secondary)", fontSize: 14 }}>
            Select a company to view fundamentals.
          </p>
        )}
        {activeTicker && mLoading && (
          <div style={{ padding: 24 }}>
            <Spinner />
          </div>
        )}
        {activeTicker && mErr && <ErrorMessage />}
        {activeTicker && m && (
          <>
            <div style={{ marginBottom: 12 }}>
              <h2 style={{ fontSize: 20, fontWeight: 600 }}>{m.ticker}</h2>
              <div className="mono price" style={{ fontSize: 14, marginTop: 4 }}>
                Last close: {fmtVal(px?.last_close, "$")}{" "}
                <span style={{ color: "var(--text-tertiary)", fontSize: 12 }}>
                  {px?.as_of ? `(as of ${px.as_of})` : ""}
                </span>
              </div>
              {ind && (
                <div
                  className="mono"
                  style={{
                    fontSize: 12,
                    color: "var(--text-secondary)",
                    marginTop: 6,
                    display: "flex",
                    gap: 16,
                  }}
                >
                  <MetricTooltip metricKey="rsi_14">
                    <span>RSI {ind.rsi_14 != null ? ind.rsi_14.toFixed(1) : "—"}</span>
                  </MetricTooltip>
                  <MetricTooltip metricKey="sma_50">
                    <span>SMA50 {ind.sma_50 != null ? fmtVal(ind.sma_50, "$") : "—"}</span>
                  </MetricTooltip>
                  <MetricTooltip metricKey="sma_200">
                    <span>SMA200 {ind.sma_200 != null ? fmtVal(ind.sma_200, "$") : "—"}</span>
                  </MetricTooltip>
                </div>
              )}
            </div>
            {tradingViewSymbol && (
              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: 12,
                  marginBottom: 12,
                  flexShrink: 0,
                  minHeight: 0,
                }}
              >
                <TradingViewWidget symbol={tradingViewSymbol} />
                <TechnicalPanel symbol={tradingViewSymbol} />
              </div>
            )}
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(3, minmax(0, 1fr))",
                gap: 10,
                overflowY: "auto",
              }}
            >
              {gridMetrics.map((def) => (
                <div
                  key={def.key}
                  style={{
                    padding: "10px 12px",
                    borderRadius: 10,
                    border: "0.5px solid var(--border)",
                    background: "var(--bg-secondary)",
                  }}
                >
                  <MetricTooltip metricKey={def.key}>
                    <div style={{ fontSize: 11, color: "var(--text-tertiary)" }}>
                      {def.label}
                    </div>
                  </MetricTooltip>
                  <div className="mono metric-value" style={{ fontSize: 14, marginTop: 4 }}>
                    {fmtVal(m.data[def.key], def.unit)}
                  </div>
                </div>
              ))}
            </div>
            <DataFreshness
              date={
                m.data["period_end"]
                  ? String(m.data["period_end"])
                  : undefined
              }
            />
          </>
        )}
      </div>
    </div>
  );
}
