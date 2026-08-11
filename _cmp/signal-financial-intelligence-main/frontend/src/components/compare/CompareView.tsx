import { useCompare } from "../../hooks/useCompare";
import { COMPARE_STARTERS } from "../../constants/starters";
import { usePriceSnapshot } from "../../hooks/usePriceSnapshot";
import { useAppStore } from "../../store/appStore";
import { Disclaimer } from "../ui/Disclaimer";
import { ErrorMessage } from "../ui/ErrorMessage";
import { Spinner } from "../ui/Spinner";
import { SuggestedQuestions } from "../knowledge/SuggestedQuestions";

export function CompareView() {
  const compareTickets = useAppStore((s) => s.compareTickets);
  const addCompareTicker = useAppStore((s) => s.addCompareTicker);
  const removeCompareTicker = useAppStore((s) => s.removeCompareTicker);
  const { data: snap } = usePriceSnapshot();
  const { data, isFetching, error, refetch } = useCompare(compareTickets);

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        height: "100%",
        padding: "12px 16px",
        gap: 16,
        minHeight: 0,
      }}
    >
      <div style={{ display: "flex", flexWrap: "wrap", gap: 8, alignItems: "center" }}>
        {compareTickets.map((t) => (
          <span
            key={t}
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 6,
              padding: "6px 10px",
              borderRadius: 8,
              background: "var(--bg-secondary)",
              border: "0.5px solid var(--border)",
              fontSize: 12,
            }}
          >
            {t}
            <button
              type="button"
              onClick={() => removeCompareTicker(t)}
              style={{
                border: "none",
                background: "transparent",
                color: "var(--text-tertiary)",
                cursor: "pointer",
              }}
            >
              ×
            </button>
          </span>
        ))}
        <select
          style={{
            padding: "6px 10px",
            borderRadius: 8,
            border: "0.5px solid var(--border)",
            background: "var(--bg-secondary)",
            color: "var(--text-primary)",
            fontSize: 12,
          }}
          value=""
          onChange={(e) => {
            const v = e.target.value;
            if (v) addCompareTicker(v);
            e.target.value = "";
          }}
        >
          <option value="">Add ticker…</option>
          {(snap ?? []).map((r) => (
            <option key={r.ticker} value={r.ticker}>
              {r.ticker} — {r.name}
            </option>
          ))}
        </select>
        <button
          type="button"
          onClick={() => refetch()}
          disabled={compareTickets.length < 2 || isFetching}
          style={{
            marginLeft: "auto",
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
          Run compare
        </button>
      </div>

      <SuggestedQuestions
        questions={COMPARE_STARTERS}
        onSelect={(q) => {
          const uni = new Set((snap ?? []).map((r) => r.ticker));
          const parts = q.toUpperCase().split(/[^A-Z0-9.]+/).filter(Boolean);
          const hits = parts.filter((t) => uni.has(t)).slice(0, 3);
          hits.forEach((t) => addCompareTicker(t));
        }}
      />

      <div style={{ flex: 1, overflowY: "auto", minHeight: 0 }}>
        {isFetching && (
          <div style={{ padding: 24 }}>
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
      </div>

      <Disclaimer />
    </div>
  );
}
