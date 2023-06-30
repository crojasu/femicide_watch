import argparse
import json
import os
import requests
import pandas as pd
from datetime import date, datetime
from fmedia.model_storage import load_model_from_gcs, update_data, blob_exists, load_data_from_gcp
from fmedia.train_evaluate_predict import predict
from dotenv import load_dotenv

load_dotenv()

BUCKET_NAME = os.getenv("BUCKET_NAME")
MODEL_FILENAME = os.getenv("MODEL_FILENAME")
VECTORIZER_FILENAME = os.getenv("VECTORIZER_FILENAME")

def fetch_articles(start_date: date, end_date: date, start_page=1):
    url_pattern = 'https://content.guardianapis.com/search?q=(murder%20OR%20homicide%20OR%20femicide%20OR%20feminicide%20OR%20murdered%20OR%20dead%20OR%20death%20OR%20killed%20OR%20murdered%20OR%20shot%20OR%20stabbed%20OR%20struck%20OR%20strangled%20OR%20"lifeless")%20AND%20(woman%20OR%20girl%20OR%20"a%20young%20woman"%20OR%20"a%20teenage%20girl"%20OR%20"a%20girl"%20OR%20"body%20of%20a%20woman"%20OR%20prostitute%20OR%20"sex%20worker")&from-date={start_date}&to-date={end_date}&show-fields=body,thumbnail&page-size=100&page={page}&api-key=test'
    page = start_page
    while True:
        print(f'Fetching page {page}...')
        url = url_pattern.format(start_date=start_date, end_date=end_date, page=page)
        response = requests.get(url).json()
        articles = response["response"]["results"]
        for article in articles:
            yield article
        current_page = response["response"]["currentPage"]
        total_pages = response["response"]["pages"]
        if current_page == total_pages:
            break
        page += 1

def fetch_articles_year(year: int):
    start_date = date(year, 1, 1)
    print(f'Fetching year {start_date}')
    end_date = start_date.replace(year=start_date.year + 1)
    return fetch_articles(start_date, end_date)

def main(year=None):
    model, vectorizer = load_model_from_gcs(MODEL_FILENAME, VECTORIZER_FILENAME)
    csv_counter = 1
    start_date = date.today() if year is None else date(year, 1, 1)
    
    if year is None:
        end_date = date.today()
        articles_generator = fetch_articles(date.today(), end_date)
    else:
        end_date = date(year+1, 1, 1)
        file_name = f'filtered_articles_{year}.csv'
        print(f'blob {file_name}')
        if blob_exists(BUCKET_NAME, start_date):
            print(f'Fetching from csv {file_name}')
            df = load_data_from_gcp(file_name)
            articles = df.to_dict(orient='records')
            return {'articles': articles}
        else:
            return
            articles_generator = fetch_articles_year(year)
    
    filtered_articles = []
    total_articles_processed = 0
    total_true_predictions = 0
    total_false_predictions = 0

    for i, article in enumerate(articles_generator, start=1):
        print(f'Processing article {i}...')
        df = pd.DataFrame([article])
        if "body" in df['fields'][0]:
            total_articles_processed += 1
            body_text = df['fields'][0]['body']
            prediction = predict(body_text, vectorizer=vectorizer, model=model)
            if prediction:
                total_true_predictions += 1
                filtered_articles.append(article)
                if len(filtered_articles) % 100 == 0:
                    df_filtered = pd.DataFrame(filtered_articles)
                    csv_filename = f'filtered_articles_{start_date}_{csv_counter}.csv'
                    print(f'Saving filtered articles to {csv_filename}...')
                    update_data(df_filtered, csv_filename)
                    print('Saved successfully.')
                    filtered_articles.clear()
                    csv_counter += 1
            else:
                total_false_predictions += 1

        if i % 1000 == 0:
            with open('start_page.txt', 'w') as f:
                f.write(str(i // 1000 + 1))
                
    print(f'Start date: {start_date}')
    print(f'End date: {end_date}')
    print(f'Total articles processed: {total_articles_processed}')
    print(f'Total articles predicted true: {total_true_predictions}')
    print(f'Total articles predicted false: {total_false_predictions}')

    summary = {
        'start_date': [start_date],
        'end_date': [end_date],
        'total_articles_processed': [total_articles_processed],
        'total_true_predictions': [total_true_predictions],
        'total_false_predictions': [total_false_predictions]
    }

    if filtered_articles:
        df_filtered = pd.DataFrame(filtered_articles)
        df_summary = pd.DataFrame(summary)
        df_final = pd.concat([df_filtered, df_summary])
        csv_filename = f'filtered_articles_{start_date}_{csv_counter}.csv'
        print(f'Saving final batch of filtered articles to {csv_filename}...')
        update_data(df_final, csv_filename)
        print('Final batch saved successfully.')

    return {
        'summary': {
            'total_articles_processed': total_articles_processed,
            'total_true_predictions': total_true_predictions,
            'total_false_predictions': total_false_predictions,
        },
        'articles': filtered_articles
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process start year.')
    parser.add_argument('--year', type=int, help='an integer for the year')
    args = parser.parse_args()
    main(args.year)
