import type { Components } from "react-markdown";
import ReactMarkdown from "react-markdown";
import rehypeKatex from "rehype-katex";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import "katex/dist/katex.min.css";

import { formatCitationPill } from "../../lib/formatCitationPill";
import type { ChatMessage } from "../../types/chat";

interface Props {
  message: ChatMessage;
}

const LATEX_CMD_RE =
  /\\(?:text|frac|sum|int|sqrt|alpha|beta|gamma|delta|times|cdot|left|right|over|underline|mathbf|mathrm)/i;
const MATH_OPERATOR_RE = /[=+\-*/^]|\\frac|\\sum/;

function looksLikeLatex(content: string): boolean {
  const s = content.trim();
  if (!s || isDollarAmount(s) || isPlainPercentage(s)) {
    return false;
  }
  if (LATEX_CMD_RE.test(s)) {
    return true;
  }
  return MATH_OPERATOR_RE.test(s) && /[a-zA-Z]/.test(s);
}

function isDollarAmount(content: string): boolean {
  return /^\$?\d[\d,]*\.?\d*[KMBTkmbt%]*$/i.test(content.trim());
}

function isPlainPercentage(content: string): boolean {
  return /^\d[\d.,]*%$/.test(content.trim());
}

/** LLM sometimes uses bracket/paren delimiters instead of $$ / $. */
export function normalizeMathDelimiters(content: string): string {
  let out = content;

  out = out.replace(/\\\[([\s\S]*?)\\\]/g, (_, equation) => {
    const eq = String(equation).trim();
    return looksLikeLatex(eq) ? `$$\n${eq}\n$$` : `\\[${eq}\\]`;
  });

  out = out.replace(/\\\(([\s\S]*?)\\\)/g, (_, equation) => {
    const eq = String(equation).trim();
    return looksLikeLatex(eq) ? `$${eq}$` : `\\(${eq}\\)`;
  });

  out = out.replace(/^\[\s*([\s\S]*?)\s*\]$/gm, (match, equation) => {
    const eq = String(equation).trim();
    return looksLikeLatex(eq) ? `$$\n${eq}\n$$` : match;
  });

  out = out.replace(/\[\s*((?:\\.|[^\]])+)\s*\]/g, (match, equation) => {
    const eq = String(equation).trim();
    return looksLikeLatex(eq) ? `$$${eq}$$` : match;
  });

  return out;
}

/** @deprecated Use formatCitationPill from lib/formatCitationPill */
export function formatSourcePill(source: string): string {
  return formatCitationPill(source);
}

export const markdownComponents: Components = {
  ul: ({ children }) => <ul className="answer-list">{children}</ul>,
  li: ({ children }) => <li>{children}</li>,
  table: ({ children }) => (
    <div style={{ overflowX: "auto", margin: "12px 0" }}>
      <table
        style={{
          width: "100%",
          borderCollapse: "collapse",
          fontSize: "13px",
          fontFamily: "var(--font-mono)",
        }}
      >
        {children}
      </table>
    </div>
  ),
  thead: ({ children }) => (
    <thead
      style={{
        borderBottom: "1px solid rgba(255,255,255,0.15)",
      }}
    >
      {children}
    </thead>
  ),
  th: ({ children }) => (
    <th
      style={{
        padding: "8px 12px",
        textAlign: "left",
        color: "rgba(255,255,255,0.5)",
        fontSize: "11px",
        fontWeight: 500,
        textTransform: "uppercase",
        letterSpacing: "0.05em",
        whiteSpace: "nowrap",
      }}
    >
      {children}
    </th>
  ),
  td: ({ children }) => (
    <td
      style={{
        padding: "8px 12px",
        borderBottom: "0.5px solid rgba(255,255,255,0.06)",
        color: "rgba(255,255,255,0.85)",
        verticalAlign: "top",
      }}
    >
      {children}
    </td>
  ),
  tr: ({ children }) => (
    <tr
      style={{ transition: "background 0.1s" }}
      onMouseEnter={(e) => {
        e.currentTarget.style.background = "rgba(255,255,255,0.03)";
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.background = "transparent";
      }}
    >
      {children}
    </tr>
  ),
};

export function MessageBubble({ message }: Props) {
  const isUser = message.role === "user";
  const pills = message.sources.map(formatCitationPill);
  const uniquePills = [...new Set(pills)];

  return (
    <div style={{ alignSelf: isUser ? "flex-end" : "flex-start", maxWidth: "92%" }}>
      <div
        style={{
          padding: "10px 14px",
          borderRadius: 12,
          background: isUser ? "var(--bg-tertiary)" : "var(--bg-secondary)",
          border: "0.5px solid var(--border)",
          color: "var(--text-primary)",
          fontSize: 14,
          lineHeight: 1.55,
        }}
      >
        {isUser ? (
          <div style={{ whiteSpace: "pre-wrap" }}>{message.content}</div>
        ) : (
          <div className="markdown-body">
            <ReactMarkdown
              remarkPlugins={[
                remarkGfm,
                [remarkMath, { singleDollarTextMath: false }],
              ]}
              rehypePlugins={[rehypeKatex]}
              components={markdownComponents}
            >
              {normalizeMathDelimiters(message.content)}
            </ReactMarkdown>
          </div>
        )}
      </div>
      {!isUser && uniquePills.length > 0 && (
        <div style={{ marginTop: 10 }}>
          <div className="source-label">Sources</div>
          <div className="source-pills">
            {uniquePills.map((pill) => (
              <span key={pill} className="source-pill">
                {pill}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
