import { useEffect, useRef } from "react";

export type IndicatorKind = "RSI" | "MACD" | "STOCH";

interface Props {
  symbol: string;
  indicator: IndicatorKind;
  height?: number;
}

export default function SingleIndicatorWidget({
  symbol,
  indicator,
  height = 250,
}: Props) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current || !symbol) return;

    containerRef.current.innerHTML = "";

    const script = document.createElement("script");
    script.src =
      "https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js";
    script.async = true;
    script.innerHTML = JSON.stringify({
      symbol,
      interval: "D",
      width: "100%",
      height,
      theme: "dark",
      style: "1",
      locale: "en",
      backgroundColor: "#000000",
      hide_top_toolbar: true,
      hide_legend: false,
      save_image: false,
      studies: [indicator],
      isTransparent: false,
    });

    containerRef.current.appendChild(script);

    return () => {
      if (containerRef.current) {
        containerRef.current.innerHTML = "";
      }
    };
  }, [symbol, indicator, height]);

  return (
    <div
      className="tradingview-widget-container"
      ref={containerRef}
      style={{ height: `${height}px`, width: "100%", minWidth: 0 }}
    />
  );
}
