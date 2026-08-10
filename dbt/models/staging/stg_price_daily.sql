{# Prod: ingestion only. dev/ci: prefer price_daily; fall back to sample_prices seed when empty. #}
WITH combined AS (
    SELECT
        ticker,
        CAST("date" AS DATE) AS date,
        "open"::numeric AS open,
        high::numeric AS high,
        low::numeric AS low,
        close::numeric AS close,
        volume::bigint AS volume,
        vwap::numeric AS vwap,
        1 AS _src_priority
    FROM {{ source('signal', 'price_daily') }}

    {% if target.name != 'prod' %}
    UNION ALL
    SELECT
        ticker,
        CAST("date" AS DATE) AS date,
        "open"::numeric AS open,
        high::numeric AS high,
        low::numeric AS low,
        close::numeric AS close,
        volume::bigint AS volume,
        vwap::numeric AS vwap,
        2 AS _src_priority
    FROM {{ ref('sample_prices') }}
    {% endif %}
),

deduped AS (
    SELECT DISTINCT ON (ticker, date)
        ticker,
        date,
        open,
        high,
        low,
        close,
        volume,
        vwap
    FROM combined
    ORDER BY
        ticker,
        date,
        _src_priority ASC
)

SELECT * FROM deduped
