{{ config(materialized='table') }}

select * from {{ ref('int_price_indicators') }}
