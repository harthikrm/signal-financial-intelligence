/** Extract compact "NVDA 10-K 2026" from full agent/Knowledge citation strings. */
const FILING_CITE_RE =
  /\b([A-Z]{1,5})\s+(10-K|10-Q|8-K)\s+(\d{4})(?:-\d{2}-\d{2})?/i;

export function formatCitationPill(source: string): string {
  const trimmed = (source || "").trim();
  if (!trimmed) return "";

  const match = trimmed.match(FILING_CITE_RE);
  if (match) {
    return `${match[1].toUpperCase()} ${match[2].toUpperCase()} ${match[3]}`;
  }

  const head = trimmed.split(",")[0].trim();
  const headMatch = head.match(FILING_CITE_RE);
  if (headMatch) {
    return `${headMatch[1].toUpperCase()} ${headMatch[2].toUpperCase()} ${headMatch[3]}`;
  }

  const parts = head.split(/\s+/);
  if (parts.length >= 2) {
    const ticker = parts[0];
    const filingType = parts[1];
    const datePart = parts[2] ?? "";
    const year = /^\d{4}/.test(datePart) ? datePart.slice(0, 4) : "";
    return year ? `${ticker} ${filingType} ${year}` : `${ticker} ${filingType}`;
  }

  return head.slice(0, 32);
}
