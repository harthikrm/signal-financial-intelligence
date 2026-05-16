select
    ticker,
    cast("date" as date) as date,
    "open"::numeric as open,
    high::numeric as high,
    low::numeric as low,
    close::numeric as close,
    volume::bigint as volume,
    vwap::numeric as vwap
from {{ ref('sample_prices') }}
