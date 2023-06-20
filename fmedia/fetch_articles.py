import requests
import pandas as pd
from datetime import date
from fmedia.model_storage import (
    load_data_from_gcp,
    update_data_to_gcs,
    load_model_from_gcs,
)

import ast
from dotenv import load_dotenv
import os
from fmedia.train_evaluate_predict import predict

load_dotenv()  # Load environment variables from .env file

# Get the environment variables
MODEL_FILENAME = os.getenv("MODEL_FILENAME")
VECTORIZER_FILENAME = os.getenv("VECTORIZER_FILENAME")

def fetch_articles(start_date: date, end_date: date) -> pd.DataFrame:
    # Define the URL pattern
    url_pattern = 'https://content.guardianapis.com/search?q=(murder%20OR%20homicide%20OR%20femicide%20OR%20feminicide%20OR%20murdered%20OR%20dead%20OR%20death%20OR%20killed%20OR%20murdered%20OR%20shot%20OR%20stabbed%20OR%20struck%20OR%20strangled%20OR%20"lifeless")%20AND%20(woman%20OR%20girl%20OR%20"a%20young%20woman"%20OR%20"a%20teenage%20girl"%20OR%20"a%20girl"%20OR%20"body%20of%20a%20woman"%20OR%20prostitute%20OR%20"sex%20worker")&from-date={start_date}&to-date={end_date}&show-fields=body,thumbnail&page-size=50&page={page}&api-key=test'

    data_folder = 'data'  # Folder to store the CSV files
    csv_prefix = f'articles_{start_date}'  # Combined CSV prefix
    articles = []
    page = 1
    csv_counter = 1

    while True:
        url = url_pattern.format(start_date=start_date, end_date=end_date, page=page)
        response = requests.get(url).json()
        news_list = response["response"]["results"]
        articles.extend(news_list)

        current_page = response["response"]["currentPage"]
        total_pages = response["response"]["pages"]
        print(page)
        if current_page == total_pages or page % 25 == 0:
            df = pd.DataFrame(articles)
            csv_filename = f'{csv_prefix}_{csv_counter}.csv'
            update_data_to_gcs(df, csv_filename)

            csv_counter += 1
            articles = []

        if current_page == total_pages:
            break

        page += 1

    return df


def get_filtered_articles(df: pd.DataFrame) -> None:
    model, vectorizer = load_model_from_gcs(MODEL_FILENAME, VECTORIZER_FILENAME)
    #df['fields'] = df['fields'].apply(ast.literal_eval) 
    df['prediction'] = df['fields'].apply(lambda x: predict(x['body'], vectorizer, model))
    df_filtered = df[df['prediction'] == True].copy()
    df_filtered.drop(columns=['prediction'], inplace=True)   
    print(df_filtered) 
    return df_filtered

if __name__ == '__main__':
    start_date = date(2020, 1, 1)
    end_date = date.today()
    df = fetch_articles(start_date, end_date)
    get_filtered_articles(df)
