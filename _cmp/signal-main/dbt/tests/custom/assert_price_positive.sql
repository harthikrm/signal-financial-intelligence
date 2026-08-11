SELECT ticker, date, close
FROM {{ ref('stg_price_daily') }}
WHERE close IS NOT NULL AND close <= 0
