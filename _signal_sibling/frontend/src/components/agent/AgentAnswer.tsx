import type { Components } from "react-markdown";
import ReactMarkdown from "react-markdown";
import rehypeKatex from "rehype-katex";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import "katex/dist/katex.min.css";

import { formatCitationPill } from "../../lib/formatCitationPill";
import type { AgentMessage } from "../../types/agent";
import {
  markdownComponents,
  normalizeMathDelimiters,
} from "../knowledge/MessageBubble";

interface Props {
  message: AgentMessage;
}

function stripTrailingSourcesBlock(content: string): string {
  const marker = content.search(/\n\*\*Sources\*\*/i);
  if (marker === -1) return content;
  return content.slice(0, marker).trimEnd();
}

export function AgentAnswer({ message }: Props) {
  const pills = [
    ...new Set(
      message.citations.map(formatCitationPill).filter((p) => p.length > 0)
    ),
  ];
  const body = stripTrailingSourcesBlock(message.content);

  return (
    <div style={{ alignSelf: "flex-start", maxWidth: "92%" }}>
      <div
        style={{
          padding: "10px 14px",
          borderRadius: 12,
          background: "var(--bg-secondary)",
          border: "0.5px solid var(--border)",
          color: "var(--text-primary)",
          fontSize: 14,
          lineHeight: 1.55,
        }}
      >
        <div className="markdown-body">
          <ReactMarkdown
            remarkPlugins={[remarkGfm, [remarkMath, { singleDollarTextMath: false }]]}
            rehypePlugins={[rehypeKatex]}
            components={markdownComponents as Components}
          >
            {normalizeMathDelimiters(body)}
          </ReactMarkdown>
        </div>
      </div>
      {pills.length > 0 && (
        <div style={{ marginTop: 10 }}>
          <div className="source-label">Sources</div>
          <div className="source-pills">
            {pills.map((pill) => (
              <span
                key={pill}
                className="source-pill"
                style={{
                  background: "rgba(255,255,255,0.06)",
                  border: "0.5px solid rgba(255,255,255,0.12)",
                  fontSize: 11,
                  fontFamily: "var(--font-mono)",
                  padding: "2px 8px",
                  borderRadius: 4,
                }}
              >
                {pill}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
