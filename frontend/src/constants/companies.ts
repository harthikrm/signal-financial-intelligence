/**
 * TradingView expects "EXCHANGE:TICKER". Exchange comes from the API (companies.exchange).
 */
export function getTradingViewSymbol(ticker: string, exchange: string): string {
  if (ticker === "BRK.B") {
    return "NYSE:BRK.B";
  }
  const ex = exchange.trim();
  return `${ex}:${ticker}`;
}
