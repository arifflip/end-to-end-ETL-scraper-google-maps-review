import os
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

import json
import time

from typing import List
from google import genai
from pydantic import BaseModel, Field

#functio to connect to dataase
def connect_to_db() :
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DWH_HOST = os.getenv("DWH_HOST")
    DWH_PORT = os.getenv("DWH_PORT")
    DWG_DB_NAME = os.getenv("DWG_DB_NAME")

    connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DWH_HOST}:{DWH_PORT}/{DWG_DB_NAME}"
    engine = create_engine(connection_string)

#get review data from bronze db
def get_data() :
    query = """
    SELECT 
    review_id, review
    FROM 
    bronze.raw_review_scraping_result
    WHERE
    review NOT LIKE '%%Lainnya'
    AND review NOT LIKE '%%ulasannya%%'
    AND review IS NOT NULL;
    """

    df_review = pd.read_sql(query, con=engine)
    df_review

    return df_review

# Schema Pydantic
class ReviewSentimentItem(BaseModel):
    sentiment_score: int = Field(description="Skor sentimen angka 0-5.")
    sentiment_label: str = Field(description="Label deskriptif sentimen.")
    relevansi: bool = Field(description="True jika relevan, False jika out-of-context.")
    category: str = Field(description="Kategori utama.")
    sub_category: str = Field(description="Sub-kategori spesifik.")
    reason: str = Field(description="Penjelasan AI.")
    is_positive: str = Field(description="'Positive', 'Negative', atau 'Irrelevant'")

class BulkReviewSentimentAnalysis(BaseModel):
    results: List[ReviewSentimentItem]

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def analyze_batch_reviews(
    reviews_payload: List[dict], 
    business_context: str = "Showroom, Dealer Mobil, Pabrik VinFast di berbagai aspek...",
    max_retries: int = 5
) -> List[dict]:
    
    only_reviews = [item.get('review', '') for item in reviews_payload]
    
    prompt = f"""
    Kamu adalah pakar analitik data konsumen.
    KONTEKS BISNIS: {business_context}
    INPUT DATA ULASAN: {json.dumps(only_reviews, ensure_ascii=False)}

    ATURAN SKOR SENTIMEN (0 - 5):
    - Skor 0: Tidak Relevan | 1: Sangat Negatif | 2: Negatif | 3: Netral | 4: Positif | 5: Sangat Positif

    ATURAN KATEGORI DAN SUB KATEGORI (WAJIB PILIH DARI DAFTAR INI):
    1. Pelayanan & Sales (Sub: 'Keramahan & Respon Staf', 'Proses Pembelian & Dokumen', 'Pengetahuan Produk (Sales)', 'Layanan Test Drive')
    2. Kualitas Produk & Performa (Sub: 'Desain & Fitur Mobil', 'Kualitas Baterai & Performa', 'Masalah Teknis/Kerusakan', 'Kelayakan Produk (Pabrik)')
    3. Purna Jual & Fasilitas (Sub: 'Servis & Sparepart', 'Klaim Garansi & Stasiun Cas (Charging)', 'Kebersihan & Kenyamanan Showroom')
    4. Harga & Bisnis Perusahaan (Sub: 'Harga Mobil & Promo', 'Lowongan Kerja & Rekrutmen', 'Perizinan & Keberadaan Pabrik/Perusahaan')
    5. Non-Konteks & Spam (Sub: 'Pakaian & Produk Lain', 'Komentar Acak / Spam', 'Ulasan Bahasa Asing/Acak')

    PENTING: Jumlah output results PERSIS SAMA (1:1) dengan input!
    """

    hit_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # --- RETRY LOGIC UNTUK HANDLING ERROR 503 / 429 ---
    for attempt in range(1, max_retries + 1):
        try:
            response = client.models.generate_content(
                model='gemini-3.6-flash',
                contents=prompt,
                config={
                    'response_mime_type': 'application/json',
                    'response_schema': BulkReviewSentimentAnalysis,
                    'temperature': 0.1
                },
            )
            # Jika berhasil, keluar dari loop retry
            break
        except Exception as e:
            print(f"⚠️ Warning: Hit API gagal (Attempt {attempt}/{max_retries}). Error: {e}")
            if attempt == max_retries:
                print("❌ High Demand persistent. Gagal setelah max retries.")
                raise e # Throw error jika sudah capai limit retry
            
            # Waktu tunggu makin lama (Exponential Backoff): 5 detik, 10 detik, 20 detik, dst.
            sleep_time = 5 * (2 ** (attempt - 1))
            print(f"⏳ Menunggu {sleep_time} detik sebelum mencoba lagi...")
            time.sleep(sleep_time)

    parsed_obj = BulkReviewSentimentAnalysis.model_validate_json(response.text)
    
    final_output = []
    for input_item, ai_res in zip(reviews_payload, parsed_obj.results):
        res_dict = ai_res.model_dump()
        formatted_dict = {
            'review_id': input_item.get('review_id'),
            'review': input_item.get('review', ''),
            'created_at': hit_timestamp,
            'sentiment_score': res_dict.get('sentiment_score'),
            'sentiment_label': res_dict.get('sentiment_label'),
            'relevansi': res_dict.get('relevansi'),
            'category': res_dict.get('category'),
            'sub_category': res_dict.get('sub_category'),
            'reason': res_dict.get('reason'),
            'is_positive': res_dict.get('is_positive')
        }
        final_output.append(formatted_dict)

    return final_output


def batch_sentiment_gemini_review(df_review) :

    #set up chunk to send number of row each batch
    CHUNK_SIZE = 20
    chunks = [df_review[i:i + CHUNK_SIZE] for i in range(0, df_review.shape[0], CHUNK_SIZE)]
    json_result=[]

    for index, batch in enumerate(chunks) :
        payload = batch[['review_id', 'review']].to_dict(orient='records')

        response=analyze_batch_reviews(payload)

        json_result.extend(response)

        time.sleep(5)

        print(f"------ Done at batch : {index+1} ------ ")

    result=pd.DataFrame(json_result)
    result.to_csv("/opt/airflow/data/sentiment_gemini_result.csv",index=None,sep="\t")

def run_sentiment_gemini() :
    connect_to_db()

    try :
        #get data from bronze review table
        df_review=get_data()

        #sentimetn using gemini API
        batch_sentiment_gemini_review(df_review)

    except Exception as e :
        print(f"---- There is an error \n {e}")