export function Spinner({ size = 20 }: { size?: number }) {
  return (
    <div
        style={{
          width: size,
          height: size,
          borderRadius: "50%",
          border: "2px solid rgba(249,115,22,0.25)",
          borderTopColor: "var(--accent)",
          animation: "spin 0.8s linear infinite",
          display: "inline-block",
        }}
    />
  );
}
