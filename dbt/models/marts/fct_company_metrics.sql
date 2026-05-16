WITH metrics AS (
    SELECT * FROM {{ ref('int_company_metrics') }}
),

max_pe AS (
    SELECT
        ticker,
        MAX(period_end) AS max_period_end
    FROM metrics
    GROUP BY ticker
),

ttm AS (
    SELECT
        m.ticker,
        SUM(
            CASE
                WHEN
                    m.period_type = 'quarterly'
                    AND m.period_end > mp.max_period_end - INTERVAL '15 months'
                    AND m.period_end <= mp.max_period_end
                    THEN m.revenue
                ELSE 0
            END
        ) AS revenue_ttm,
        SUM(
            CASE
                WHEN
                    m.period_type = 'quarterly'
                    AND m.period_end > mp.max_period_end - INTERVAL '15 months'
                    AND m.period_end <= mp.max_period_end
                    THEN m.gross_profit
                ELSE 0
            END
        ) AS gross_profit_ttm,
        SUM(
            CASE
                WHEN
                    m.period_type = 'quarterly'
                    AND m.period_end > mp.max_period_end - INTERVAL '15 months'
                    AND m.period_end <= mp.max_period_end
                    THEN m.net_income
                ELSE 0
            END
        ) AS net_income_ttm,
        SUM(
            CASE
                WHEN
                    m.period_type = 'quarterly'
                    AND m.period_end > mp.max_period_end - INTERVAL '15 months'
                    AND m.period_end <= mp.max_period_end
                    THEN m.free_cash_flow
                ELSE 0
            END
        ) AS fcf_ttm,
        MAX(
            CASE
                WHEN
                    m.period_type = 'quarterly'
                    AND m.period_end = mp.max_period_end
                    THEN m.total_assets
            END
        ) AS total_assets,
        MAX(
            CASE
                WHEN
                    m.period_type = 'quarterly'
                    AND m.period_end = mp.max_period_end
                    THEN m.total_equity
            END
        ) AS total_equity,
        MAX(
            CASE
                WHEN
                    m.period_type = 'quarterly'
                    AND m.period_end = mp.max_period_end
                    THEN m.total_debt
            END
        ) AS total_debt,
        MAX(
            CASE
                WHEN
                    m.period_type = 'quarterly'
                    AND m.period_end = mp.max_period_end
                    THEN m.cash
            END
        ) AS cash
    FROM metrics m
    INNER JOIN max_pe mp ON m.ticker = mp.ticker
    GROUP BY m.ticker
)

SELECT
    m.*,
    t.revenue_ttm,
    t.gross_profit_ttm,
    t.net_income_ttm,
    t.fcf_ttm,
    CASE
        WHEN t.revenue_ttm > 0 THEN t.gross_profit_ttm / t.revenue_ttm * 100
    END AS gross_margin_ttm,
    CASE
        WHEN t.revenue_ttm > 0 THEN t.net_income_ttm / t.revenue_ttm * 100
    END AS net_margin_ttm,
    CASE
        WHEN t.revenue_ttm > 0 THEN t.fcf_ttm / t.revenue_ttm * 100
    END AS fcf_margin_ttm
FROM metrics m
LEFT JOIN ttm t ON m.ticker = t.ticker
