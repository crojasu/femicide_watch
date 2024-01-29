import json
import os
import requests
import pandas as pd
from datetime import date
from .model_storage import load_model_from_gcs, save_data_to_gcs, blob_exists, load_data_from_gcp
from .train_evaluate_predict import predict
from dotenv import load_dotenv
import argparse
import time

load_dotenv()

BUCKET_NAME = os.getenv("BUCKET_NAME")
MODEL_FILENAME = os.getenv("MODEL_FILENAME")
VECTORIZER_FILENAME = os.getenv("VECTORIZER_FILENAME")

def fetch_articles_from_gcp(year):
    # Load data from GCP if available
    print("cheking saved files")
    gcp_filename = f"filtered_articles_{year}-01-01"
    if blob_exists(BUCKET_NAME, gcp_filename):
        print("from files")
        return load_data_from_gcp(gcp_filename, year)

    return None

def fetch_articles(start_date: date, end_date: date, start_page=1):
    url_pattern = 'https://content.guardianapis.com/search?q=&from-date={start_date}&to-date={end_date}&show-fields=body,thumbnail&page-size=100&page={page}&api-key=test'
    page = start_page

    while True:
        print(f'Fetching page {page}...')
        url = url_pattern.format(start_date=start_date, end_date=end_date, page=page)
        response = requests.get(url).json()
        articles = response["response"]["results"]

        if not articles:  # Break if no articles are returned
            break

        for article in articles:
            yield article

        current_page = response["response"]["currentPage"]
        total_pages = response["response"]["pages"]
        if current_page == 2:
            break

        page += 1

    return articles

def main(year=None):
    model, vectorizer = load_model_from_gcs(MODEL_FILENAME, VECTORIZER_FILENAME)

    if year is None:
        start_date = date.today()
        end_date = start_date
    else:
        start_date = date(year, 1, 1)
        end_date = start_date.replace(year=start_date.year + 1)

    filtered_articles = []
    total_articles_processed = 0
    total_true_predictions = 0

    # Try to fetch data from GCP
    articles_data = fetch_articles_from_gcp(year)

    if articles_data is None:
        # Data not found in GCP, fetch from API
        articles_generator = fetch_articles(start_date, end_date)
        
        for i, article in enumerate(articles_generator, start=1):
            print(f'Processing article {i}...')
            common_article = {
                "title": article.get("webTitle", None),
                "content": article.get("fields", {}).get("body", None),
                "id": article.get("id", None),
                "thumbnail": article.get("fields", {}).get("thumbnail", None),
                "type": article.get("type", None),
                "sectionId": article.get("sectionId", None),
                "sectionName": article.get("sectionName", None),
                "webPublicationDate": article.get("webPublicationDate", None),
                "webUrl": article.get("webUrl", None),
                "apiUrl": article.get("apiUrl", None),
            }
            if common_article["content"]:
                total_articles_processed += 1
                body_text = common_article["content"]
                prediction = predict(body_text, vectorizer=vectorizer, model=model)
                if prediction:
                    total_true_predictions += 1
                    filtered_articles.append(common_article)  # Keep only true predictions

        print(f'Start date: {start_date}')
        print(f'End date: {end_date}')
        print(f'Total articles processed: {total_articles_processed}')
        print(f'Total articles predicted true: {total_true_predictions}')

        articles_data = {
                'summary': {
                    'start_date': str(start_date),
                    'end_date': str(end_date),
                    'total_articles_processed': total_articles_processed,
                    'total_true_predictions': total_true_predictions,
                },
                'articles': filtered_articles
            }

        # Save data to GCP if year is not None
        if year is not None and filtered_articles:
            gcp_filename = f"filtered_articles_{year}-01-01"

            save_data_to_gcs(articles_data, gcp_filename)

    return articles_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process start year and month.')
    parser.add_argument('--start_year', type=int, help='an integer for the start year')
    parser.add_argument('--end_year', type=int, help='an integer for the end year')
    parser.add_argument('--start_month', type=int, default=1, help='an integer for the start month (default is 1)')
    parser.add_argument('--end_month', type=int, default=1, help='an integer for the end month (default is 1)')
    args = parser.parse_args()
    fetch_articles_range(args.start_year, args.end_year, args.start_month, args.end_month)
