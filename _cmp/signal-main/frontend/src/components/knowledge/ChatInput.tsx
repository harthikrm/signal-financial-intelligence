import { useCallback, useEffect, useRef, useState } from "react";

interface Props {
  onSend: (question: string) => void;
  isLoading: boolean;
  placeholder?: string;
}

export function ChatInput({
  onSend,
  isLoading,
  placeholder = "Ask anything about markets, companies, or filings...",
}: Props) {
  const [value, setValue] = useState("");
  const ta = useRef<HTMLTextAreaElement>(null);

  const resize = useCallback(() => {
    const el = ta.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 120)}px`;
  }, []);

  useEffect(() => {
    resize();
  }, [value, resize]);

  const submit = () => {
    const q = value.trim();
    if (!q || isLoading) return;
    onSend(q);
    setValue("");
  };

  const disabled = isLoading || !value.trim();

  return (
    <div
      style={{
        display: "flex",
        gap: 10,
        alignItems: "flex-end",
        border: "0.5px solid var(--border)",
        borderRadius: 12,
        padding: "8px 10px",
        background: "var(--bg-secondary)",
      }}
    >
      <textarea
        ref={ta}
        rows={1}
        value={value}
        disabled={isLoading}
        placeholder={placeholder}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            submit();
          }
        }}
        style={{
          flex: 1,
          resize: "none",
          border: "none",
          outline: "none",
          background: "transparent",
          color: "var(--text-primary)",
          fontSize: 14,
          lineHeight: 1.45,
          maxHeight: 120,
          fontFamily: "var(--font-display)",
        }}
      />
      <button
        type="button"
        className="chat-send-btn"
        disabled={disabled}
        onClick={submit}
        style={{
          width: 36,
          height: 36,
          borderRadius: 8,
          border: "none",
          cursor: disabled ? "default" : "pointer",
          fontWeight: 700,
        }}
        aria-label="Send"
      >
        ↑
      </button>
    </div>
  );
}
