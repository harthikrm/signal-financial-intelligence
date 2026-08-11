import { useEffect, useRef } from "react"

interface Props {
  symbol: string
  height?: number
}

export default function TechnicalPanel({ symbol, height = 400 }: Props) {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!containerRef.current || !symbol) return

    containerRef.current.innerHTML = ""

    const script = document.createElement("script")
    script.src = "https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js"
    script.async = true
    script.innerHTML = JSON.stringify({
      interval: "1D",
      width: "100%",
      height,
      symbol: symbol,
      showIntervalTabs: false,
      locale: "en",
      colorTheme: "dark",
      isTransparent: true,
    })

    containerRef.current.appendChild(script)

    return () => {
      if (containerRef.current) {
        containerRef.current.innerHTML = ""
      }
    }
  }, [symbol, height])

  return (
    <div
      className="tradingview-widget-container"
      ref={containerRef}
      style={{ height: `${height}px`, width: "100%" }}
    />
  )
}
