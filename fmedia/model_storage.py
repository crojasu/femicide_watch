import joblib
from google.cloud import storage
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Get the environment variables
BUCKET_NAME = os.getenv("BUCKET_NAME")
MODEL_NAME = os.getenv("MODEL_NAME")
MODEL_FILENAME = os.getenv("MODEL_FILENAME")
VECTORIZER_FILENAME = os.getenv("VECTORIZER_FILENAME")
GOOGLE_APPLICATION_CREDENTIALS= os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

def save_model_to_gcs(model, model_filename, vectorizer, vectorizer_filename):
    credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    client = storage.Client.from_service_account_json(credentials_path)
    bucket = client.bucket(BUCKET_NAME)

    # Save the trained model
    model_blob = bucket.blob(f"{MODEL_NAME}/{model_filename}")
    joblib.dump(model, model_blob.open("wb"))

    # Save the vectorizer
    vectorizer_blob = bucket.blob(f"{MODEL_NAME}/{vectorizer_filename}")
    joblib.dump(vectorizer, vectorizer_blob.open("wb"))


def load_model_from_gcs(model_filename, vectorizer_filename):
    credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    client = storage.Client.from_service_account_json(credentials_path)    
    bucket = client.bucket(BUCKET_NAME)

    # Load the trained model
    model_blob = bucket.blob(f"{MODEL_NAME}/{model_filename}")
    model = joblib.load(model_blob.open("rb"))

    # Load the vectorizer
    vectorizer_blob = bucket.blob(f"{MODEL_NAME}/{vectorizer_filename}")
    vectorizer = joblib.load(vectorizer_blob.open("rb"))

    return model, vectorizer

def model_exists_in_gcs(model_filename, vectorizer_filename):
    credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    client = storage.Client.from_service_account_json(credentials_path)

    bucket = client.get_bucket(BUCKET_NAME)
    model_blob = bucket.blob(f"{MODEL_NAME}/{model_filename}")
    vectorizer_blob = bucket.blob(f"{MODEL_NAME}/{vectorizer_filename}")
    return model_blob.exists() and vectorizer_blob.exists()
