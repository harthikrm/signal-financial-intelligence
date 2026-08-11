SELECT ticker, period_end, gross_margin
FROM {{ ref('fct_company_metrics') }}
WHERE gross_margin IS NOT NULL
  AND (gross_margin > 100 OR gross_margin < -100)
