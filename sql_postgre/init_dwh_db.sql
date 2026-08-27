--- DATAABASE
CREATE DATABASE dwh;

--- Change to directory DB dwh
\c dwh;

-- SCHEMA
CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;

-- Bronze Tables
CREATE TABLE IF NOT EXISTS bronze.raw_place_scraping_result(
    place_name VARCHAR(200),
    url TEXT,
    place_tag VARCHAR(100),
    total_review INT,
    total_rating FLOAT,
    phone_number VARCHAR(100),
    scraped_time TIMESTAMP,
    ingestion_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS bronze.raw_review_scraping_result(
    name VARCHAR(50),
    review TEXT,
    date_posted VARCHAR(50),
    star VARCHAR(50),
    review_id TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    place_url TEXT,
    place_address TEXT,
    place_website VARCHAR(2048),
    scraped_time TIMESTAMP,
    ingestion_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Silver Tables
CREATE TABLE IF NOT EXISTS silver.clean_place_scraping_result(
    place_name VARCHAR(100),
    url VARCHAR(2048),
    place_tag VARCHAR(100),
    total_review INT,
    total_rating FLOAT,
    phone_number VARCHAR(100),
    scraped_time TIMESTAMP,
    ingestion_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS silver.clean_review_scraping_result(
    name VARCHAR(50),
    review TEXT,
    date_posted DATE,
    star VARCHAR(50),
    review_id VARCHAR(200),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    place_url VARCHAR(2048),
    place_address VARCHAR(2048),
    place_website VARCHAR(2048),
    scraped_time TIMESTAMP,
    ingestion_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS silver.gemini_sentiment_result (
	review_id TEXT,
	review	TEXT,
	created_at TIMESTAMP,
	sentiment_score INT,
	sentiment_label	VARCHAR(50),
	relevansi VARCHAR(50),
	category VARCHAR(200),
	sub_category VARCHAR(200),
	reason TEXT,
	is_positive VARCHAR(20)
);

-- Gold Tables

CREATE TABLE IF NOT EXISTS gold.dim_place_scraping_result (
    place_id VARCHAR(100) PRIMARY KEY,
    place_name VARCHAR(100),
    url VARCHAR(2048),
    place_tag VARCHAR(100),
    address VARCHAR(2048),
    phone_number VARCHAR(100),
    website VARCHAR(2048),
    scraped_total_review INT,
    scraped_average_rating FLOAT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS gold.fact_review_scraping_result (
    review_id VARCHAR(200) PRIMARY KEY,

    place_id VARCHAR(100),

    reviewer_name VARCHAR(255),
    review TEXT,
    rating INT,
    review_date_posted DATE,
    review_date_scraped TIMESTAMP,
    
	sentiment_date TIMESTAMP,
	sentiment_score INT,
	sentiment_label	VARCHAR(50),
	relevansi VARCHAR(50),
	category VARCHAR(200),
	sub_category VARCHAR(200),
	reason TEXT,
	is_positive VARCHAR(20),

	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_review_place
        FOREIGN KEY (place_id)
        REFERENCES gold.dim_place_scraping_result
        ON DELETE CASCADE 
) ;