import { usePriceSnapshot } from "../../hooks/usePriceSnapshot";

function fmtPrice(n: number | null | undefined) {
  if (n == null || Number.isNaN(n)) return "—";
  return n.toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

function fmtPct(n: number | null | undefined) {
  if (n == null || Number.isNaN(n)) return "—";
  const sign = n >= 0 ? "+" : "";
  return `${sign}${n.toFixed(2)}%`;
}

export function StatusBar() {
  const { data, isLoading } = usePriceSnapshot();
  const items = data ?? [];

  const strip = [...items, ...items];

  return (
    <footer
      style={{
        position: "fixed",
        bottom: 0,
        left: 0,
        right: 0,
        height: 36,
        zIndex: 40,
        borderTop: "0.5px solid var(--border)",
        background: "rgba(0,0,0,0.9)",
        overflow: "hidden",
        display: "flex",
        alignItems: "center",
      }}
    >
      {isLoading && items.length === 0 ? (
        <span
          style={{
            paddingLeft: 16,
            fontSize: 11,
            color: "var(--text-tertiary)",
          }}
        >
          Loading tape…
        </span>
      ) : (
        <div
          className="tape-track"
          style={{
            display: "flex",
            alignItems: "center",
            gap: 28,
            whiteSpace: "nowrap",
            paddingLeft: 16,
          }}
        >
          {strip.map((row, idx) => {
            const chg = row.day_change_pct;
            const pos = chg != null && chg >= 0;
            const neg = chg != null && chg < 0;
            return (
              <div
                key={`${row.ticker}-${idx}`}
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: 8,
                }}
              >
                {row.logo_url ? (
                  <img
                    src={row.logo_url}
                    alt=""
                    width={20}
                    height={20}
                    style={{ borderRadius: 4, objectFit: "cover" }}
                  />
                ) : (
                  <div
                    style={{
                      width: 20,
                      height: 20,
                      borderRadius: 4,
                      background: "var(--bg-tertiary)",
                    }}
                  />
                )}
                <span
                  style={{
                    fontSize: 12,
                    fontWeight: 500,
                    color: "var(--text-secondary)",
                  }}
                >
                  {row.ticker}
                </span>
                <span className="mono price" style={{ fontSize: 12, color: "var(--text-primary)" }}>
                  {fmtPrice(row.last_close)}
                </span>
                <span
                  className={`mono ${pos ? "positive" : ""} ${neg ? "negative" : ""}`}
                  style={{ fontSize: 11 }}
                >
                  {fmtPct(chg)}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </footer>
  );
}
