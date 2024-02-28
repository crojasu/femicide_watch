# Femicide Media Watch

## Overview

incluide in this overview: that the app is deployed in heroku , that works, with api fast, docker, and python, and we use this librerys fastapi
uvicorn
joblib
google-cloud-storage
nltk
pandas
scikit-learn
python-dotenv
jinja2
mediacloud-api-legacy 

Femicide Media Watch is a Python application designed to predict whether a text is about femicide. This tool aids in filtering newspaper articles, highlighting relevant content, and storing it in a database. It aims to identify indicators from the text, including the style of writing, to enhance awareness and understanding of femicide reporting.

## Repository Structure

- `fmedia/`: Contains all the logic of the model.
  - `fetch_articles.py`: Logic for fetching articles from The Guardian.
  - `main.py`: Manages the endpoint for Uvicorn.
  - `model_storage.py`: Functions for cloud storage management.
  - `preprocess.py`: Preprocessing of text for analysis.
  - `train_evaluate_predict.py`: Manages training, evaluation, and prediction functions.

## Running the Application

### Endpoints

- **Home**: Access the home page at `http://localhost:8000/`. This serves as the entry point to the application.

- **Predict**: Predict whether a given text is about femicide by visiting `http://localhost:8000/predict/?text=your-text-to-predict`. Replace `your-text-to-predict` with the actual text you wish to analyze.

- **Fetch Articles**: This endpoint fetches and displays articles related to femicide. If no dates are provided, it displays articles from the last search performed. It returns a CSV file with the articles predicted and a JSON object with the article IDs and web titles.

  - **Example**: `http://localhost:8000/fetch-articles?start_date=2020-01-01&end_date=2023-01-01`
  
  - **Check Today's Articles**: To check for articles published today, visit `http://femicidewatch-5a7c7e9e2d35.herokuapp.com/fetch-articles/`. This endpoint is especially useful for daily monitoring.

### Daily Backend Job

A backend job is executed daily through a sidekiq job that invokes the `fetch_articles` function with today's date. This ensures that the application continually updates its dataset with the latest articles.

## Building the Dataset and Training the Model

The foundation of Femicide Media Watch lies in its ability to accurately predict femicide-related content. This capability is derived from a carefully curated dataset and a rigorously trained model.

### Creating the Dataset

We initiated the dataset creation by fetching articles from The Guardian's API. The objective was to filter the vast database for articles specifically related to femicide. To achieve this, we applied the following filters:

#### Keywords
- murder
- homicide
- femicide
- feminicide
- murdered
- dead
- death
- killed
- shot
- stabbed
- struck
- strangled
- "lifeless"

#### Entities
- woman
- "girl"
- "a young woman"
- "a teenage girl"
- "a girl"
- "body of a woman"
- "prostitute"
- "sex worker"

These filters were strategically combined using logical operators (AND, OR) to refine the search results. The API call also included parameters for pagination, specific fields (body, thumbnail), page size, and the API key for authentication.

```plaintext
url_pattern = 'https://content.guardianapis.com/search?q=(murder OR homicide OR femicide OR feminicide OR murdered OR dead OR death OR killed OR shot OR stabbed OR struck OR strangled OR "lifeless") AND (woman OR girl OR "a young woman" OR "a teenage girl" OR "a girl" OR "body of a woman" OR prostitute OR "sex worker")&from-date={start_date}&to-date={end_date}&show-fields=body,thumbnail&page-size=50&page={page}&api-key=test'

## Training the Model

The model's training began with a base dataset of 10,000 news articles filtered through a topic identification model. From this subset, we manually selected 1,000 articles that genuinely reported on femicide cases. This meticulous selection process ensured the model's training data was both relevant and accurate.

### For Future Training

To retrain the model with an expanded dataset, ensure the environment variable `dataset_with_ceros` points to the new file stored in GCP. Use the following command to initiate retraining:

```bash
make train f"data/{dataset_with_ceros}"

This process will train the model with the new dataset, automatically updating the production model and vectorizer if the new model demonstrates improved precision.

## License

This project is open-source and available for use and modification. However, we kindly ask that any use, distribution, or modification of this project includes proper attribution back to the original authors. If you find this project useful for your work or if it inspires the development of your own projects, please give credit by citing this project.

## Acknowledgments

This project was developed under the umbrella and with the support of WeLevelUp. We extend our deepest gratitude to WeLevelUp for their encouragement, resources, and commitment to fostering innovation and development in the field of technology for social good.



