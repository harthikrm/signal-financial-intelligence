import { useState, type ReactNode } from "react";

import { metricByKey } from "../../constants/metrics";

export function MetricTooltip({
  metricKey,
  children,
}: {
  metricKey: string;
  children: ReactNode;
}) {
  const [open, setOpen] = useState(false);
  const def = metricByKey(metricKey);

  return (
    <span
      style={{ position: "relative", display: "inline-block" }}
      onMouseEnter={() => setOpen(true)}
      onMouseLeave={() => setOpen(false)}
    >
      {children}
      {open && def && (
        <div
          style={{
            position: "absolute",
            bottom: "100%",
            left: "50%",
            transform: "translateX(-50%)",
            marginBottom: 8,
            minWidth: 200,
            maxWidth: 280,
            padding: "10px 12px",
            borderRadius: 8,
            background: "var(--bg-elevated)",
            border: "0.5px solid var(--border)",
            fontSize: 12,
            color: "var(--text-secondary)",
            zIndex: 50,
            pointerEvents: "none",
            boxShadow: "0 8px 24px rgba(0,0,0,0.45)",
          }}
        >
          <div style={{ fontWeight: 600, color: "var(--text-primary)", marginBottom: 4 }}>
            {def.label}
            {def.unit ? ` (${def.unit})` : ""}
          </div>
          <div>{def.description}</div>
        </div>
      )}
    </span>
  );
}
