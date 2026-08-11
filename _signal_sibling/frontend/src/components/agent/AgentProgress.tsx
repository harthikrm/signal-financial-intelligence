import type { AgentProgress as Progress } from "../../types/agent";

interface Props {
  progress: Progress;
}

const STAGE_LABEL: Record<Progress["stage"], string> = {
  idle: "",
  planning: "Planning tool calls",
  tools: "Running tools against database",
  verifying: "Verifying data coverage",
  synthesizing: "Synthesizing answer",
  done: "Complete",
};

export function AgentProgress({ progress }: Props) {
  if (progress.stage === "idle") return null;

  const label = STAGE_LABEL[progress.stage];

  return (
    <div
      style={{
        padding: "10px 14px",
        borderRadius: 12,
        border: "0.5px solid var(--border)",
        background: "var(--bg-secondary)",
        fontSize: 13,
        color: "var(--text-secondary)",
        lineHeight: 1.5,
      }}
    >
      <div style={{ color: "var(--text-primary)", fontWeight: 500 }}>{label}</div>
      {progress.planTools && progress.planTools.length > 0 && (
        <div style={{ marginTop: 6, fontFamily: "var(--font-mono)", fontSize: 12 }}>
          Tools: {progress.planTools.join(", ")}
        </div>
      )}
      {progress.stage === "tools" && progress.toolCount != null && (
        <div style={{ marginTop: 4, fontSize: 12 }}>
          {progress.toolCount} result{progress.toolCount === 1 ? "" : "s"} collected
        </div>
      )}
      {progress.stage === "verifying" && progress.verificationGaps && (
        <div style={{ marginTop: 4, fontSize: 12, fontStyle: "italic" }}>
          {progress.verificationGaps}
        </div>
      )}
    </div>
  );
}
