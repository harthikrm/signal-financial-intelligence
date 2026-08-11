import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useState } from "react";

import { CompareView } from "./components/compare/CompareView";
import { ExploreView } from "./components/explore/ExploreView";
import { KnowledgeView } from "./components/knowledge/KnowledgeView";
import { StatusBar } from "./components/layout/StatusBar";
import { TopBar } from "./components/layout/TopBar";
import { MobileGate } from "./components/ui/MobileGate";
import { useAppStore } from "./store/appStore";

function useDesktop(min: number) {
  const [ok, setOk] = useState(
    typeof window !== "undefined" ? window.innerWidth >= min : true
  );
  useEffect(() => {
    const on = () => setOk(window.innerWidth >= min);
    on();
    window.addEventListener("resize", on);
    return () => window.removeEventListener("resize", on);
  }, [min]);
  return ok;
}

export default function App() {
  const desktop = useDesktop(1024);
  const activeTab = useAppStore((s) => s.activeTab);

  if (!desktop) {
    return <MobileGate />;
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        background: "var(--bg-primary)",
      }}
    >
      <TopBar />
      <main
        style={{
          flex: 1,
          marginTop: 56,
          marginBottom: 36,
          minHeight: 0,
          overflow: "hidden",
          display: "flex",
          flexDirection: "column",
        }}
      >
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.12 }}
            style={{
              flex: 1,
              minHeight: 0,
              display: "flex",
              flexDirection: "column",
            }}
          >
            {activeTab === "knowledge" && <KnowledgeView />}
            {activeTab === "explore" && <ExploreView />}
            {activeTab === "compare" && <CompareView />}
          </motion.div>
        </AnimatePresence>
      </main>
      <StatusBar />
    </div>
  );
}
