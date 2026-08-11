import { useEffect, useRef } from "react";

import { useAppStore } from "../../store/appStore";
import { AgentAnswer } from "./AgentAnswer";

export function AgentChatHistory() {
  const agentHistory = useAppStore((s) => s.agentHistory);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [agentHistory]);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
      {agentHistory.map((m, i) =>
        m.role === "user" ? (
          <div
            key={i}
            style={{
              alignSelf: "flex-end",
              maxWidth: "92%",
              padding: "10px 14px",
              borderRadius: 12,
              background: "var(--bg-tertiary)",
              border: "0.5px solid var(--border)",
              color: "var(--text-primary)",
              fontSize: 14,
              lineHeight: 1.55,
              whiteSpace: "pre-wrap",
            }}
          >
            {m.content}
          </div>
        ) : (
          <AgentAnswer key={i} message={m} />
        )
      )}
      <div ref={bottomRef} aria-hidden />
    </div>
  );
}
