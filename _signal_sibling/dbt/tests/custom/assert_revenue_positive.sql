SELECT m.ticker, m.period_end, m.revenue
FROM {{ ref('fct_company_metrics') }} m
LEFT JOIN {{ ref('stg_companies') }} c ON m.ticker = c.ticker
WHERE m.revenue IS NOT NULL
  AND m.revenue < 0
  AND c.sector NOT IN ('Traditional Finance')
