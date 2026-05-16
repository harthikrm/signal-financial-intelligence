interface Props {
  questions: string[];
  onSelect: (q: string) => void;
}

export function SuggestedQuestions({ questions, onSelect }: Props) {
  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "1fr 1fr",
        gap: 12,
        maxWidth: 560,
        width: "100%",
      }}
    >
      {questions.map((q) => (
        <button
          key={q}
          type="button"
          onClick={() => onSelect(q)}
          style={{
            textAlign: "left",
            padding: "12px 16px",
            borderRadius: 12,
            border: "0.5px solid var(--border)",
            background: "var(--bg-secondary)",
            color: "var(--text-secondary)",
            fontSize: 12,
            lineHeight: 1.45,
            cursor: "pointer",
            transition: "background 120ms ease, color 120ms ease",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = "var(--bg-tertiary)";
            e.currentTarget.style.color = "var(--text-primary)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = "var(--bg-secondary)";
            e.currentTarget.style.color = "var(--text-secondary)";
          }}
        >
          {q}
        </button>
      ))}
    </div>
  );
}
