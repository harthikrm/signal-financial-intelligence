SELECT ticker, period_end, revenue_growth
FROM {{ ref('int_yoy_growth') }}
WHERE revenue_growth IS NOT NULL
  AND (revenue_growth > 500 OR revenue_growth < -100)
