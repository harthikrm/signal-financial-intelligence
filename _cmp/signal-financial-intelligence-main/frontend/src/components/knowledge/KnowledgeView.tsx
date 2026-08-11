import { useMemo } from "react";

import { KNOWLEDGE_STARTERS } from "../../constants/starters";
import { PIONEER_QUOTES } from "../../constants/quotes";
import { useChat } from "../../hooks/useChat";
import { useAppStore } from "../../store/appStore";
import { Disclaimer } from "../ui/Disclaimer";
import { LoadingDots } from "../ui/LoadingDots";
import { ChatHistory } from "./ChatHistory";
import { ChatInput } from "./ChatInput";
import { SuggestedQuestions } from "./SuggestedQuestions";

export function KnowledgeView() {
  const chatHistory = useAppStore((s) => s.chatHistory);
  const quote = useMemo(
    () => PIONEER_QUOTES[Math.floor(Math.random() * PIONEER_QUOTES.length)],
    []
  );
  const { sendMessage, isLoading } = useChat();

  const showStarters = chatHistory.length === 0;

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        height: "100%",
        maxWidth: 800,
        width: "100%",
        margin: "0 auto",
        padding: "12px 16px 0",
        minHeight: 0,
      }}
    >
      {showStarters ? (
        <div
          style={{
            flex: 1,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            textAlign: "center",
            gap: 32,
            minHeight: 0,
          }}
        >
          <div style={{ maxWidth: 560 }}>
            <p
              style={{
                fontSize: 18,
                fontStyle: "italic",
                color: "var(--text-primary)",
                lineHeight: 1.5,
              }}
            >
              {quote.text}
            </p>
            <p style={{ marginTop: 12, fontSize: 13, color: "var(--text-secondary)" }}>
              — {quote.author}
            </p>
          </div>
          <SuggestedQuestions
            questions={KNOWLEDGE_STARTERS}
            onSelect={(q) => {
              void sendMessage(q);
            }}
          />
        </div>
      ) : (
        <div style={{ flex: 1, display: "flex", flexDirection: "column", minHeight: 0 }}>
          <ChatHistory />
          {isLoading && (
            <div style={{ padding: "8px 0" }}>
              <LoadingDots />
            </div>
          )}
        </div>
      )}

      <div style={{ padding: "12px 0 8px", flexShrink: 0 }}>
        <ChatInput onSend={(q) => void sendMessage(q)} isLoading={isLoading} />
        <Disclaimer />
      </div>
    </div>
  );
}
