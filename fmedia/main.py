from fastapi import FastAPI, Response, HTTPException
from .model_storage import (
    load_model_from_gcs,
    model_exists_in_gcs,
    load_data_from_gcp,
    update_data_to_gcs,
    combine_csv_files,
    get_csv_filenames,
    get_gcs_bucket
)
from .preprocess import preprocess
from .train_evaluate_predict import predict, main
from dotenv import load_dotenv
import os
from datetime import date
import pandas as pd
from .fetch_articles import fetch_articles_year, main as fetch_main
import subprocess

load_dotenv()  # Load environment variables from .env file

# Get the environment variables
BUCKET_NAME = os.getenv("BUCKET_NAME")
MODEL_FILENAME = os.getenv("MODEL_FILENAME")
VECTORIZER_FILENAME = os.getenv("VECTORIZER_FILENAME")

app = FastAPI()


# Load the model and vectorizer
if not model_exists_in_gcs(MODEL_FILENAME, VECTORIZER_FILENAME):
    main()
else:
    model, vectorizer = load_model_from_gcs(MODEL_FILENAME, VECTORIZER_FILENAME)

@app.get("/")
def read_root():
    return {"message": "Welcome to FMedia API!"}


@app.get("/predict/")
def get_prediction(text: str):
    if not text:
        return {"error": "Text not provided"}
    cleaned_text = preprocess(text)

    prediction = predict(cleaned_text, vectorizer=vectorizer, model=model)
    prediction = bool(prediction)

    return {"prediction": prediction}

@app.get("/fetch-articles/")
async def fetch_articles_today():
    articles = fetch_main()
    
    return articles

@app.get("/fetch-articles/{year}")
async def fetch_articles_year(year: int):
    articles = fetch_main(year)
    
    return articles

@app.get("/fetch-articles/{start_year}/{end_year}")
async def fetch_articles_range(start_year: int, end_year: int):
    all_articles = []
    for year in range(start_year, end_year+1):
        year_articles = fetch_main(year)
        all_articles.extend(year_articles['articles'])
    
    return all_articles

