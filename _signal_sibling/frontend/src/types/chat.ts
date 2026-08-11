export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  sources: string[];
}

export interface ChatRequest {
  question: string;
  history: { role: string; content: string }[];
  session_id?: string | null;
}

export interface ChatResponse {
  answer: string;
  sources: string[];
  model_used: string;
}
