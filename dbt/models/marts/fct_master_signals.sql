WITH metrics AS (
    SELECT * FROM {{ ref('fct_company_metrics') }}
),
indicators AS (
    SELECT * FROM {{ ref('fct_price_indicators') }}
    WHERE date = (SELECT MAX(date) FROM {{ ref('fct_price_indicators') }})
),
latest_metrics AS (
    SELECT DISTINCT ON (ticker) *
    FROM metrics
    WHERE period_type = 'annual'
    ORDER BY ticker, period_end DESC
)

SELECT
    m.ticker,
    i.rsi_14,
    m.revenue_growth,
    m.net_margin,
    CASE
        WHEN i.rsi_14 < 30 AND m.revenue_growth > 20
            THEN 'STRONG_BUY_OPPORTUNITY'
        WHEN i.sma_50 > i.sma_200 AND m.net_margin > 20
            THEN 'QUALITY_MOMENTUM'
        WHEN i.rsi_14 > 70 AND m.revenue_growth < 0
            THEN 'RISK_EXIT'
        ELSE 'MONITOR'
    END AS master_signal,
    NOW() AS computed_at
FROM latest_metrics m
LEFT JOIN indicators i ON m.ticker = i.ticker
