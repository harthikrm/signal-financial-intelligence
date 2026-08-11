export function MobileGate() {
  return (
    <div
      style={{
        minHeight: "100vh",
        background: "var(--bg-primary)",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: 24,
        textAlign: "center",
      }}
    >
      <div
        className="mono"
        style={{
          color: "var(--accent)",
          fontSize: 32,
          marginBottom: 12,
        }}
      >
        ◈
      </div>
      <h1 style={{ fontSize: 24, fontWeight: 600, marginBottom: 12 }}>
        Signal
      </h1>
      <p
        style={{
          fontSize: 16,
          color: "var(--text-secondary)",
          maxWidth: 280,
          lineHeight: 1.5,
        }}
      >
        Try Signal on your desktop today
      </p>
      <p
        style={{
          marginTop: 24,
          fontSize: 12,
          color: "var(--text-tertiary)",
        }}
      >
        signal.harthik.dev
      </p>
    </div>
  );
}
