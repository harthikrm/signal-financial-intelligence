select * from {{ source('signal', 'filings_metadata') }}
