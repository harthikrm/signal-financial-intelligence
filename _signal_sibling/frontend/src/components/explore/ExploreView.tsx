import { useMemo } from "react";
import { createPortal } from "react-dom";

import { getTradingViewSymbol } from "../../constants/companies";
import { useCompany } from "../../hooks/useCompany";
import { useMetrics } from "../../hooks/useMetrics";
import { usePriceSnapshot } from "../../hooks/usePriceSnapshot";
import { useAppStore } from "../../store/appStore";
import { ErrorMessage } from "../ui/ErrorMessage";
import { Spinner } from "../ui/Spinner";
import { ExploreStickySearch } from "./ExploreStickySearch";
import { LeftPanel } from "./LeftPanel";
import { MetricsGrid } from "./MetricsGrid";
import AdvancedChartWithStudies from "./AdvancedChartWithStudies";
import CompanyProfileWidget from "./CompanyProfileWidget";
import NewsWidget from "./NewsWidget";
import TechnicalGaugeWidget from "./TechnicalGaugeWidget";
import { TickerSearch } from "./TickerSearch";
import TradingViewWidget from "./TradingViewWidget";

const SectionHeader = ({ title }: { title: string }) => (
  <div
    style={{
      display: "flex",
      alignItems: "center",
      gap: "12px",
      padding: "32px 24px 20px",
      borderTop: "0.5px solid rgba(255,255,255,0.08)",
      marginTop: "8px",
    }}
  >
    <div
      style={{
        width: "4px",
        height: "22px",
        background: "#60a5fa",
        borderRadius: "2px",
        flexShrink: 0,
      }}
    />
    <span
      style={{
        fontSize: "18px",
        fontWeight: 600,
        color: "rgba(255,255,255,0.9)",
        letterSpacing: "0.01em",
      }}
    >
      {title}
    </span>
    <div
      style={{
        flex: 1,
        height: "0.5px",
        background: "rgba(255,255,255,0.08)",
        marginLeft: "8px",
      }}
    />
  </div>
);

export function ExploreView() {
  const activeTicker = useAppStore((s) => s.activeTicker);
  const setActiveTicker = useAppStore((s) => s.setActiveTicker);
  const { data: snap, isLoading: snapLoading, error: snapErr, exchangeByTicker } =
    usePriceSnapshot();
  const { data: company } = useCompany(activeTicker);
  const { data: metrics, isLoading: mLoading, error: mErr } = useMetrics(activeTicker);

  const tradingViewSymbol = useMemo(() => {
    if (!activeTicker) return null;
    const exchange = exchangeByTicker[activeTicker];
    if (!exchange) return null;
    return getTradingViewSymbol(activeTicker, exchange);
  }, [activeTicker, exchangeByTicker]);

  const snapRow = snap?.find((r) => r.ticker === activeTicker);
  const metricData = metrics?.data ?? {};
  const companies = snap ?? [];

  if (!activeTicker) {
    return (
      <>
        {createPortal(
          <div className="explore-empty">
            {snapLoading && <Spinner />}
            {snapErr && <ErrorMessage />}
            <TickerSearch
              mode="empty"
              sticky={false}
              companies={companies}
              onSelect={(ticker) => setActiveTicker(ticker)}
            />
          </div>,
          document.body
        )}
      </>
    );
  }

  return (
    <div className="explore-detail">
      <ExploreStickySearch
        ticker={activeTicker}
        companyName={company?.name ?? snapRow?.name}
        companies={companies}
        onSelect={(ticker) => setActiveTicker(ticker)}
        onClear={() => setActiveTicker(null)}
      />

      {mLoading && (
        <div style={{ padding: 48, display: "flex", justifyContent: "center" }}>
          <Spinner />
        </div>
      )}
      {mErr && (
        <div style={{ padding: 24 }}>
          <ErrorMessage />
        </div>
      )}

      {metrics && (
        <div style={{ paddingLeft: "16px", paddingRight: "16px" }}>
          <div className="explore-two-col-row">
            <LeftPanel ticker={activeTicker} />
            <div className="explore-chart-col">
              {tradingViewSymbol && (
                <TradingViewWidget symbol={tradingViewSymbol} height={480} />
              )}
            </div>
          </div>

          {tradingViewSymbol && (
            <>
              <SectionHeader title="Market Intelligence" />

              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "1fr 360px",
                  gap: "1px",
                  background: "rgba(255,255,255,0.06)",
                  width: "100%",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: "1px",
                    background: "rgba(255,255,255,0.06)",
                  }}
                >
                  <div
                    style={{
                      display: "grid",
                      gridTemplateColumns: "1fr 1fr 1fr",
                      gap: "1px",
                      background: "rgba(255,255,255,0.06)",
                    }}
                  >
                    <div style={{ background: "#000", padding: "12px 0 0" }}>
                      <div
                        style={{
                          padding: "0 16px 8px",
                          fontSize: "11px",
                          color: "rgba(255,255,255,0.35)",
                          textTransform: "uppercase",
                          letterSpacing: "0.05em",
                        }}
                      >
                        Daily
                      </div>
                      <TechnicalGaugeWidget
                        symbol={tradingViewSymbol}
                        interval="1D"
                        height={420}
                      />
                    </div>
                    <div style={{ background: "#000", padding: "12px 0 0" }}>
                      <div
                        style={{
                          padding: "0 16px 8px",
                          fontSize: "11px",
                          color: "rgba(255,255,255,0.35)",
                          textTransform: "uppercase",
                          letterSpacing: "0.05em",
                        }}
                      >
                        Weekly
                      </div>
                      <TechnicalGaugeWidget
                        symbol={tradingViewSymbol}
                        interval="1W"
                        height={420}
                      />
                    </div>
                    <div style={{ background: "#000", padding: "12px 0 0" }}>
                      <div
                        style={{
                          padding: "0 16px 8px",
                          fontSize: "11px",
                          color: "rgba(255,255,255,0.35)",
                          textTransform: "uppercase",
                          letterSpacing: "0.05em",
                        }}
                      >
                        Company Profile
                      </div>
                      <CompanyProfileWidget symbol={tradingViewSymbol} height={420} />
                    </div>
                  </div>

                  <div style={{ background: "#000" }}>
                    <div
                      style={{
                        padding: "12px 16px 8px",
                        fontSize: "11px",
                        color: "rgba(255,255,255,0.35)",
                        textTransform: "uppercase",
                        letterSpacing: "0.05em",
                        borderTop: "0.5px solid rgba(255,255,255,0.06)",
                      }}
                    >
                      Price · RSI · MACD
                    </div>
                    <div style={{ height: "700px", width: "100%" }}>
                      <AdvancedChartWithStudies
                        symbol={tradingViewSymbol}
                        height={700}
                      />
                    </div>
                  </div>
                </div>

                <div style={{ background: "#000", minHeight: "920px" }}>
                  <NewsWidget symbol={tradingViewSymbol} />
                </div>
              </div>
            </>
          )}

          <SectionHeader title="Fundamental Metrics" />
          <MetricsGrid data={metricData} />
        </div>
      )}
    </div>
  );
}
