import { useCompare } from "../../hooks/useCompare";
import { usePriceSnapshot } from "../../hooks/usePriceSnapshot";
import { useAppStore } from "../../store/appStore";
import { ErrorMessage } from "../ui/ErrorMessage";
import { Spinner } from "../ui/Spinner";
import { CompareTable } from "./CompareTable";
import { TickerSelector } from "./TickerSelector";

export function CompareView() {
  const compareTickets = useAppStore((s) => s.compareTickets);
  const addCompareTicker = useAppStore((s) => s.addCompareTicker);
  const removeCompareTicker = useAppStore((s) => s.removeCompareTicker);
  const { data: snap } = usePriceSnapshot();
  const { data, isFetching, error, refetch } = useCompare(compareTickets);

  const replaceCompareTickets = (next: string[]) => {
    compareTickets.forEach((t) => removeCompareTicker(t));
    next.forEach((t) => addCompareTicker(t));
  };

  const handleSelectAt = (index: number, ticker: string) => {
    const next = [...compareTickets];
    if (index < next.length) {
      next[index] = ticker.toUpperCase();
    } else {
      next.push(ticker.toUpperCase());
    }
    replaceCompareTickets(next.slice(0, 3));
  };

  const handleClearAt = (index: number) => {
    const next = compareTickets.filter((_, i) => i !== index);
    replaceCompareTickets(next);
  };

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        height: "100%",
        padding: "12px 16px 0",
        gap: 20,
        minHeight: 0,
      }}
    >
      {compareTickets.length < 1 ? (
        <div
          style={{
            position: "fixed",
            top: 56,
            bottom: 36,
            left: 0,
            right: 0,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            minHeight: "calc(100vh - 56px - 36px - 60px)",
            padding: "0 24px",
            zIndex: 1,
          }}
        >
          <p
            style={{
              fontSize: 14,
              color: "rgba(255,255,255,0.5)",
              textAlign: "center",
              maxWidth: 480,
              margin: "0 auto 24px",
              lineHeight: 1.6,
            }}
          >
            Add at least two tickers to compare metrics side by side and press
            Generate AI Analysis for in-depth information.
          </p>
          <TickerSelector
            companies={snap ?? []}
            selectedTickers={compareTickets}
            onSelectAt={handleSelectAt}
            onClearAt={handleClearAt}
          />
        </div>
      ) : (
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: 14,
          }}
        >
          <p
            style={{
              fontSize: 14,
              color: "rgba(255,255,255,0.5)",
              textAlign: "center",
              maxWidth: 480,
              margin: "0 auto",
              lineHeight: 1.6,
            }}
          >
            Add at least two tickers to compare metrics side by side and press
            Generate AI Analysis for in-depth information.
          </p>
          <TickerSelector
            companies={snap ?? []}
            selectedTickers={compareTickets}
            onSelectAt={handleSelectAt}
            onClearAt={handleClearAt}
          />
        </div>
      )}

      <div style={{ display: "flex", justifyContent: "center" }}>
        <button
          type="button"
          onClick={() => refetch()}
          disabled={compareTickets.length < 2 || isFetching}
          style={{
            padding: "8px 14px",
            borderRadius: 8,
            border: "none",
            background: "var(--accent)",
            color: "#000",
            fontWeight: 600,
            fontSize: 12,
            cursor: compareTickets.length < 2 ? "default" : "pointer",
            opacity: compareTickets.length < 2 ? 0.4 : 1,
          }}
        >
          Generate AI Analysis
        </button>
      </div>

      <div style={{ flex: 1, overflowY: "auto", minHeight: 0, display: "flex", flexDirection: "column", gap: 20 }}>
        {compareTickets.length >= 2 && (
          <section>
            <h3
              style={{
                fontSize: 13,
                fontWeight: 600,
                color: "var(--text-secondary)",
                marginBottom: 10,
              }}
            >
              Metrics comparison
            </h3>
            <CompareTable tickers={compareTickets} />
          </section>
        )}

        {compareTickets.length >= 2 && (
          <section>
            <h3
              style={{
                fontSize: 13,
                fontWeight: 600,
                color: "var(--text-secondary)",
                marginBottom: 10,
              }}
            >
              AI analysis
            </h3>
            {isFetching && (
              <div style={{ padding: 12 }}>
                <Spinner />
              </div>
            )}
            {error && <ErrorMessage />}
            {data && (
              <pre
                style={{
                  whiteSpace: "pre-wrap",
                  fontSize: 13,
                  lineHeight: 1.55,
                  color: "var(--text-primary)",
                  fontFamily: "var(--font-display)",
                }}
              >
                {data.content}
              </pre>
            )}
            {!data && !isFetching && !error && (
              <p style={{ fontSize: 13, color: "var(--text-tertiary)" }}>
                Click &quot;Generate AI analysis&quot; for a narrative comparison.
              </p>
            )}
          </section>
        )}

        <div style={{ height: 32 }} />
      </div>

      <p
        style={{
          position: "fixed",
          bottom: 36,
          left: 0,
          right: 0,
          textAlign: "center",
          fontSize: 11,
          color: "rgba(255,255,255,0.3)",
          padding: "6px 24px",
          background: "rgba(0,0,0,0.9)",
          backdropFilter: "blur(12px)",
          WebkitBackdropFilter: "blur(12px)",
          zIndex: 10,
          margin: 0,
        }}
      >
        Signal is for informational purposes only. Not financial advice.
      </p>
    </div>
  );
}
