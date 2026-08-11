import { useMemo } from "react";
import { createPortal } from "react-dom";

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
        position: "relative",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        width: "100%",
        minHeight: 0,
      }}
    >
      {showStarters &&
        createPortal(
          <div className="knowledge-empty-state">
            <div className="knowledge-empty-state-content">
              <div>
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
                <p
                  style={{
                    marginTop: 12,
                    fontSize: 13,
                    color: "var(--text-secondary)",
                  }}
                >
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
          </div>,
          document.body
        )}

      <div className="knowledge-scroll">
        {!showStarters && (
          <div
            className="knowledge-scroll-inner"
            style={{
              display: "flex",
              flexDirection: "column",
              gap: 14,
              minHeight: 0,
            }}
          >
            <ChatHistory />
            {isLoading && (
              <div style={{ padding: "4px 0" }}>
                <LoadingDots />
              </div>
            )}
          </div>
        )}
      </div>

      <div className="knowledge-composer">
        <div className="knowledge-composer-inner">
          <ChatInput onSend={(q) => void sendMessage(q)} isLoading={isLoading} />
        </div>
        <Disclaimer />
      </div>
    </div>
  );
}
