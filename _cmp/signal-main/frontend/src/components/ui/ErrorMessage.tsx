export function ErrorMessage({
  message = "We are currently updating the page.",
}: {
  message?: string;
}) {
  return (
    <div
      style={{
        padding: "12px 16px",
        borderRadius: 8,
        background: "var(--bg-secondary)",
        color: "var(--text-secondary)",
        fontSize: 13,
        border: "0.5px solid var(--border)",
      }}
    >
      {message}
    </div>
  );
}
