with chg as (
    select
        *,
        close - lag(close) over (
            partition by ticker
            order by date
        ) as price_chg
    from {{ ref('stg_price_daily') }}
),
rolled as (
    select
        *,
        avg(close) over (
            partition by ticker
            order by date
            rows between 19 preceding and current row
        ) as sma_20,
        avg(close) over (
            partition by ticker
            order by date
            rows between 49 preceding and current row
        ) as sma_50,
        avg(close) over (
            partition by ticker
            order by date
            rows between 199 preceding and current row
        ) as sma_200,
        avg(
            case when price_chg > 0 then price_chg else 0 end
        ) over (
            partition by ticker
            order by date
            rows between 13 preceding and current row
        ) as avg_gain_14,
        avg(
            case when price_chg < 0 then -price_chg else 0 end
        ) over (
            partition by ticker
            order by date
            rows between 13 preceding and current row
        ) as avg_loss_14
    from chg
)
select
    ticker,
    date,
    open,
    high,
    low,
    close,
    volume,
    sma_20,
    sma_50,
    sma_200,
    case
        when avg_loss_14 > 0 then
            100.0 - (
                100.0 / (1.0 + (avg_gain_14 / nullif(avg_loss_14, 0)))
            )
        when avg_gain_14 > 0 then 100.0
        else 50.0
    end as rsi_14
from rolled
