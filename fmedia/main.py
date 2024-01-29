from fastapi import FastAPI, Response, HTTPException, Request
from .model_storage import (
    load_model_from_gcs,
    model_exists_in_gcs,
    load_data_from_gcp,
    get_csv_filenames,
    get_gcs_bucket
)
from .preprocess import preprocess
from .train_evaluate_predict import predict, main
from dotenv import load_dotenv
import os
from datetime import date
import pandas as pd
from .fetch_articles import main as fetch_main
import subprocess
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from .models import PostcodeInfo, ArticleSummary, Article, ArticlesResponse
from typing import List
from pydantic import BaseModel

load_dotenv()  # Load environment variables from .env file

# Get the environment variables
BUCKET_NAME = os.getenv("BUCKET_NAME")
MODEL_FILENAME = os.getenv("MODEL_FILENAME")
VECTORIZER_FILENAME = os.getenv("VECTORIZER_FILENAME")

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/data", StaticFiles(directory="data"), name="data")

templates = Jinja2Templates(directory="templates")

csv_file_path = 'data/merged_email_data.csv'  # Replace with your CSV file path
df = pd.read_csv(csv_file_path)

# Load the model and vectorizer
if not model_exists_in_gcs(MODEL_FILENAME, VECTORIZER_FILENAME):
    main()
else:
    model, vectorizer = load_model_from_gcs(MODEL_FILENAME, VECTORIZER_FILENAME)

def normalize_postcode(postcode) -> str:
    """Remove spaces from the postcode. Handles non-string inputs."""
    if isinstance(postcode, str):
        return postcode.replace(" ", "")
    else:
        # Return a default value or handle it as you see fit
        return ""

@app.get("/", response_class=HTMLResponse, summary="Welcome to FMedia API", description="Welcome to the FMedia API! This API provides various functionalities to access and interact with media-related data. You can use the endpoints to fetch articles, make predictions, and more. Explore the API in different ways:\n\n1. **Web Documentation**: Access the API's interactive documentation at the root URL (e.g., `http://localhost:8000`) to learn about available endpoints and make test requests.\n2. **Simple HTML View**: You can access a simple HTML view by visiting the root URL in a web browser, which provides a user-friendly interface to interact with the API.\n3. **JSON Responses**: Send HTTP requests to the root endpoint to receive JSON responses containing data from the API. Start exploring the API and enjoy using its features!")
def read_root(request: Request):

    if "text/html" in request.headers["accept"]:        
        return templates.TemplateResponse("home_template.html", {"request": request})
    else:
        data = {"message": "Welcome to FMedia API!"}
        return JSONResponse(content=data)


@app.get("/predict/", summary="Get Prediction", 
         description="Predicts the outcome based on the provided text.")
def get_prediction(text: str):
    """
    Receives a text input and returns a prediction.

    The function first checks if the text is provided. If not, it returns an error.
    Otherwise, it preprocesses the text, makes a prediction using the loaded model,
    and returns the prediction result.

    Args:
    - text (str): Text input for which the prediction is to be made.

    Returns:
    - dict: A dictionary with a key 'prediction' and a boolean value indicating the prediction result.
    """
    if not text:
        return {"error": "Text not provided"}
    cleaned_text = preprocess(text)

    prediction = predict(cleaned_text, vectorizer=vectorizer, model=model)
    prediction = bool(prediction)

    return {"prediction": prediction}


@app.get("/fetch-articles/", response_model=ArticlesResponse, summary="Fetch articles for today")
async def fetch_articles_today(request: Request):
    """
    Fetches and returns articles for the current day along with a summary.
    The response includes a list of articles and summary statistics.

    The function checks the 'Accept' header in the request to determine 
    whether to return HTML or JSON.

    Returns:
    A JSON response containing articles and a summary if 'Accept' is not 'text/html'.
    An HTML response if 'Accept' is 'text/html'.
    """
    articles_data = fetch_main(None)  # Replace with actual function to fetch articles

    if "text/html" in request.headers.get('accept', ''):
        return templates.TemplateResponse("articles_template.html", {
            "request": request,
            "summary": articles_data["summary"],
            "articles": articles_data["articles"]
        })

    return ArticlesResponse(**articles_data)

# Endpoint to fetch articles by year
@app.get("/fetch-articles/{year}", response_model=ArticlesResponse, summary="Fetch articles for a specific year")
async def fetch_articles_year(year: int, request: Request):
    """
    Fetch and return articles for a specific year along with a summary.
    Supports returning either HTML or JSON based on 'Accept' header in request.
    """
    articles_data = fetch_main(year)  # Replace with actual function to fetch articles

    if "text/html" in request.headers.get('accept', ''):
        return templates.TemplateResponse("articles_template.html", {
            "request": request,
            "summary": articles_data["summary"],
            "articles": articles_data["articles"]
        })

    return ArticlesResponse(**articles_data)

    """
#@app.get("/fetch-articles/{start_year}/{end_year}")
async def fetch_articles_range(start_year: int, end_year: int, start_month: int = 1, end_month: int = 1):

    Fetch and return articles for a specified range of years and months.

    - **start_year**: The start year of the range.
    - **end_year**: The end year of the range.
    - **start_month**: The start month (default is 1).
    - **end_month**: The end month (default is 1).
    - **return**: A list of articles from the specified range of years and months.
  
    all_articles = []

    for year in range(start_year, end_year + 1):
        start_date = date(year, start_month, 1)
        end_date = date(year, end_month, 1)
        year_articles = fetch_articles(start_date, end_date)  # Replace with your article-fetching logic
        all_articles.extend(year_articles['articles'])
    
    return ArticlesResponse(articles=all_articles)
  """

@app.get("/info-by-postcode/{postcode}", response_model=List[PostcodeInfo], summary="Get information by postcode")
async def get_info_by_postcode(postcode: str):
    """
    Retrieve information for a given postcode.
    
    This endpoint normalizes the provided postcode to remove spaces and searches
    for matching entries in the data. It returns detailed information about
    the person or entity associated with that postcode.

    Parameters:
    - postcode: A string representing the postcode, with or without spaces.

    Returns:
    A list of information entries matching the provided postcode.
    """
    normalized_input_postcode = normalize_postcode(postcode)
    df['normalized_pcds'] = df['pcds'].apply(normalize_postcode)
    filtered_df = df[df['normalized_pcds'] == normalized_input_postcode]

    if filtered_df.empty:
        raise HTTPException(status_code=404, detail="No information found for this postcode")

    info = [PostcodeInfo(**row) for row in filtered_df.to_dict(orient='records')]
    return info
