# End to end ETL - Google Map 'place' reviews scraper 

<img width="1419" height="704" alt="Portfolio - Project Portfolio - ETL Google Maps Review Scraper" src="https://github.com/user-attachments/assets/7e620c2b-ca02-432d-a04c-e4f1bc975dc7" />

<img width="1153" height="780" alt="Medallion Architecture" src="https://github.com/user-attachments/assets/d03cd957-f62e-4dc1-b37f-f59d73228287" />


# Sentiment Google Maps Review  - End-to-End ETL Pipeline
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Selenium](https://img.shields.io/badge/Selenium-43B02A?style=for-the-badge&logo=Selenium&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Apache Airflow](https://img.shields.io/badge/Apache%20Airflow-017CEE?style=for-the-badge&logo=Apache%20Airflow&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

Pipeline Data Engineering End-to-End yang terotomatisasi untuk mengekstraksi, membersihkan, mentransformasi, dan menyimpan data ulasan Google Maps. Proyek ini bertujuan untuk mendukung analisis berbasis data terkait persepsi publik dan kepuasan pelanggan terhadap subjek/layanan tertentu.

---

## Problem Statement

Memahami persepsi publik dan umpan balik konsumen terhadap suatu brand atau layanan di lokasi fisik erupakan kebutuhan analisis yang krusial. Sebagai peneliti atau analis eksternal tanpa akses ke data internal perusahaan, diperlukan sumber data publik yang andal untuk menangkap opini konsumen secara nyata.

Google Maps Reviews dipilih sebagai sumber data utama karena ketersediaannya yang tinggi (*high availability*) dan mudah diakses secara publik. Platform ini menyediakan pengalaman pengguna secara *real-time* dan spesifik berdasarkan lokasi fisik.

---

## Limitasi & Tantangan

### Batasan Bisnis
* Biaya API Mahal: Menggunakan Google Places API resmi untuk ekstraksi ulasan skala besar membutuhkan biaya yang sangat tinggi.
* Skalabilitas Manual: Pengumpulan data secara manual sangat tidak efisien, sulit dikembangkan (*not scalable*), dan rentan terhadap kesalahan manusia (*human error*).
* Noise Data: Ulasan Google Maps mengandung *noise*, teks irelevan, atau *spam* yang perlu difilter agar data siap dianalisis.

### Batasan Teknis
* Dynamic UI Rendering: Memerlukan penanganan elemen *JavaScript rendering* di sisi klien, *lazy loading*, *pop-up* dinamis, dan fitur *infinite scroll*.
* Proteksi Anti-Scraping: Risiko tinggi memicu pembatasan akses (*rate-limiting*), CAPTCHA, hingga pemblokiran IP sementara oleh Google.
* Kebutuhan Otomasi: Pipeline memerlukan eksekusi terjadwal dan andal tanpa intervensi manual untuk menjaga histori data tetap terbarui.

---

## Arsitektur & Tech Stack

| Teknologi | Kegunaan |
| :--- | :--- |
| Python | Bahasa pemrograman utama untuk *scripting* dan manipulasi data |
| Selenium | *Web scraping* dinamis (otomasi browser & penanganan *infinite scroll*) |
| Pandas | Parsing data hasil ekstrasi, pembersihan data, normalisasi, dan transformasi |
| PostgreSQL | Database Relasional / Data Warehouse untuk penyimpanan data terstruktur |
| Apache Airflow | Penjadwalan pipeline (*orchestration*), manajemen task, dan monitoring DAG |
| Docker & Docker Compose | Kontainerisasi seluruh *environment*, dependensi, dan *isolated services* |

---

## Output Utama Proyek

1. Scraping Engine Otomatis: Script Selenium yang dapat mengambil data list tempat dan review dari setiap tempatnya.
2. Pipeline ETL Terstandarisasi: 
   - Selenium scraper yang dapat meng-extract elemen HTML mentah/struktur JSON.
   - Pembersihan format tanggal, normalisasi rating, pembersihan teks dari *noise*, dan penanganan nilai kosong (*missing values*).
   - Pengmuatan data terstruktur ke tabel PostgreSQL.
3. Workflow Terotomatisasi: Airflow DAGs untuk eksekusi pipeline secara periodik.
4. Dataset Siap Analisis: Penyimpanan data yang siap digunakan untuk Sentiment Analysis, pemodelan NLP, atau pembuatan Dashboard Business Intelligence (Looker / Tableau / PowerBI).

---
