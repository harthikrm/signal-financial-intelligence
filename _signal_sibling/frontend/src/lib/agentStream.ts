import type { AgentStreamHandlers } from "../types/agent";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";
const API_KEY = import.meta.env.VITE_SIGNAL_KEY || "";

interface ParsedEvent {
  event: string;
  data: string;
}

function parseSseChunk(buffer: string): { events: ParsedEvent[]; rest: string } {
  const events: ParsedEvent[] = [];
  const blocks = buffer.split("\n\n");
  const rest = blocks.pop() ?? "";

  for (const block of blocks) {
    if (!block.trim()) continue;
    let event = "message";
    const dataLines: string[] = [];
    for (const line of block.split("\n")) {
      if (line.startsWith("event:")) {
        event = line.slice(6).trim();
      } else if (line.startsWith("data:")) {
        dataLines.push(line.slice(5).trim());
      }
    }
    if (dataLines.length) {
      events.push({ event, data: dataLines.join("\n") });
    }
  }

  return { events, rest };
}

function dispatchEvent(event: string, raw: string, handlers: AgentStreamHandlers) {
  let data: Record<string, unknown> = {};
  try {
    data = JSON.parse(raw) as Record<string, unknown>;
  } catch {
    data = { message: raw };
  }

  switch (event) {
    case "status":
      handlers.onStatus?.(data as { stage?: string; model_used?: string });
      break;
    case "plan":
      handlers.onPlan?.(
        data as {
          plan?: { name: string; args?: Record<string, unknown> }[];
          reasoning?: string;
        }
      );
      break;
    case "tools":
      handlers.onTools?.(data as { tool_results?: unknown[] });
      break;
    case "verify":
      handlers.onVerify?.(
        data as { verification?: { sufficient?: boolean; gaps?: string } }
      );
      break;
    case "done":
      handlers.onDone?.(
        data as { answer?: string; citations?: string[]; model_used?: string }
      );
      break;
    case "error":
      handlers.onError?.(data as { message?: string });
      break;
    default:
      break;
  }
}

export async function streamAgent(
  question: string,
  handlers: AgentStreamHandlers,
  signal?: AbortSignal
): Promise<void> {
  const res = await fetch(`${API_BASE}/api/agent/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Signal-Key": API_KEY,
    },
    body: JSON.stringify({ question }),
    signal,
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(text || `Agent stream failed (${res.status})`);
  }

  const reader = res.body?.getReader();
  if (!reader) {
    throw new Error("No response body from agent stream");
  }

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    const { events, rest } = parseSseChunk(buffer);
    buffer = rest;
    for (const ev of events) {
      dispatchEvent(ev.event, ev.data, handlers);
    }
  }

  if (buffer.trim()) {
    const { events } = parseSseChunk(`${buffer}\n\n`);
    for (const ev of events) {
      dispatchEvent(ev.event, ev.data, handlers);
    }
  }
}
