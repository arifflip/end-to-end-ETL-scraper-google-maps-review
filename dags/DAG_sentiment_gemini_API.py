#add filepath to read the function
import sys
sys.path.append("/opt/airflow/dags/function_scraper_and_integration")
from function_scraper_and_integration import * 

from datetime import datetime
from airflow.decorators import dag, task

default_args = {
    "owner": "airflow",
    "retries": 0,
}

@dag(
    dag_id="gemini_API_sentiment",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule_interval=None, # Dijalankan manual lewat UI Airflow
    catchup=False,
    tags=["Gemini API", "Sentiment"],
)

def gemini_API_sentiment() :


    @task
    def do_sentiment_via_gemini_api() :
        run_sentiment_gemini()

    @task
    def write_setiment_dataset_to_silver_db():
        csv_file_path = '/opt/airflow/data/review_scraping_result.csv'
        
        df = pd.read_csv(csv_file_path,sep="\t")

        pg_hook = PostgresHook(postgres_conn_id='dwh_postgres')
        engine = pg_hook.get_sqlalchemy_engine()
        
        df.to_sql(
            name='gemini_scraping_result',
            schema='silver',
            con=engine,
            if_exists='append',
            index=False
        )
        print("Ingestion via Pandas selesai!")


    sentiment=do_sentiment_via_gemini_api()
    write_to_silver=write_setiment_dataset_to_silver_db()

    sentiment >> write_to_silver

gemini_API_sentiment()