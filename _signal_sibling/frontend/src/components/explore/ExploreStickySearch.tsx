import type { PriceSnapshotItem } from "../../types/company";
import { TickerSearch } from "./TickerSearch";

interface Props {
  ticker: string;
  companyName?: string;
  companies: PriceSnapshotItem[];
  onSelect: (ticker: string) => void;
  onClear: () => void;
}

export function ExploreStickySearch({
  ticker,
  companyName,
  companies,
  onSelect,
  onClear,
}: Props) {
  const selectedLabel = companyName?.trim() || ticker;

  return (
    <div
      style={{
        position: "sticky",
        top: 0,
        zIndex: 20,
        display: "flex",
        justifyContent: "center",
        padding: "12px 24px",
        background: "rgba(0,0,0,0.9)",
        backdropFilter: "blur(12px)",
        WebkitBackdropFilter: "blur(12px)",
        borderBottom: "0.5px solid rgba(255,255,255,0.08)",
        flexShrink: 0,
      }}
    >
      <TickerSearch
        mode="sticky"
        selectedTicker={ticker}
        selectedLabel={selectedLabel}
        companies={companies}
        onSelect={onSelect}
        onClear={onClear}
      />
    </div>
  );
}
