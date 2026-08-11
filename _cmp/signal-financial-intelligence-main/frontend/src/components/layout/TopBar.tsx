import { motion } from "framer-motion";

import { useAppStore } from "../../store/appStore";

const tabs = [
  { id: "knowledge" as const, label: "Knowledge" },
  { id: "explore" as const, label: "Explore" },
  { id: "compare" as const, label: "Compare" },
];

export function TopBar() {
  const activeTab = useAppStore((s) => s.activeTab);
  const setActiveTab = useAppStore((s) => s.setActiveTab);

  return (
    <header
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        height: 56,
        zIndex: 40,
        borderBottom: "0.5px solid var(--border)",
        background: "rgba(0,0,0,0.8)",
        backdropFilter: "blur(12px)",
        WebkitBackdropFilter: "blur(12px)",
      }}
    >
      <div
        style={{
          height: "100%",
          display: "flex",
          alignItems: "center",
          gap: 28,
          padding: "0 20px",
        }}
      >
        <div
          className="mono"
          style={{
            color: "var(--accent)",
            fontWeight: 600,
            fontSize: 15,
            letterSpacing: "-0.02em",
          }}
        >
          ◈ Signal
        </div>
        <nav style={{ display: "flex", alignItems: "center", gap: 4 }}>
          {tabs.map((t) => {
            const active = activeTab === t.id;
            return (
              <button
                key={t.id}
                type="button"
                onClick={() => setActiveTab(t.id)}
                style={{
                  position: "relative",
                  background: "transparent",
                  border: "none",
                  cursor: "pointer",
                  padding: "10px 14px",
                  fontSize: 13,
                  fontWeight: 500,
                  color: active ? "var(--text-primary)" : "var(--text-secondary)",
                  transition: "color 120ms ease",
                }}
              >
                {t.label}
                {active && (
                  <motion.div
                    layoutId="tab-indicator"
                    transition={{ type: "spring", stiffness: 520, damping: 38 }}
                    style={{
                      position: "absolute",
                      left: 8,
                      right: 8,
                      bottom: 4,
                      height: 2,
                      borderRadius: 1,
                      background: "var(--accent)",
                    }}
                  />
                )}
              </button>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
