import { useCallback, useRef, useState } from "react";

import { streamAgent } from "../lib/agentStream";
import { useAppStore } from "../store/appStore";
import type { AgentProgress, AgentStage } from "../types/agent";

const idleProgress = (): AgentProgress => ({ stage: "idle" });

export function useAgent() {
  const [isLoading, setIsLoading] = useState(false);
  const [progress, setProgress] = useState<AgentProgress>(idleProgress);
  const abortRef = useRef<AbortController | null>(null);
  const addAgentMessage = useAppStore((s) => s.addAgentMessage);

  const setStage = (stage: AgentStage, patch: Partial<AgentProgress> = {}) => {
    setProgress({ stage, ...patch });
  };

  const sendMessage = useCallback(
    async (question: string) => {
      abortRef.current?.abort();
      const controller = new AbortController();
      abortRef.current = controller;

      addAgentMessage({ role: "user", content: question, citations: [] });
      setIsLoading(true);
      setStage("planning");

      try {
        await streamAgent(
          question,
          {
            onStatus: () => setStage("planning"),
            onPlan: (data) => {
              const planTools = (data.plan ?? []).map((p) => p.name);
              setStage("planning", {
                planTools,
                planReasoning: data.reasoning,
              });
            },
            onTools: (data) => {
              setStage("tools", {
                toolCount: data.tool_results?.length ?? 0,
              });
            },
            onVerify: (data) => {
              setStage("verifying", {
                verificationGaps: data.verification?.gaps,
              });
            },
            onDone: (data) => {
              setStage("synthesizing");
              addAgentMessage({
                role: "assistant",
                content:
                  data.answer?.trim() ||
                  "No answer was returned. Please try again.",
                citations: data.citations ?? [],
              });
              setStage("done");
            },
            onError: (data) => {
              addAgentMessage({
                role: "assistant",
                content:
                  data.message ||
                  "Something went wrong while running the agent.",
                citations: [],
              });
            },
          },
          controller.signal
        );
      } catch (err) {
        if ((err as Error).name === "AbortError") return;
        addAgentMessage({
          role: "assistant",
          content: "We could not reach Signal just now. Please try again.",
          citations: [],
        });
      } finally {
        setIsLoading(false);
        setProgress(idleProgress());
        abortRef.current = null;
      }
    },
    [addAgentMessage]
  );

  const cancel = useCallback(() => {
    abortRef.current?.abort();
    setIsLoading(false);
    setProgress(idleProgress());
  }, []);

  return { sendMessage, isLoading, progress, cancel };
}
