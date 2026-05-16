{# dev: fail if staging is empty. ci/prod: skip (empty OK in CI; prod before ingestion). #}
{% if target.name == 'dev' %}
SELECT 1 AS failure
WHERE (SELECT COUNT(*) FROM {{ ref('stg_financials_raw') }}) = 0
{% else %}
SELECT 1 WHERE FALSE
{% endif %}
