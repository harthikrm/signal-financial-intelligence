import { useEffect, useRef } from "react"

interface Props {
  symbol: string
}

export default function TechnicalPanel({ symbol }: Props) {
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
      height: 400,
      symbol: symbol,
      showIntervalTabs: true,
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
  }, [symbol])

  return (
    <div
      className="tradingview-widget-container"
      ref={containerRef}
      style={{ height: "400px", width: "100%" }}
    />
  )
}
