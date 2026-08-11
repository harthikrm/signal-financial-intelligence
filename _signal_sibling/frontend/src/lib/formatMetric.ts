export function formatValue(value: number | null | undefined, unit: string): string {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "N/A";
  }

  if (unit === "%") {
    const abs = Math.abs(value);
    if (abs >= 10) return value.toFixed(1) + "%";
    return value.toFixed(2) + "%";
  }

  if (unit === "$") {
    const abs = Math.abs(value);
    const sign = value < 0 ? "-" : "";
    if (abs >= 1_000_000_000_000) {
      return sign + "$" + (abs / 1_000_000_000_000).toFixed(2) + "T";
    }
    if (abs >= 1_000_000_000) {
      return sign + "$" + (abs / 1_000_000_000).toFixed(1) + "B";
    }
    if (abs >= 1_000_000) {
      return sign + "$" + (abs / 1_000_000).toFixed(1) + "M";
    }
    if (abs >= 1_000) {
      return sign + "$" + (abs / 1_000).toFixed(1) + "K";
    }
    return sign + "$" + abs.toFixed(2);
  }

  if (unit === "x") {
    const abs = Math.abs(value);
    if (abs >= 10) return value.toFixed(1) + "x";
    return value.toFixed(2) + "x";
  }

  const abs = Math.abs(value);
  const sign = value < 0 ? "-" : "";
  if (abs >= 1_000_000_000) {
    return sign + (abs / 1_000_000_000).toFixed(1) + "B";
  }
  if (abs >= 1_000_000) {
    return sign + (abs / 1_000_000).toFixed(1) + "M";
  }
  return value.toFixed(2);
}

export function formatMetricValue(v: unknown, unit: string): string {
  if (v == null || v === "") return "N/A";
  const n = typeof v === "number" ? v : Number(v);
  if (Number.isNaN(n)) return String(v);
  return formatValue(n, unit);
}
