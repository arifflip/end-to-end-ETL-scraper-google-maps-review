-- script cleansing for silver.clean_place_scraping_result
INSERT INTO
	silver.clean_place_scraping_result(
	place_name,
	url,
	place_tag,
	total_review,
	total_rating,
	phone_number,
	scraped_time
	)
SELECT
	place_name,
	url,
	place_tag,
	total_review,
	total_rating,
	REPLACE(phone_number, '-', '') AS phone_number,
	scraped_time
FROM
	bronze.raw_place_scraping_result
WHERE total_rating IS NOT NULL;

-- script cleansing for silver.clean_review_scraping_result

INSERT INTO 
	silver.CLEAN_REVIEW_SCRAPING_RESULT(
	name,   
	review,
    date_posted,
    star,
    review_id,
    latitude,
    longitude,
    place_url,
    place_address,
    place_website,
    scraped_time
	)
SELECT 
	INITCAP(name),
	review,
	(
        scraped_time - (
            -- 1. Normalisasi kata "se-" jadi "1 " (contoh: "setahun" -> "1 tahun")
            WITH normalized AS (
                SELECT LOWER(
                    REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(
                        date_posted, 
                        'setahun', '1 tahun'),
                        'sebulan', '1 bulan'),
                        'seminggu', '1 minggu'),
                        'sehari', '1 hari'),
                        'sejam', '1 jam')
                ) AS txt
            )
            -- 2. Ambil angka dan konversi ke INTERVAL berdasarkan satuannya
            SELECT CASE 
                WHEN txt LIKE '%tahun%'  THEN (COALESCE((REGEXP_MATCH(txt, '(\d+)'))[1]::INT, 1) || ' years')::INTERVAL
                WHEN txt LIKE '%bulan%'  THEN (COALESCE((REGEXP_MATCH(txt, '(\d+)'))[1]::INT, 1) || ' months')::INTERVAL
                WHEN txt LIKE '%minggu%' THEN (COALESCE((REGEXP_MATCH(txt, '(\d+)'))[1]::INT, 1) || ' weeks')::INTERVAL
                WHEN txt LIKE '%hari%'   THEN (COALESCE((REGEXP_MATCH(txt, '(\d+)'))[1]::INT, 1) || ' days')::INTERVAL
                WHEN txt LIKE '%jam%'    THEN (COALESCE((REGEXP_MATCH(txt, '(\d+)'))[1]::INT, 1) || ' hours')::INTERVAL
                ELSE INTERVAL '0 days'
            END
            FROM normalized
        )
    )::DATE AS date_posted,
    TRIM(REPLACE(star,'bintang','')) AS star,
    review_id,
    latitude,
    longitude,
    place_url,
    place_address,
    place_website,
    scraped_time
FROM
	bronze.RAW_REVIEW_SCRAPING_RESULT;


-- GOLD.DIM_PLACE_SCRAPING_RESULT
INSERT INTO
	GOLD.DIM_PLACE_SCRAPING_RESULT (
	place_id,
	place_name,
    url,
    place_tag,
    address,
    phone_number,
    website,
    scraped_total_review,
    scraped_average_rating,
    latitude,
    longitude
	)
WITH place_summary AS (
	SELECT
		DISTINCT place_url,
		PLACE_ADDRESS,
		place_website,
		latitude,
		longitude
	FROM 
		silver.CLEAN_review_SCRAPING_RESULT )
SELECT
	(REGEXP_MATCH(place.url, '!19s([^?!&]+)'))[1] AS place_id,
	place.place_name,
	place.url,
	place.place_tag,
	summary.place_address AS address,
	place.phone_number,
	summary.place_website AS website,
	place.total_review AS scraped_total_review,
	place.total_rating AS scraped_average_rating,
	summary.latitude,
	summary.longitude 
FROM
	silver.clean_place_scraping_result AS place
LEFT JOIN
	place_summary AS summary
ON
	place.url = summary.place_url 
WHERE place.TOTAL_RATING IS NOT NULL;


-- GOLD.fact_review_scraping_result
INSERT INTO gold.FACT_REVIEW_SCRAPING_RESULT (
	review_id,
	place_id,
	reviewer_name,
	review,
	rating,
	review_date_posted,
	review_date_scraped,
	sentiment_date,
	sentiment_score,
	sentiment_label,
	relevansi,
	category,
	sub_category,
	reason,
	is_positive)
SELECT
	silver_review.review_id,
    (REGEXP_MATCH(silver_review.place_url, '!19s([^?!&]+)'))[1] AS place_id,
    silver_review.name AS reviewer_name,
    silver_review.review,
    silver_review.star::INT AS rating,
    silver_review.date_posted AS review_date_posted,
    silver_review.scraped_time AS review_date_scraped,  
	silver_sentiment.created_at AS sentiment_date,
	silver_sentiment.sentiment_score,
	silver_sentiment.sentiment_label,
	silver_sentiment.relevansi,
	silver_sentiment.category,
	silver_sentiment.sub_category,
	silver_sentiment.reason,
	silver_sentiment.is_positive
FROM
	silver.CLEAN_REVIEW_SCRAPING_RESULT AS silver_review
INNER JOIN
	silver.GEMINI_SENTIMENT_RESULT AS silver_sentiment
ON
	silver_review.REVIEW_ID = silver_sentiment.REVIEW_ID;

