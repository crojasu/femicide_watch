Femicide media watch
python app that predict if a text is about a femicide or not.
This help us to filter articles from newspaper and highlith them and store in a database.
TODO, identify indicators from text, as well as style of writting.

API of newspaper:
Today it is connected to The Guardian. 
TODO: enable more API

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
girl
"a young woman"
"a teenage girl"
"a girl"
"body of a woman"
prostitute
"sex worker

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

