export function DataFreshness({ date }: { date: string | Date | null | undefined }) {
  if (!date) return null;
  const d = typeof date === "string" ? new Date(date) : date;
  const txt = d.toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
  return (
    <p style={{ fontSize: 11, color: "var(--text-tertiary)", marginTop: 8 }}>
      Data as of {txt}
    </p>
  );
}
