import { useEffect, useRef } from "react";

import { useAppStore } from "../../store/appStore";
import { MessageBubble } from "./MessageBubble";

export function ChatHistory() {
  const chatHistory = useAppStore((s) => s.chatHistory);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatHistory]);

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        gap: 14,
      }}
    >
      {chatHistory.map((m, i) => (
        <MessageBubble key={i} message={m} />
      ))}
      <div ref={bottomRef} aria-hidden />
    </div>
  );
}
