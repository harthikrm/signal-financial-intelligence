import { useEffect, useMemo, useState } from "react";

import type { PriceSnapshotItem } from "../../types/company";

interface BaseProps {
  companies: PriceSnapshotItem[];
  onSelect: (ticker: string) => void;
}

interface EmptyProps extends BaseProps {
  mode?: "empty";
  sticky?: false;
}

interface StickyProps extends BaseProps {
  mode: "sticky";
  selectedTicker: string;
  selectedLabel: string;
  onClear: () => void;
}

type Props = EmptyProps | StickyProps;

function isSticky(props: Props): props is StickyProps {
  return props.mode === "sticky";
}

export function TickerSearch(props: Props) {
  const { companies, onSelect } = props;
  const sticky = isSticky(props);

  const [query, setQuery] = useState("");
  const [editing, setEditing] = useState(false);
  const [emptyOpen, setEmptyOpen] = useState(false);
  const [clearHover, setClearHover] = useState(false);

  const selectedTicker = sticky ? props.selectedTicker : "";

  useEffect(() => {
    if (!sticky) return;
    setQuery("");
    setEditing(false);
  }, [sticky, selectedTicker]);

  const filtered = useMemo(() => {
    const q = query.trim().toUpperCase();
    if (!q) return companies.slice(0, sticky ? 8 : 70);
    return companies
      .filter(
        (c) =>
          c.ticker.toUpperCase().includes(q) ||
          c.name.toUpperCase().includes(q)
      )
      .slice(0, sticky ? 8 : 12);
  }, [companies, query, sticky]);

  const showResults = sticky
    ? editing && query.trim().length > 0 && filtered.length > 0
    : (emptyOpen || query.trim().length > 0) && filtered.length > 0;

  const inputValue = sticky
    ? editing
      ? query
      : props.selectedLabel
    : query;

  const handleFocus = () => {
    if (sticky) {
      setEditing(true);
      setQuery("");
    } else {
      setEmptyOpen(true);
    }
  };

  const handleBlur = () => {
    if (!sticky) {
      window.setTimeout(() => setEmptyOpen(false), 150);
    }
  };

  const handleClear = () => {
    setQuery("");
    setEditing(false);
    if (sticky) {
      props.onClear();
    }
  };

  const wrapperStyle = sticky
    ? {
        width: "100%",
        maxWidth: 600,
        position: "relative" as const,
      }
    : {
        width: "100%",
        maxWidth: 400,
        position: "relative" as const,
      };

  const inputStyle = sticky
    ? {
        width: "100%",
        height: 40,
        padding: "0 40px 0 16px",
        fontSize: 14,
        fontWeight: 400,
        borderRadius: 6,
        border: "0.5px solid rgba(255,255,255,0.12)",
        background: "rgba(255,255,255,0.06)",
        color: "#ffffff",
        outline: "none",
        fontFamily: "var(--font-display)",
        boxSizing: "border-box" as const,
      }
    : {
        width: "100%",
        padding: "14px 20px",
        fontSize: 16,
        fontWeight: 500,
        borderRadius: 8,
        border: "0.5px solid rgba(255,255,255,0.15)",
        background: "rgba(255,255,255,0.05)",
        color: "#ffffff",
        outline: "none",
        textAlign: "center" as const,
        letterSpacing: "0.12em",
        fontFamily: "var(--font-mono)",
      };

  return (
    <div style={wrapperStyle}>
      <input
        type="text"
        autoComplete="off"
        spellCheck={false}
        value={inputValue}
        onChange={(e) => {
          if (sticky && !editing) setEditing(true);
          setQuery(e.target.value);
        }}
        onFocus={handleFocus}
        onBlur={handleBlur}
        placeholder={sticky ? "Search ticker or company" : "TCKR"}
        autoFocus={!sticky}
        style={inputStyle}
      />
      {sticky && selectedTicker && (
        <button
          type="button"
          onClick={handleClear}
          onMouseEnter={() => setClearHover(true)}
          onMouseLeave={() => setClearHover(false)}
          aria-label="Clear ticker"
          style={{
            position: "absolute",
            right: 12,
            top: "50%",
            transform: "translateY(-50%)",
            border: "none",
            background: "transparent",
            cursor: "pointer",
            fontSize: 18,
            lineHeight: 1,
            padding: 0,
            color: clearHover ? "#ffffff" : "rgba(255,255,255,0.4)",
          }}
        >
          ×
        </button>
      )}
      {showResults && (
        <ul
          style={{
            listStyle: "none",
            marginTop: 6,
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
          {filtered.map((c) => (
            <li key={c.ticker}>
              <button
                type="button"
                onClick={() => {
                  onSelect(c.ticker);
                  setQuery("");
                  setEditing(false);
                  setEmptyOpen(false);
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
}
