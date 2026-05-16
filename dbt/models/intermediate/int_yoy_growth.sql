select
    ticker,
    period_end,
    revenue,
    net_income,
    net_margin,
    revenue_growth
from {{ ref('int_company_metrics') }}
