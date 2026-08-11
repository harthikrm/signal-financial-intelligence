FROM apache/airflow:2.8.1-python3.11
COPY ingestion/requirements.txt /tmp/ingestion-requirements.txt
RUN pip install --no-cache-dir --user -r /tmp/ingestion-requirements.txt
# dbt for weekly_metrics_refresh (Phase 8); pins align with Phase 1 manual / plan
RUN pip install --no-cache-dir --user dbt-core==1.11.9 dbt-postgres==1.10.0
