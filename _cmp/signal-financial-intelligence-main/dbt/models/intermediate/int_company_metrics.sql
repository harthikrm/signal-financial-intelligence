WITH financials AS (
    SELECT * FROM {{ ref('stg_financials_raw') }}
),

pivoted AS (
    SELECT
        ticker,
        period_end,
        period_type,
        fiscal_year,
        form,
        MAX(CASE WHEN metric_name = 'revenue' THEN value END) AS revenue,
        MAX(CASE WHEN metric_name = 'gross_profit' THEN value END) AS gross_profit,
        MAX(CASE WHEN metric_name = 'operating_income' THEN value END) AS operating_income,
        MAX(CASE WHEN metric_name = 'net_income' THEN value END) AS net_income,
        MAX(CASE WHEN metric_name = 'rd_expense' THEN value END) AS rd_expense,
        MAX(CASE WHEN metric_name = 'capex' THEN value END) AS capex,
        MAX(CASE WHEN metric_name = 'operating_cash_flow' THEN value END) AS operating_cash_flow,
        MAX(CASE WHEN metric_name = 'total_assets' THEN value END) AS total_assets,
        MAX(CASE WHEN metric_name = 'current_assets' THEN value END) AS current_assets,
        MAX(CASE WHEN metric_name = 'total_liabilities' THEN value END) AS total_liabilities,
        MAX(CASE WHEN metric_name = 'current_liabilities' THEN value END) AS current_liabilities,
        MAX(CASE WHEN metric_name = 'total_equity' THEN value END) AS total_equity,
        MAX(CASE WHEN metric_name = 'cash' THEN value END) AS cash,
        MAX(CASE WHEN metric_name = 'total_debt' THEN value END) AS total_debt,
        MAX(CASE WHEN metric_name = 'shares_outstanding' THEN value END) AS shares_outstanding,
        MAX(CASE WHEN metric_name = 'eps_diluted' THEN value END) AS eps_diluted,
        MAX(CASE WHEN metric_name = 'interest_expense' THEN value END) AS interest_expense,
        MAX(CASE WHEN metric_name = 'depreciation_amortization' THEN value END) AS da
    FROM financials
    GROUP BY ticker, period_end, period_type, fiscal_year, form
),

computed AS (
    SELECT
        *,
        COALESCE(operating_cash_flow, 0) - COALESCE(capex, 0) AS free_cash_flow,
        COALESCE(operating_income, 0) + COALESCE(da, 0) AS ebitda,
        CASE WHEN revenue > 0 THEN gross_profit / revenue * 100 END AS gross_margin,
        CASE WHEN revenue > 0 THEN operating_income / revenue * 100 END AS operating_margin,
        CASE WHEN revenue > 0 THEN net_income / revenue * 100 END AS net_margin,
        CASE WHEN total_equity > 0 THEN net_income / total_equity * 100 END AS roe,
        CASE WHEN total_assets > 0 THEN net_income / total_assets * 100 END AS roa,
        CASE WHEN total_assets > 0 THEN revenue / total_assets END AS asset_turnover,
        CASE
            WHEN current_liabilities > 0 THEN current_assets / current_liabilities
        END AS current_ratio,
        CASE WHEN total_equity > 0 THEN total_debt / total_equity END AS debt_to_equity,
        COALESCE(total_debt, 0) - COALESCE(cash, 0) AS net_debt,
        CASE
            WHEN interest_expense > 0 THEN operating_income / interest_expense
        END AS interest_coverage
    FROM pivoted
),

lagged AS (
    SELECT
        *,
        LAG(revenue) OVER (
            PARTITION BY ticker
            ORDER BY period_end
        ) AS prior_revenue
    FROM computed
)

SELECT
    *,
    CASE
        WHEN prior_revenue IS NOT NULL AND prior_revenue > 0
        THEN (revenue - prior_revenue) / prior_revenue * 100.0
    END AS revenue_growth
FROM lagged
