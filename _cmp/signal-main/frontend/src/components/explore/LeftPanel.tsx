import { useCompany } from "../../hooks/useCompany";
import { useMetrics } from "../../hooks/useMetrics";
import { usePriceSnapshot } from "../../hooks/usePriceSnapshot";
import { formatMetricValue } from "../../lib/formatMetric";
import { DataFreshness } from "../ui/DataFreshness";
import { MetricTooltip } from "../ui/MetricTooltip";
import { Spinner } from "../ui/Spinner";

interface Props {
  ticker: string;
}

const PANEL_METRICS: { key: string; label: string; unit: string }[] = [
  { key: "market_cap", label: "Market Cap", unit: "$" },
  { key: "pe_ratio", label: "P/E Ratio", unit: "x" },
  { key: "revenue_ttm", label: "Revenue TTM", unit: "$" },
  { key: "eps_diluted", label: "EPS", unit: "$" },
];

function weekRangeLabel(data: Record<string, unknown>): string {
  const hi = data.week_52_high;
  const lo = data.week_52_low;
  if (hi == null && lo == null) return "—";
  const h = hi != null ? formatMetricValue(hi, "$") : "—";
  const l = lo != null ? formatMetricValue(lo, "$") : "—";
  return `${h} / ${l}`;
}

export function LeftPanel({ ticker }: Props) {
  const { data: company } = useCompany(ticker);
  const { data: metrics, isLoading } = useMetrics(ticker);
  const { data: snap } = usePriceSnapshot();

  const row = snap?.find((r) => r.ticker === ticker);
  const data = metrics?.data ?? {};
  const companyName = company?.name ?? row?.name ?? ticker;
  const sector = company?.sector ?? row?.sector;

  return (
    <aside className="explore-left-panel">
      <div style={{ display: "flex", alignItems: "flex-start", gap: 10 }}>
        {row?.logo_url ? (
          <img
            src={row.logo_url}
            alt=""
            width={32}
            height={32}
            style={{ borderRadius: 6, objectFit: "cover", flexShrink: 0 }}
          />
        ) : (
          <span
            style={{
              width: 32,
              height: 32,
              borderRadius: 6,
              background: "rgba(255,255,255,0.08)",
              flexShrink: 0,
            }}
          />
        )}
        <div style={{ minWidth: 0 }}>
          <div
            style={{
              fontSize: 16,
              fontWeight: 600,
              lineHeight: 1.25,
              color: "var(--text-primary)",
            }}
          >
            {companyName}
          </div>
          {sector && (
            <span
              style={{
                display: "inline-block",
                marginTop: 6,
                fontSize: 11,
                color: "var(--text-secondary)",
                padding: "2px 8px",
                borderRadius: 4,
                border: "0.5px solid rgba(255,255,255,0.12)",
                background: "rgba(255,255,255,0.04)",
              }}
            >
              {sector}
            </span>
          )}
        </div>
      </div>

      <div
        style={{
          height: "0.5px",
          background: "rgba(255,255,255,0.06)",
          margin: "20px 0",
        }}
      />

      {isLoading ? (
        <Spinner />
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {PANEL_METRICS.map((m) => (
            <div key={m.key}>
              <MetricTooltip metricKey={m.key}>
                <div
                  style={{
                    fontSize: 11,
                    color: "var(--text-tertiary)",
                    textTransform: "uppercase",
                    letterSpacing: "0.05em",
                    marginBottom: 4,
                  }}
                >
                  {m.label}
                </div>
              </MetricTooltip>
              <div
                className="mono metric-value"
                style={{
                  fontSize: 15,
                  fontWeight: 500,
                  color: "#ffffff",
                }}
              >
                {formatMetricValue(data[m.key], m.unit)}
              </div>
            </div>
          ))}
          <div>
            <div
              style={{
                fontSize: 11,
                color: "var(--text-tertiary)",
                textTransform: "uppercase",
                letterSpacing: "0.05em",
                marginBottom: 4,
              }}
            >
              52W High / Low
            </div>
            <div
              className="mono metric-value"
              style={{
                fontSize: 15,
                fontWeight: 500,
                color: "#ffffff",
              }}
            >
              {weekRangeLabel(data)}
            </div>
          </div>
        </div>
      )}

      <div style={{ marginTop: "auto", paddingTop: 20 }}>
        <DataFreshness
          date={data.period_end ? String(data.period_end) : undefined}
        />
      </div>
    </aside>
  );
}
