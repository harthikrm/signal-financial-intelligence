import { useAppStore } from "../../store/appStore";

export function ChatHistory() {
  const chatHistory = useAppStore((s) => s.chatHistory);

  return (
    <div
      style={{
        flex: 1,
        overflowY: "auto",
        display: "flex",
        flexDirection: "column",
        gap: 14,
        paddingRight: 4,
      }}
    >
      {chatHistory.map((m, i) => (
        <div
          key={i}
          style={{
            alignSelf: m.role === "user" ? "flex-end" : "flex-start",
            maxWidth: "92%",
          }}
        >
          <div
            style={{
              padding: "10px 14px",
              borderRadius: 12,
              background:
                m.role === "user" ? "var(--bg-tertiary)" : "var(--bg-secondary)",
              border: "0.5px solid var(--border)",
              color: "var(--text-primary)",
              fontSize: 14,
              lineHeight: 1.5,
              whiteSpace: "pre-wrap",
            }}
          >
            {m.content}
          </div>
          {m.role === "assistant" && m.sources.length > 0 && (
            <div
              style={{
                marginTop: 6,
                fontSize: 11,
                color: "var(--text-tertiary)",
              }}
            >
              Sources: {m.sources.join(" · ")}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
