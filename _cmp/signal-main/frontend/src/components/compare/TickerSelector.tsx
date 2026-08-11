import { useMemo, useState } from "react";

import type { PriceSnapshotItem } from "../../types/company";

interface Props {
  companies: PriceSnapshotItem[];
  selectedTickers: string[];
  onSelectAt: (index: number, ticker: string) => void;
  onClearAt: (index: number) => void;
}

const MAX_SLOTS = 3;

export function TickerSelector({
  companies,
  selectedTickers,
  onSelectAt,
  onClearAt,
}: Props) {
  const [queries, setQueries] = useState<string[]>(["", "", ""]);
  const [openSlot, setOpenSlot] = useState<number | null>(null);
  const [clearHoverSlot, setClearHoverSlot] = useState<number | null>(null);

  const visibleSlots = Math.min(MAX_SLOTS, Math.max(1, selectedTickers.length + 1));

  const resultSets = useMemo(() => {
    return Array.from({ length: MAX_SLOTS }).map((_, index) => {
      const excluded = new Set(
        selectedTickers.filter((_, selectedIndex) => selectedIndex !== index)
      );
      const q = queries[index].trim().toUpperCase();

      const filtered = companies.filter((c) => {
        if (excluded.has(c.ticker)) return false;
        if (!q) return true;
        return (
          c.ticker.toUpperCase().includes(q) || c.name.toUpperCase().includes(q)
        );
      });

      return filtered.slice(0, q ? 12 : 70);
    });
  }, [companies, queries, selectedTickers]);

  return (
    <div
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "flex-start",
        gap: 12,
        flexWrap: "wrap",
      }}
    >
      {Array.from({ length: visibleSlots }).map((_, index) => {
        const selected = selectedTickers[index] ?? "";
        const isOpen = openSlot === index;
        const query = queries[index];
        const results = resultSets[index];

        return (
          <div
            key={index}
            style={{ width: 200, position: "relative" }}
          >
            <input
              type="search"
              placeholder="TCKR"
              value={isOpen ? query : selected}
              onFocus={() => {
                setOpenSlot(index);
                setQueries((prev) => {
                  const next = [...prev];
                  next[index] = "";
                  return next;
                });
              }}
              onBlur={() => {
                window.setTimeout(() => {
                  setOpenSlot((slot) => (slot === index ? null : slot));
                  setQueries((prev) => {
                    const next = [...prev];
                    next[index] = "";
                    return next;
                  });
                }, 150);
              }}
              onChange={(e) => {
                const v = e.target.value;
                if (!isOpen) setOpenSlot(index);
                setQueries((prev) => {
                  const next = [...prev];
                  next[index] = v;
                  return next;
                });
              }}
              style={{
                width: "100%",
                padding: "12px 16px",
                fontSize: 14,
                borderRadius: 6,
                border: "0.5px solid rgba(255,255,255,0.12)",
                background: "rgba(255,255,255,0.05)",
                color: "#ffffff",
                outline: "none",
                boxSizing: "border-box",
                fontFamily: "var(--font-display)",
              }}
            />
            {selected && (
              <button
                type="button"
                aria-label={`Clear slot ${index + 1}`}
                onMouseEnter={() => setClearHoverSlot(index)}
                onMouseLeave={() => setClearHoverSlot((slot) => (slot === index ? null : slot))}
                onClick={() => {
                  onClearAt(index);
                  setQueries((prev) => {
                    const next = [...prev];
                    next[index] = "";
                    return next;
                  });
                  setOpenSlot(null);
                }}
                style={{
                  position: "absolute",
                  right: 12,
                  top: "50%",
                  transform: "translateY(-50%)",
                  border: "none",
                  background: "transparent",
                  color: clearHoverSlot === index ? "#ffffff" : "rgba(255,255,255,0.4)",
                  fontSize: 18,
                  lineHeight: 1,
                  cursor: "pointer",
                  padding: 0,
                }}
              >
                ×
              </button>
            )}
            {isOpen && results.length > 0 && (
              <ul
                style={{
                  listStyle: "none",
                  margin: "6px 0 0",
                  padding: 0,
                  textAlign: "left",
                  border: "0.5px solid rgba(255,255,255,0.12)",
                  borderRadius: 8,
                  overflow: "hidden",
                  background: "rgba(0,0,0,0.95)",
                  position: "absolute",
                  left: 0,
                  right: 0,
                  zIndex: 30,
                  maxHeight: 280,
                  overflowY: "auto",
                }}
              >
                {results.map((c) => (
                  <li key={c.ticker}>
                    <button
                      type="button"
                      onClick={() => {
                        onSelectAt(index, c.ticker);
                        setQueries((prev) => {
                          const next = [...prev];
                          next[index] = "";
                          return next;
                        });
                        setOpenSlot(null);
                      }}
                      style={{
                        width: "100%",
                        display: "flex",
                        alignItems: "center",
                        gap: 12,
                        padding: "8px 12px",
                        border: "none",
                        borderBottom: "0.5px solid rgba(255,255,255,0.06)",
                        background: "transparent",
                        cursor: "pointer",
                        color: "var(--text-primary)",
                        textAlign: "left",
                      }}
                    >
                      {c.logo_url ? (
                        <img
                          src={c.logo_url}
                          alt=""
                          width={22}
                          height={22}
                          style={{ borderRadius: 6 }}
                        />
                      ) : (
                        <span
                          style={{
                            width: 22,
                            height: 22,
                            borderRadius: 6,
                            background: "var(--bg-tertiary)",
                          }}
                        />
                      )}
                      <span>
                        <strong style={{ fontSize: 13 }}>{c.ticker}</strong>
                        <span
                          style={{
                            display: "block",
                            fontSize: 12,
                            color: "var(--text-secondary)",
                          }}
                        >
                          {c.name}
                        </span>
                      </span>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        );
      })}
    </div>
  );
}
