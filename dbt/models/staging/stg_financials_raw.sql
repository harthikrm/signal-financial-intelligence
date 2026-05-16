{# Prod: ingestion only. dev/ci: union sample_financials seed so models/tests exercise real rows when financials_raw is empty. #}
WITH combined AS (
    SELECT
        ticker,
        metric_name,
        CAST(period_end AS DATE) AS period_end,
        form,
        CAST(value AS NUMERIC) AS value,
        1 AS _src_priority
    FROM {{ source('signal', 'financials_raw') }}

    {% if target.name != 'prod' %}
    UNION ALL
    SELECT
        ticker,
        metric_name,
        CAST(period_end AS DATE) AS period_end,
        form,
        CAST(value AS NUMERIC) AS value,
        2 AS _src_priority
    FROM {{ ref('sample_financials') }}
    {% endif %}
),

deduped AS (
    SELECT DISTINCT ON (ticker, metric_name, period_end, form)
        ticker,
        metric_name,
        period_end,
        form,
        value
    FROM combined
    ORDER BY
        ticker,
        metric_name,
        period_end,
        form,
        _src_priority ASC
),

cleaned AS (
    SELECT
        ticker,
        metric_name,
        CAST(period_end AS DATE) AS period_end,
        form,
        CAST(value AS NUMERIC) AS value,
        CASE
            WHEN form = '10-K' THEN 'annual'
            WHEN form = '10-Q' THEN 'quarterly'
            ELSE 'other'
        END AS period_type,
        EXTRACT(YEAR FROM CAST(period_end AS DATE)) AS fiscal_year
    FROM deduped
    WHERE value IS NOT NULL
      AND value != 0
)
SELECT * FROM cleaned
