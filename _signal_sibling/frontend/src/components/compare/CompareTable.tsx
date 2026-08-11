import { COMPARE_METRIC_ROWS } from "../../constants/compareMetrics";
import { useMetricsBatch } from "../../hooks/useMetricsBatch";
import { formatMetricValue } from "../../lib/formatMetric";
import { Spinner } from "../ui/Spinner";

interface Props {
  tickers: string[];
}

function numericValue(raw: unknown): number | null {
  if (raw == null || raw === "") return null;
  const n = typeof raw === "number" ? raw : Number(raw);
  return Number.isFinite(n) ? n : null;
}

function cellClass(
  values: (number | null)[],
  index: number,
  higherIsBetter: boolean
): string | undefined {
  const nums = values.filter((v): v is number => v != null);
  if (nums.length < 2 || values[index] == null) return undefined;
  const v = values[index]!;
  const best = higherIsBetter ? Math.max(...nums) : Math.min(...nums);
  const worst = higherIsBetter ? Math.min(...nums) : Math.max(...nums);
  if (v === best && best !== worst) return "positive";
  if (v === worst && best !== worst) return "negative";
  return undefined;
}

export function CompareTable({ tickers }: Props) {
  const queries = useMetricsBatch(tickers);
  const loading = queries.some((q) => q.isLoading);
  const byTicker: Record<string, Record<string, unknown>> = {};
  tickers.forEach((t, i) => {
    byTicker[t] = queries[i]?.data?.data ?? {};
  });

  if (loading) {
    return (
      <div style={{ padding: 24 }}>
        <Spinner />
      </div>
    );
  }

  return (
    <div style={{ overflowX: "auto" }}>
      <table
        style={{
          width: "100%",
          borderCollapse: "collapse",
          fontSize: 13,
        }}
      >
        <thead>
          <tr>
            <th
              style={{
                textAlign: "left",
                padding: "10px 12px",
                color: "var(--text-tertiary)",
                fontWeight: 500,
                borderBottom: "0.5px solid var(--border)",
              }}
            >
              Metric
            </th>
            {tickers.map((t) => (
              <th
                key={t}
                style={{
                  textAlign: "right",
                  padding: "10px 12px",
                  fontWeight: 600,
                  borderBottom: "0.5px solid var(--border)",
                }}
              >
                {t}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {COMPARE_METRIC_ROWS.map((row) => {
            const values = tickers.map((t) =>
              numericValue(byTicker[t]?.[row.key])
            );
            return (
              <tr key={row.key}>
                <td
                  style={{
                    padding: "10px 12px",
                    color: "var(--text-secondary)",
                    borderBottom: "0.5px solid var(--border)",
                  }}
                >
                  {row.label}
                </td>
                {tickers.map((t, i) => {
                  const raw = byTicker[t]?.[row.key];
                  const cls = cellClass(values, i, row.higherIsBetter);
                  return (
                    <td
                      key={t}
                      className={cls ? `mono ${cls}` : "mono"}
                      style={{
                        textAlign: "right",
                        padding: "10px 12px",
                        borderBottom: "0.5px solid var(--border)",
                        fontWeight: 500,
                      }}
                    >
                      {formatMetricValue(raw, row.unit)}
                    </td>
                  );
                })}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
