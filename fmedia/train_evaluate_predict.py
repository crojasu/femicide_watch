import joblib
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from .preprocess import preprocess
from .model_storage import save_model_to_gcs

def train(X, y):
    vectorizer = CountVectorizer(ngram_range=(1, 1), max_df=1.0, max_features=None)
    X_bow = vectorizer.fit_transform(X)

    naive = MultinomialNB(alpha=0.1)
    naive.fit(X_bow, y)

    return vectorizer, naive

def evaluate(vectorizer, model, X_test, y_test):
    X_test_bow = vectorizer.transform(X_test)
    y_pred = model.predict(X_test_bow)
    accuracy = (y_pred == y_test).mean()  # Calculate accuracy
    return accuracy

def predict(text, vectorizer, model):
    cleaned_text = preprocess(text)
    X_pred = vectorizer.transform([cleaned_text])
    y_pred = model.predict(X_pred)
    print(y_pred[0])
    return y_pred[0]

def main():
    df = pd.read_csv("data/femicide_final_with_ceros.csv")
    df["fields"] = df['clean_text']
    df_solo_1 = df[df.topic == 1]
    X = df_solo_1['fields']
    y = df_solo_1['cases']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)
    vectorizer, model = train(X_train, y_train)
    accuracy = evaluate(vectorizer, model, X_test, y_test)
    save_model_to_gcs(model, "model.joblib", vectorizer, "vectorizer.joblib")
    print("Accuracy:", accuracy)


if __name__ == '__main__':
    main()
