import { motion } from "framer-motion";

import { useAppStore } from "../../store/appStore";

const tabs = [
  { id: "knowledge" as const, label: "Knowledge" },
  { id: "agent" as const, label: "Agent" },
  { id: "explore" as const, label: "Explore" },
  { id: "compare" as const, label: "Compare" },
];

function SignalLogo() {
  return (
    <svg
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden
    >
      <path
        d="M4 16 C4 16 8 8 12 12 C16 16 20 8 20 8"
        stroke="white"
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
      />
      <circle cx="4" cy="16" r="1.5" fill="white" />
      <circle cx="20" cy="8" r="1.5" fill="white" />
    </svg>
  );
}

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
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
          }}
        >
          <SignalLogo />
          <span
            className="mono"
            style={{
              color: "#ffffff",
              fontWeight: 600,
              fontSize: 15,
              letterSpacing: "-0.02em",
            }}
          >
            Signal
          </span>
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
                      background: "#60a5fa",
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
