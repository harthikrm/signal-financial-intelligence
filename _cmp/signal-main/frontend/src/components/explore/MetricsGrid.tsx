import { useMemo } from "react";

import {
  METRICS,
  type MetricCategory,
  type MetricDefinition,
} from "../../constants/metrics";
import { formatMetricValue } from "../../lib/formatMetric";
import { MetricTooltip } from "../ui/MetricTooltip";

const SKIP_KEYS = new Set([
  "period_end",
  "period_type",
  "fiscal_year",
  "form",
  "ticker",
  // Shown in Explore key metrics row (API-computed or top strip)
  "pe_ratio",
  "market_cap",
  "week_52_high",
  "week_52_low",
]);

const CATEGORY_ORDER: MetricCategory[] = [
  "Profitability",
  "Growth",
  "Efficiency",
  "Liquidity",
  "Cash Flow",
  "Valuation",
  "Price",
];

interface Props {
  data: Record<string, unknown>;
}

export function MetricsGrid({ data }: Props) {
  const byCategory = useMemo(() => {
    const keys = new Set(Object.keys(data));
    const map = new Map<MetricCategory, MetricDefinition[]>();

    for (const def of METRICS) {
      if (SKIP_KEYS.has(def.key) || !keys.has(def.key)) continue;
      const list = map.get(def.category) ?? [];
      list.push(def);
      map.set(def.category, list);
    }

    return CATEGORY_ORDER.filter((c) => map.has(c)).map((c) => ({
      category: c,
      metrics: map.get(c)!,
    }));
  }, [data]);

  if (byCategory.length === 0) {
    return null;
  }

  return (
    <div style={{ width: "100%", paddingTop: 16, paddingBottom: 32 }}>
      {byCategory.map(({ category, metrics }) => (
        <div key={category} style={{ marginBottom: 20 }}>
          <div
            style={{
              fontSize: 11,
              color: "var(--text-secondary)",
              padding: "0 24px 10px",
              fontWeight: 500,
            }}
          >
            {category}
          </div>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))",
              gap: 10,
              padding: "0 24px",
            }}
          >
            {metrics.map((def) => (
              <div
                key={def.key}
                style={{
                  padding: "10px 12px",
                  borderRadius: 8,
                  border: "0.5px solid rgba(255,255,255,0.08)",
                  background: "rgba(255,255,255,0.04)",
                }}
              >
                <MetricTooltip metricKey={def.key}>
                  <div style={{ fontSize: 11, color: "var(--text-tertiary)" }}>
                    {def.label}
                  </div>
                </MetricTooltip>
                <div
                  className="mono metric-value"
                  style={{ fontSize: 14, marginTop: 4, fontWeight: 500 }}
                >
                  {formatMetricValue(data[def.key], def.unit)}
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}

    </div>
  );
}
