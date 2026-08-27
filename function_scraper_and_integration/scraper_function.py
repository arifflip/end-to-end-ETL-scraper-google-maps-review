import undetected_chromedriver as uc
from pyvirtualdisplay import Display
import time
import os

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import pandas as pd
from datetime import datetime

# Initiate driver
def init_driver()  :
    display = Display(visible=0, size=(1920, 1080))
    display.start()

    options = uc.ChromeOptions()

    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--force-device-scale-factor=1')

    try:
        driver = uc.Chrome(options=options,version_main=151)
        driver.set_window_size(1920, 1080)
        print("----- Driver created succesfully")
    except Exception as e:
       print("Driver failed to inititiatee", type(e)) 
    return driver


# Function to wait element to be located 
def global_wait(driver,selector,elem) :
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((selector, elem)))

# Scroll to bottom of the element
# def do_scroll_to_the_bottom_of_page(driver,elem) :

#     break_counter=0

#     panel_review = driver.find_element(By.XPATH, elem)

#     last_height = driver.execute_script("return arguments[0].scrollHeight", panel_review)

#     print("---- Scroll Down ----")
#     while True:

#         driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", panel_review)
        
#         time.sleep(7)
        
#         new_height = driver.execute_script("return arguments[0].scrollHeight", panel_review)
        
#         if new_height == last_height:
#             if break_counter != 2 :
#                 break_counter+=1
#                 print(f"-reaching break counter {break_counter}")
#                 pass

#             else :
#                 print("---- Scorlling process finishied ----")
#                 break
            
#         last_height = new_height

# def do_scroll_to_the_bottom_of_page(driver, elem):
#     break_counter = 0

#     # Pastikan mencari elemen
#     panel_review = driver.find_element(By.XPATH, elem)

#     last_height = driver.execute_script(
#         "return arguments[0].scrollHeight", panel_review
#     )

#     print("---- Scroll Down Started ----")

#     while True:
#         # 1. Gunakan scrollTop (lebih reliable untuk div di Chrome)
#         driver.execute_script(
#             "arguments[0].scrollTop = arguments[0].scrollHeight;", panel_review
#         )

#         # 2. Jeda waktu tunggu render AJAX (7 detik sudah cukup aman)
#         time.sleep(10)

#         new_height = driver.execute_script(
#             "return arguments[0].scrollHeight", panel_review
#         )

#         if new_height == last_height:
#             break_counter += 1
#             print(
#                 f"- Reaching break counter {break_counter}/3 (menunggu data baru...)"
#             )

#             if break_counter >= 3:  # Coba 3 kali sebelum menyerah
#                 print("---- Scrolling process finished ----")
#                 break
#         else:
#             # FIX: RESET counter ke 0 jika tinggi berhasil bertambah!
#             break_counter = 0
#             #print(f"Berhasil scroll! Tinggi baru: {new_height}")

#         last_height = new_height

def do_scroll_to_the_bottom_of_page(driver, elem):
    break_counter = 0

    panel_review = driver.find_element(By.XPATH, elem)

    last_height = driver.execute_script(
        "return arguments[0].scrollHeight", panel_review
    )

    print("---- Scroll Down Started ----")

    while True:
        # 1. Scroll ke paling bawah
        driver.execute_script(
            "arguments[0].scrollTop = arguments[0].scrollHeight;", panel_review
        )

        # 2. Jeda waktu render (3-5 detik cukup kalau pancingannya jalan)
        time.sleep(4)

        new_height = driver.execute_script(
            "return arguments[0].scrollHeight", panel_review
        )

        if new_height == last_height:
            break_counter += 1
            print(
                f"- Reaching break counter {break_counter}/3 (menunggu data baru...)"
            )

            # --- FIX UTAMA: PANCINGAN SCROLL ---
            # Tarik scroll ke atas 400px, lalu dorong lagi ke bawah untuk memicu event AJAX Google Maps
            driver.execute_script(
                "arguments[0].scrollTop -= 400;", panel_review
            )
            time.sleep(1)
            driver.execute_script(
                "arguments[0].scrollTop = arguments[0].scrollHeight;",
                panel_review,
            )

            if break_counter >= 3:
                print("---- Scrolling process finished ----")
                break
        else:
            # RESET counter jika ada data baru
            break_counter = 0

        last_height = new_height

# Inject Cookie
def cookie_injector(driver) :

    driver.get("https://www.google.com/maps") # 1. Buka GMaps dulu (Wajib!)
    driver.add_cookie({
            "name": "CONSENT",
            "value": "YES+cb",
            "domain": ".google.com",
            "path": "/"
        })

    driver.refresh()
    time.sleep(5)
    return driver

## ----------------------------
## FUNCTION TO SCRAPE PLACES BY A QUERY
## ----------------------------

# Search place by 'key_search'
def search_place(driver,key_search) :
    
    #go to gmaps
    driver.get('https://www.google.com/maps/')
    global_wait(driver,By.XPATH,"//input[@class='UGojuc fontBodyMedium EmSKud lpggsf ']")

    # query places
    driver.find_element(By.XPATH,"//input[@class='UGojuc fontBodyMedium EmSKud lpggsf ']").clear()
    driver.find_element(By.XPATH,"//input[@class='UGojuc fontBodyMedium EmSKud lpggsf ']").send_keys(key_search)

    # click searh
    driver.find_element(By.XPATH,"//button[@class='mL3xi']").click()

    #scroll_down
    global_wait(driver,By.XPATH,"//div[@class='m6QErb DxyBCb kA9KIf dS8AEf XiKgde ecceSd']")
    do_scroll_to_the_bottom_of_page(driver,"//div[@class='m6QErb DxyBCb kA9KIf dS8AEf XiKgde ecceSd']")


# Extract data by key_data_wanna_be_scraped which hold each selector for each keys
def extract_places_data(content, key_data_wanna_be_scraped) :
    
    result=None
    children=None

    try :
        if key_data_wanna_be_scraped =='nama_lokasi' :
            result=content.find_element(By.CLASS_NAME,"qBF1Pd ").text
            return result

        if key_data_wanna_be_scraped =='url' :
            result=content.find_element(By.XPATH,"..").find_element(By.XPATH,".//a[@class='hfpxzc']").get_attribute('href')
            result=result.replace("&hl=en","&hl=id")
            return result

        elif key_data_wanna_be_scraped == 'tag_lokasi' :
            children=content.find_elements(By.XPATH,".//div[@class='W4Efsd']")
            result=children[1].find_element(By.XPATH,".//span").get_attribute('innerText')
            return result

        elif key_data_wanna_be_scraped == 'total_rating' :
            children=content.find_elements(By.XPATH,".//div[@class='W4Efsd']")
            result=children[0].find_element(By.XPATH,".//span[@class='MW4etd']").get_attribute("innerText")

            #cleansing for rating
            result=float(result.replace(",","."))
            return result

        elif key_data_wanna_be_scraped == 'total_review' :
            children=content.find_elements(By.XPATH,".//div[@class='W4Efsd']")
            result=children[0].find_element(By.XPATH,".//span[@class='UY7F9']").get_attribute("innerText")
            result=result.replace('(',"").replace(')',"")
            return result

        elif key_data_wanna_be_scraped == 'no_hp' :
            children=content.find_elements(By.XPATH,".//div[@class='W4Efsd']")
            result = children[3].find_element(By.XPATH,".//span[@class='UsdlK']").get_attribute("innerText")
            return result

    except :
        result=None
        return result

# Scrape the value by key inside the function
def do_scrape_places_data(elem) :
    result=[]
    for key in ['nama_lokasi','url','tag_lokasi','total_review','total_rating','no_hp'] :
        value=extract_places_data(elem,key)
        result.append(value)
    
    return result

def full_scrap_places_data(driver,key_search) :

    search_place(driver,key_search=key_search)
    time.sleep(5)

    elems=driver.find_elements(By.XPATH,"//div[@class='bfdHYd Ppzolf OFBs3e  ']")

    df_result=pd.DataFrame(columns=['nama_lokasi','url','tag_lokasi','total_review','total_rating','no_hp','scraped_time'])

    for elem in elems :
        value = do_scrape_places_data(elem)

        value.append(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        df_result.loc[len(df_result)]=value

    return df_result

## ----------------------------
## FUNCTION TO SCRAPE REVIEWS FROM PLACE
## ----------------------------

def go_to_place_review_page(driver,url) :

    #visit url
    driver.get(url)

    #time.sleep(5)
    global_wait(driver,By.XPATH,"//div[contains(@class, 'rogA2c ')]")

    #get alaamt dan nama website
    alamat=extract_data_from_page_elements(driver,"rogA2c ",case="alamat")
    website=extract_data_from_page_elements(driver,"rogA2c ITvuef",case="web")

    #get to review section
    driver.find_element(By.CLASS_NAME,"RWPxGd").find_element(By.XPATH,"//*[@data-tab-index='1']").click()

    return dict(zip(['alamat','website'],[alamat,website]))

def get_latitude_longitude(driver) :

    #check if canvas is already clicked or not
    #if driver.find_element(By.XPATH,"//canvas[@class='H1VXrf JRr1M DnOnV']").find_elements(By.XPATH,"//div[@class='mLuXec']") == [] :

    #click on canvas to make latlong elem appear on the display
    elem=driver.find_element(By.XPATH,"//div[@class='D21QYe']")
    actions = ActionChains(driver)
    actions.context_click(elem).perform()

    time.sleep(3)

    #extract latitude longitude
    try :
        result=driver.find_element(By.XPATH,"//div[@class='mLuXec']").text
        result=dict(zip(['latitude','longitude'],[i.strip() for i in result.split(",")])) 
    except :
        result=dict(zip(['latitude','longitude'],[None,None]))

    return result

#get people review
def extract_data_from_page_elements(main_element,class_name,case=str) :
    try :
        #case if we want extract and website (used in "ringkasan" menu)
        if case in ["alamat","web"] :
            result=main_element.find_element(By.XPATH,f"//div[@class='{class_name}']").text

        #case if want extract star-rating
        elif case == "star-rating" :
            #result = re.search(r"\d+",main_element.find_element(By.XPATH,f".//*[@class='{class_name}']").get_attribute('aria-label')).group()
            result = main_element.find_element(By.XPATH,f".//span[@class='{class_name}']").get_attribute('aria-label')

        #get review id
        elif case == "review-id" :
            result=main_element.get_attribute("data-review-id")

        else : 
            #case if want extract reviewer nama, review, review date (used in "ulasan" menu)
            result = main_element.find_element(By.XPATH,f".//*[@class='{class_name}']").text

    except :
        result=None

    return result

#integrate all text scraped
def do_extract_reviews_value(content) :

    name=extract_data_from_page_elements(content,'d4r55 fontTitleMedium') #get name reviewer
    comment=extract_data_from_page_elements(content,'wiI7pd') #get review comment
    post_time=extract_data_from_page_elements(content,'rsqaWe') #get review post timee
    star_given=extract_data_from_page_elements(content,'kvMYJc',case="star-rating") #get star given

    review_id=extract_data_from_page_elements(content,class_name="None",case="review-id")

    return [name,comment,post_time,star_given,review_id]

def scrape_gmaps_review(driver) :
    
    #get total review
    df_result=pd.DataFrame(columns=['name','review','date_posted','star',"review_id"])

    #scroll down
    time.sleep(8)
    global_wait(driver,By.XPATH,"//div[@class='m6QErb DxyBCb kA9KIf dS8AEf XiKgde ']")
    do_scroll_to_the_bottom_of_page(driver,"//div[@class='m6QErb DxyBCb kA9KIf dS8AEf XiKgde ']")

    #get total review scraped on this scroll
    contents=driver.find_elements(By.XPATH,"//*[@class='jftiEf fontBodyMedium ']")

    #extract data
    for content in contents :
        scraped_review=do_extract_reviews_value(content)
        
        #insert to dataframe
        df_result.loc[len(df_result)] = scraped_review

    #get_latlong
    latlong_value=get_latitude_longitude(driver)

    df_result['latitude']=latlong_value['latitude']
    df_result['longitude']=latlong_value['longitude']

    return df_result

def run_review_scraper(driver,list_url_places:list,file_path:str) :

    #loop per place
    counter=1
    for url_place in list_url_places :

        print(f"Running on index {counter}/{len(list_url_places)} : at {url_place}")

        #visit review section
        review_section_result=go_to_place_review_page(driver,url_place)

        #scrpaer value
        df_result=scrape_gmaps_review(driver)

        #insert data from review_section_result to df_result
        df_result["url"]=url_place
        df_result["alamat"]=review_section_result['alamat']
        df_result["website"]=review_section_result['website']
        df_result["scraped_time"]=datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        #write to csv
        file_exists = os.path.exists(file_path)
        df_result.to_csv(file_path, sep="\t", mode='a', index=False, header=not file_exists)

        driver.save_screenshot(f"/opt/airflow/data/scroll_monitoring_{url_place}.png")
        print(f"Total Reveiw Scraped{df_result.shape[0]} : at {url_place}")

        counter+=1

