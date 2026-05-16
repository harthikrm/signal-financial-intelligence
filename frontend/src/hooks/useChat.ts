import { useCallback, useState } from "react";

import { api } from "../lib/api";
import { useAppStore } from "../store/appStore";
import type { ChatResponse } from "../types/chat";

export function useChat() {
  const [isLoading, setIsLoading] = useState(false);
  const sessionId = useAppStore((s) => s.sessionId);
  const addChatMessage = useAppStore((s) => s.addChatMessage);

  const sendMessage = useCallback(
    async (question: string) => {
      addChatMessage({ role: "user", content: question, sources: [] });
      const prior = useAppStore
        .getState()
        .chatHistory.slice(0, -1)
        .slice(-12)
        .map(({ role, content }) => ({ role, content }));
      setIsLoading(true);
      try {
        const { data } = await api.post<ChatResponse>("/api/chat/query", {
          question,
          history: prior,
          session_id: sessionId,
        });
        addChatMessage({
          role: "assistant",
          content: data.answer,
          sources: data.sources ?? [],
        });
      } catch {
        addChatMessage({
          role: "assistant",
          content: "We could not reach Signal just now. Please try again.",
          sources: [],
        });
      } finally {
        setIsLoading(false);
      }
    },
    [addChatMessage, sessionId]
  );

  return { sendMessage, isLoading };
}
