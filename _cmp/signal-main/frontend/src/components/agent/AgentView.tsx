import { createPortal } from "react-dom";

import { AGENT_STARTERS } from "../../constants/agentStarters";
import { useAgent } from "../../hooks/useAgent";
import { useAppStore } from "../../store/appStore";
import { Disclaimer } from "../ui/Disclaimer";
import { ChatInput } from "../knowledge/ChatInput";
import { SuggestedQuestions } from "../knowledge/SuggestedQuestions";
import { AgentChatHistory } from "./AgentChatHistory";
import { AgentProgress } from "./AgentProgress";

export function AgentView() {
  const agentHistory = useAppStore((s) => s.agentHistory);
  const { sendMessage, isLoading, progress } = useAgent();
  const showStarters = agentHistory.length === 0;

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
                <h2
                  style={{
                    fontSize: 20,
                    fontWeight: 600,
                    color: "var(--text-primary)",
                    marginBottom: 10,
                  }}
                >
                  Signal Agent
                </h2>
                <p
                  style={{
                    fontSize: 14,
                    color: "var(--text-secondary)",
                    lineHeight: 1.55,
                    maxWidth: 520,
                  }}
                >
                  Ask complex research questions. The agent plans which tools to
                  call, queries filings and financial data, verifies coverage, and
                  answers with citations.
                </p>
              </div>
              <SuggestedQuestions
                questions={AGENT_STARTERS}
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
            <AgentChatHistory />
            {isLoading && <AgentProgress progress={progress} />}
          </div>
        )}
      </div>

      <div className="knowledge-composer">
        <div className="knowledge-composer-inner">
          <ChatInput
            onSend={(q) => void sendMessage(q)}
            isLoading={isLoading}
            placeholder="Ask a multi-step research question..."
          />
        </div>
        <Disclaimer />
      </div>
    </div>
  );
}
