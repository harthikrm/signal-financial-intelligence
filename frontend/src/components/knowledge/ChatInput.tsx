import { useCallback, useEffect, useRef, useState } from "react";

interface Props {
  onSend: (question: string) => void;
  isLoading: boolean;
  placeholder?: string;
}

/** Match send button height so placeholder sits optically centered. */
const CONTROL_H = 36;
const LINE_H = 20;

export function ChatInput({
  onSend,
  isLoading,
  placeholder = "Ask anything about markets, companies, or filings...",
}: Props) {
  const [value, setValue] = useState("");
  const ta = useRef<HTMLTextAreaElement>(null);
  const isEmpty = !value.trim();

  const resize = useCallback(() => {
    const el = ta.current;
    if (!el) return;
    if (!el.value) {
      el.style.height = `${CONTROL_H}px`;
      return;
    }
    el.style.height = "auto";
    el.style.height = `${Math.min(Math.max(el.scrollHeight, CONTROL_H), 120)}px`;
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
        alignItems: "center",
        border: "0.5px solid var(--border)",
        borderRadius: 12,
        padding: "8px 10px",
        background: "var(--bg-secondary)",
        boxSizing: "border-box",
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
          // Single-line: line-height = control height centers placeholder text.
          // Multi-line: normal leading + grow with content.
          lineHeight: isEmpty ? `${CONTROL_H}px` : `${LINE_H}px`,
          height: CONTROL_H,
          minHeight: CONTROL_H,
          maxHeight: 120,
          padding: 0,
          margin: 0,
          boxSizing: "border-box",
          fontFamily: "var(--font-display)",
          overflowY: "auto",
          display: "block",
        }}
      />
      <button
        type="button"
        disabled={disabled}
        onClick={submit}
        style={{
          flexShrink: 0,
          width: CONTROL_H,
          height: CONTROL_H,
          borderRadius: 8,
          border: "none",
          cursor: disabled ? "default" : "pointer",
          background: "var(--accent)",
          color: "#000",
          fontWeight: 700,
          opacity: disabled ? 0.35 : 1,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: 0,
          lineHeight: 1,
        }}
        aria-label="Send"
      >
        ↑
      </button>
    </div>
  );
}
