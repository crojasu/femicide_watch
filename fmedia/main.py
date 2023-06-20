from fastapi import FastAPI, Response
from fmedia.model_storage import (
    load_model_from_gcs,
    model_exists_in_gcs,
    load_data_from_gcp,
    update_data_to_gcs,
    combine_csv_files,
    get_csv_filenames,
)
from fmedia.preprocess import preprocess
from fmedia.train_evaluate_predict import predict, main
from dotenv import load_dotenv
import os
from datetime import date
import pandas as pd
from fmedia.fetch_articles import fetch_articles, get_filtered_articles


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

@app.get("/fetch-articles")
def fetch_articles_endpoint(start_date: date = None, end_date: date = None):
    if start_date is None and end_date is None:
        csv_filenames = get_csv_filenames('filtered_articles')
        if csv_filenames:
            csv_filenames.sort()
            csv_filename = csv_filenames[0]
            df_filtered = combine_csv_files(csv_filename)
        else:
            csv_filenames = get_csv_filenames('articles')
            if csv_filenames:
                csv_filenames.sort()
                oldest_csv_filename = min(csv_filenames, key=extract_start_date)
                df = combine_csv_files(oldest_csv_filename)
                model, vectorizer = load_model_from_gcs(MODEL_FILENAME, VECTORIZER_FILENAME)
                df_filtered = get_filtered_articles(df)
                if df_filtered.empty:
                    return {"message": "No filtered articles found"}
                csv_filename = f"filtered_articles.csv"
                update_data_to_gcs(df_filtered, csv_filename)
            else:
                return {"error": "No existing articles found"}
    else:
        df = fetch_articles(start_date, end_date)
        model, vectorizer = load_model_from_gcs(MODEL_FILENAME, VECTORIZER_FILENAME)
        df_filtered = get_filtered_articles(df)
        if df_filtered.empty:
            return {"message": "No filtered articles found"}
        csv_filename = f"filtered_articles.csv"
        update_data_to_gcs(df_filtered, csv_filename)

    json_response = df_filtered[["webTitle", "webUrl"]].to_dict(orient="records")
    csv_response = df_filtered.to_csv(index=False)
    return Response(
        content=csv_response,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={csv_filename}"},
    ), json_response