#add filepath to read the function
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
    dag_id="ingest_csv_result_to_bronze_postgre",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule_interval=None, # Dijalankan manual lewat UI Airflow
    catchup=False,
    tags=["Ingestion", "Postgres", "Scraper"],
)

def csv_pandas_pipeline():


    @task
    def load_raw_place_scraping_result():
        csv_file_path = '/opt/airflow/data/places_scraping_result.csv'
        
        # 1. Baca CSV pakai Pandas
        df = pd.read_csv(csv_file_path,sep="\t")

        # renaming columns
        df=df.rename(columns={
            'nama_lokasi' : 'place_name',
            'tag_lokasi' : 'place_tag',
            'no_hp' : 'phone_number'
        })

        df['scraped_time'] = pd.to_datetime(df['scraped_time'], format='%d/%m/%Y %H:%M:%S')

        pg_hook = PostgresHook(postgres_conn_id='dwh_postgres')
        engine = pg_hook.get_sqlalchemy_engine()

        # 4. Ingest ke database pakai to_sql
        df.to_sql(
            name='raw_place_scraping_result',
            schema='bronze',
            con=engine,
            if_exists='replace',
            index=False
        )
        print("Ingestion via Pandas selesai!")

    @task
    def load_raw_review_scraping_result():
        csv_file_path = '/opt/airflow/data/review_scraping_result.csv'
        
        # 1. Baca CSV pakai Pandas
        df = pd.read_csv(csv_file_path,sep="\t")

        # renaming columns
        df=df.rename(columns={
            'url' : 'place_url',
            'alamat' : 'place_address',
            'website' : 'place_website'
        })
        df['scraped_time'] = pd.to_datetime(df['scraped_time'], format='%d/%m/%Y %H:%M:%S')

        pg_hook = PostgresHook(postgres_conn_id='dwh_postgres')
        engine = pg_hook.get_sqlalchemy_engine()
        
        # 4. Ingest ke database pakai to_sql
        df.to_sql(
            name='raw_review_scraping_result',
            schema='bronze',
            con=engine,
            if_exists='replace',
            index=False
        )
        print("Ingestion via Pandas selesai!")

    task_silver_and_gold_transformation = SQLExecuteQueryOperator(
        task_id='task_silver_and_gold_transformation',
        conn_id='dwh_postgres',
        sql='function_scraper_and_integration/transformation_silver_and_gold.sql',)


    place_ingestion_task=load_raw_place_scraping_result()
    review_ingestion_task=load_raw_review_scraping_result()

    place_ingestion_task >> review_ingestion_task >> task_silver_and_gold_transformation

csv_pandas_pipeline()