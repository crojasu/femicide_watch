Femicide media watch
This repository is a python app that predict if a text is about a femicide or not.
This help us to filter articles from newspaper and highlith them and store in a database.
TODO, identify indicators from text, as well as style of writting.


Repository:

This repositorie contain a folder called fmedia that has all the logic of the model. 
-	fetch_srticles, is the file that make the logic of fetching articles from the guardian.
-	main, is the file that manage the endpoint for uvicorn
-	model_storage, manage all the functions that manage the cloud
- 	preprocess, managing all the preprocess for the text to be analiced
-	train_evaluate_predict, is the file that manage the train, evaluate and predict functions for each text. 

In order to run this code, we need to have a model saved. 

If there are no model:
1.- If there are no trained model , and To train_evaluate_and_save the model, we need to run train_evaluate_predict.main, this will be run with a file called femicide_final_with_ceros who was our first cleaned and evaluated dataset.
This will saved the models in the database.

to know more about how this database was build please check xxx "Building the dataset"

commands:

In order to make run the program to train and save the models:

make train_evalute_first_time start_date end_date

where start_date and end_date have to have this format: +%Y-%m-%d


2.- Call each endpoint :
Sure, I understand. I will modify the fetch_articles function so that it only returns a JSON object if no year is provided in the endpoint, which means the search is for today's date. If a year is provided, it will continue to fetch articles, store them in a CSV file and also return the articles. If two years are provided as a range, it will first check if CSV files exist for those years and if not, fetch articles for those missing years and save them in a CSV file. After this, it will return all articles for each year in the range.

Endpoints
@home
http://localhost:8000/

@call for predict
example:
http://localhost:8000/predict/?text=the-text-to-predict

@call for fetch_articles
example:
http://localhost:8000/fetch-articles?start_date=2020-01-01&end_date=2023-01-01
if no date is given it will display the articles of the last search done
It return a csv with the articles predicted as well as a json with the id and the webtitle.

3.- A backend job is excecuted daily true a sidekiq job, that call the fetch_articles witht he date Today.


"Building the dataset"
We created the dataset calling the api of the guardian with a url that make a first filtered call of all the articles.

The api url we are using to make a first filter from the database of the guardian contains the following filters:

Keywords:

murder
homicide
femicide
feminicide
murdered
dead
death
killed
shot
stabbed
struck
strangled
"lifeless"
Entities:

woman
"girl"
"a young woman"
"a teenage girl"
"a girl"
"body of a woman"
"prostitute"
"sex worker"

These filters are combined using logical operators (AND, OR) to retrieve articles related to the specified keywords and entities within the specified date range. The URL also includes additional parameters for pagination, field selection (body, thumbnail), page size, and API key.

    url_pattern = 'https://content.guardianapis.com/search?q=(murder%20OR%20homicide%20OR%20femicide%20OR%20feminicide%20OR%20murdered%20OR%20dead%20OR%20death%20OR%20killed%20OR%20murdered%20OR%20shot%20OR%20stabbed%20OR%20struck%20OR%20strangled%20OR%20"lifeless")%20AND%20(woman%20OR%20girl%20OR%20"a%20young%20woman"%20OR%20"a%20teenage%20girl"%20OR%20"a%20girl"%20OR%20"body%20of%20a%20woman"%20OR%20prostitute%20OR%20"sex%20worker")&from-date={start_date}&to-date={end_date}&show-fields=body,thumbnail&page-size=50&page={page}&api-key=test'

This model was train based in a databse of 10000 news.
we first filter the result throug a model for identify topics.After this we read and manually selected 1000 true cases.
TODO his selection can and should be review and amplified.

For retrain the model with a bigger dataset:
Please set the environmet variable 
dataset_with_ceros=to the name of the file stored in GCP with the following path f"data/{dataset_with_ceros}"

Run the MAKE command: make train f"data/{dataset_with_ceros}"
it will train the model and if is better in relation to precision score, it will automatic set this new model and vectorice to production.

please follow the guidelines of the csv file to update for dataset_with_ceros.

API of newspaper:
Today it is connected to The Guardian. 
TODO: enable more API

How are we going to improove our model.
We will create a bigger dataset with the articles we already detected daily.

