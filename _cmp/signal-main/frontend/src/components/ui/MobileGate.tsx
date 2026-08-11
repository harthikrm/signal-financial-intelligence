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
      <svg
        width="32"
        height="32"
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        style={{ marginBottom: 12 }}
        aria-hidden
      >
        <path
          d="M4 16 C4 16 8 8 12 12 C16 16 20 8 20 8"
          stroke="white"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          fill="none"
        />
        <circle cx="4" cy="16" r="1.5" fill="white" />
        <circle cx="20" cy="8" r="1.5" fill="white" />
      </svg>
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
