import requests
import pandas as pd
from datetime import date
from fmedia.train_evaluate_predict import predict, main
import ast
import io
from dotenv import load_dotenv
import os
import joblib
from google.cloud import storage
import glob
from typing import List

load_dotenv()  # Load environment variables from .env file

# Get the environment variables
BUCKET_NAME = os.getenv("BUCKET_NAME")
MODEL_NAME = os.getenv("MODEL_NAME")
MODEL_FILENAME = os.getenv("MODEL_FILENAME")
VECTORIZER_FILENAME = os.getenv("VECTORIZER_FILENAME")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

def get_gcs_bucket():
    credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    client = storage.Client.from_service_account_json(credentials_path)
    bucket = client.bucket(BUCKET_NAME)
    return bucket

def save_model_to_gcs(model, model_filename, vectorizer, vectorizer_filename):
    bucket = get_gcs_bucket()

    # Save the trained model
    model_blob = bucket.blob(f"{MODEL_NAME}/{model_filename}")
    joblib.dump(model, model_blob.open("wb"))

    # Save the vectorizer
    vectorizer_blob = bucket.blob(f"{MODEL_NAME}/{vectorizer_filename}")
    joblib.dump(vectorizer, vectorizer_blob.open("wb"))


def load_model_from_gcs(model_filename, vectorizer_filename):
    bucket = get_gcs_bucket()

    # Load the trained model
    model_blob = bucket.blob(f"{MODEL_NAME}/{model_filename}")
    model = joblib.load(model_blob.open("rb"))

    # Load the vectorizer
    vectorizer_blob = bucket.blob(f"{MODEL_NAME}/{vectorizer_filename}")
    vectorizer = joblib.load(vectorizer_blob.open("rb"))

    return model, vectorizer

def model_exists_in_gcs(model_filename, vectorizer_filename):
    bucket = get_gcs_bucket()
    model_blob = bucket.blob(f"{MODEL_NAME}/{model_filename}")
    vectorizer_blob = bucket.blob(f"{MODEL_NAME}/{vectorizer_filename}")
    return model_blob.exists() and vectorizer_blob.exists()

def update_data_to_gcs(df, csv_filename):
    bucket = get_gcs_bucket()

    # Save the DataFrame as CSV
    csv_blob = bucket.blob(f"data/{csv_filename}")
    df_csv = df.to_csv(index=False)
    csv_blob.upload_from_string(df_csv, 'text/csv')

    return f"Data updated to {csv_filename} in Google Cloud Storage"

def load_data_from_gcp(csv_filename):
    bucket = get_gcs_bucket()

    blob = bucket.blob(f"data/{csv_filename}")
    if not blob.exists():
        raise FileNotFoundError(f"CSV file '{csv_filename}' does not exist in the bucket")

    content = blob.download_as_text()
    df = pd.read_csv(io.StringIO(content))

    return df

def get_csv_filenames(csv_prefix: str) -> List[str]:
    data_folder = 'data'  # Folder where the CSV files are stored
    csv_files = glob.glob(os.path.join(data_folder, f"{csv_prefix}_*.csv"))
    return csv_files

def combine_csv_files(csv_filenames: List[str]) -> pd.DataFrame:
    dfs = []
    for csv_file in csv_filenames:
        print(f"Processing {csv_file}")
        df = pd.read_csv(csv_file)
        dfs.append(df)
    print(f"Number of DataFrames: {len(dfs)}")
    if len(dfs) == 0:
        print("No DataFrames to concatenate.")
        return None
    combined_df = pd.concat(dfs, ignore_index=True)
    return combined_df

