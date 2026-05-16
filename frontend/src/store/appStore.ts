import { create } from "zustand";

export type TabId = "knowledge" | "explore" | "compare";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  sources: string[];
}

interface AppState {
  activeTab: TabId;
  setActiveTab: (tab: TabId) => void;
  activeTicker: string | null;
  setActiveTicker: (ticker: string | null) => void;
  compareTickets: string[];
  addCompareTicker: (ticker: string) => void;
  removeCompareTicker: (ticker: string) => void;
  swapCompareTicker: (index: number, ticker: string) => void;
  chatHistory: ChatMessage[];
  addChatMessage: (msg: ChatMessage) => void;
  clearChat: () => void;
  sessionId: string;
}

const newSessionId = (): string => {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `sess-${Date.now()}`;
};

export const useAppStore = create<AppState>((set, get) => ({
  activeTab: "knowledge",
  setActiveTab: (tab) => set({ activeTab: tab }),
  activeTicker: null,
  setActiveTicker: (ticker) => set({ activeTicker: ticker }),
  compareTickets: [],
  addCompareTicker: (ticker) => {
    const u = ticker.toUpperCase().trim();
    if (!u) return;
    const cur = get().compareTickets;
    if (cur.length >= 3) return;
    if (cur.includes(u)) return;
    set({ compareTickets: [...cur, u] });
  },
  removeCompareTicker: (ticker) =>
    set({
      compareTickets: get().compareTickets.filter(
        (t) => t !== ticker.toUpperCase()
      ),
    }),
  swapCompareTicker: (index, ticker) =>
    set({
      compareTickets: get().compareTickets.map((t, i) =>
        i === index ? ticker.toUpperCase().trim() : t
      ),
    }),
  chatHistory: [],
  addChatMessage: (msg) =>
    set((s) => {
      const next = [...s.chatHistory, msg];
      const maxExchanges = 6;
      const maxMessages = maxExchanges * 2;
      return {
        chatHistory:
          next.length > maxMessages ? next.slice(next.length - maxMessages) : next,
      };
    }),
  clearChat: () => set({ chatHistory: [] }),
  sessionId: newSessionId(),
}));
