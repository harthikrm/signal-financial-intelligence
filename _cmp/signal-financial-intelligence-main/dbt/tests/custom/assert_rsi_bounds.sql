SELECT ticker, date, rsi_14
FROM {{ ref('fct_price_indicators') }}
WHERE rsi_14 IS NOT NULL
  AND (rsi_14 > 100 OR rsi_14 < 0)
