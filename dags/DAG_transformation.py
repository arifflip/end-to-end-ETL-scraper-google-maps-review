import pandas as pd
from datetime import datetime
from airflow.decorators import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.hooks.base import BaseHook
from sqlalchemy import create_engine
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

default_args = {
    "owner": "airflow",
    "retries": 0,
}

@dag(
    dag_id="transformation_silver_and_gold",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule_interval=None, # Dijalankan manual lewat UI Airflow
    catchup=False,
    tags=["Data Transformation","Silver", "Gold"],
)

def silver_gold_transformation() :

    task_silver_and_gold_transformation = SQLExecuteQueryOperator(
        task_id='task_silver_and_gold_transformation',
        conn_id='dwh_postgres',
        sql='function_scraper_and_integration/transformation_silver_and_gold.sql',)

    task_silver_and_gold_transformation

silver_gold_transformation()