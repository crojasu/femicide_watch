from fastapi import FastAPI
from fmedia.model_storage import save_model_to_gcs, load_model_from_gcs, model_exists_in_gcs
from fmedia.preprocess import preprocess
from fmedia.train_evaluate_predict import predict, main
from dotenv import load_dotenv
import os
import numpy as np

load_dotenv()  # Load environment variables from .env file

# Get the environment variables
BUCKET_NAME = os.getenv("BUCKET_NAME")
MODEL_NAME = os.getenv("MODEL_NAME")
MODEL_FILENAME = os.getenv("MODEL_FILENAME")
VECTORIZER_FILENAME = os.getenv("VECTORIZER_FILENAME")
csv_filename= os.getenv("csv_filename")

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

    prediction = predict(cleaned_text, vectorizer, model)
    prediction = bool(prediction)

    return {"prediction": prediction}
