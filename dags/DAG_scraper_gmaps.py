#add filepath to read the function
import sys
sys.path.append("/opt/airflow/dags/function_scraper_and_integration")
from function_scraper_and_integration import * 

import pendulum
local_tz = pendulum.timezone("Asia/Jakarta")

from datetime import datetime
from airflow.decorators import dag, task
from pyvirtualdisplay import Display
import undetected_chromedriver as uc

default_args = {
    "owner": "airflow",
    "retries": 0,
}

@dag(
    dag_id="scraper_google_maps",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule_interval=None, # Dijalankan manual lewat UI Airflow
    catchup=False,
    tags=["Scaper", "selenium", "GoogleMaps"],
)
def test_place_scraper_gmaps():

    @task
    def run_place_scraper():

        # init driver
        driver=init_driver()

        # run scraper
        place_to_be_search='"Vinfast" Indonesia'
        print(f"Started to search {place_to_be_search} in Google Mapp")
        scraping_result=full_scrap_places_data(driver,place_to_be_search)

        # write to csv
        filename_place_scraped_result="/opt/airflow/data/places_scraping_result.csv"
        scraping_result.to_csv(filename_place_scraped_result,index=None,sep="\t")
        print(f'File saved in {filename_place_scraped_result}')

        # close driver
        driver.quit()
        print("Driver exited peacfully!")

        return filename_place_scraped_result

    @task
    def run_places_review_scraper() :

        try :
            driver=init_driver()

            #inject cookie
            driver=cookie_injector(driver)

            # read places data
            places_data=pd.read_csv("/opt/airflow/data/places_scraping_result.csv",sep="\t")
            places_data=places_data[~places_data.total_review.isnull()]
            list_places=places_data.url.tolist()

            # loop to scrape list places
            filename_review_scraped_result="/opt/airflow/data/review_scraping_result.csv"
            run_review_scraper(driver,list_places,filename_review_scraped_result)

            # close 
            driver.quit()
            print("Driver exited peacfully!")

        except Exception as e :
            driver.quit()
            print("Damn ada ERROR", "\n", e)

    # PERBAIKAN: Panggil task di sini agar terdaftar di DAG Graph!
    place_scraper = run_place_scraper()
    review_scraper = run_places_review_scraper()
    place_scraper >> review_scraper
    review_scraper

# Instansiasi DAG
test_place_scraper_gmaps()