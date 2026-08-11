import { useEffect, useRef } from "react";

interface Props {
  symbol: string;
  height?: number;
  sidebar?: boolean;
}

export default function NewsWidget({
  symbol,
  height = 550,
  sidebar = false,
}: Props) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current || !symbol) return;
    containerRef.current.innerHTML = "";

    const script = document.createElement("script");
    script.src =
      "https://s3.tradingview.com/external-embedding/embed-widget-timeline.js";
    script.async = true;
    script.innerHTML = JSON.stringify({
      feedMode: "symbol",
      symbol: symbol,
      isTransparent: true,
      displayMode: "regular",
      width: "100%",
      height,
      colorTheme: "dark",
      locale: "en",
    });

    containerRef.current.appendChild(script);

    return () => {
      if (containerRef.current) {
        containerRef.current.innerHTML = "";
      }
    };
  }, [symbol, height]);

  return (
    <div
      className={sidebar ? "explore-news-sidebar" : undefined}
      style={{ width: "100%", ...(sidebar ? {} : { marginTop: "1px" }) }}
    >
      {!sidebar && (
        <div
          style={{
            padding: "16px 24px 8px",
            fontSize: "11px",
            textTransform: "uppercase",
            letterSpacing: "0.05em",
            color: "rgba(255,255,255,0.4)",
            borderTop: "0.5px solid rgba(255,255,255,0.06)",
          }}
        >
          Latest News
        </div>
      )}
      <div
        className="tradingview-widget-container"
        ref={containerRef}
        style={{ width: "100%", height: `${height}px`, flex: sidebar ? 1 : undefined }}
      />
    </div>
  );
}
