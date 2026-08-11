export interface AgentMessage {
  role: "user" | "assistant";
  content: string;
  citations: string[];
}

export type AgentStage =
  | "idle"
  | "planning"
  | "tools"
  | "verifying"
  | "synthesizing"
  | "done";

export interface AgentProgress {
  stage: AgentStage;
  planTools?: string[];
  planReasoning?: string;
  toolCount?: number;
  verificationGaps?: string;
}

export interface AgentStreamHandlers {
  onStatus?: (data: { stage?: string; model_used?: string }) => void;
  onPlan?: (data: {
    plan?: { name: string; args?: Record<string, unknown> }[];
    reasoning?: string;
    round?: number;
  }) => void;
  onTools?: (data: { tool_results?: unknown[]; round?: number }) => void;
  onVerify?: (data: {
    verification?: { sufficient?: boolean; gaps?: string };
  }) => void;
  onDone?: (data: {
    answer?: string;
    citations?: string[];
    model_used?: string;
  }) => void;
  onError?: (data: { message?: string }) => void;
}
