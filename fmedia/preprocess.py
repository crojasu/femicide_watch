import re
import string
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
from nltk import word_tokenize

def preprocess(text):
    def imitating_guardian(text):
        return {"body": text}

    def just_text(text):
        CLEANR = re.compile('<.*?>')
        cleantext = re.sub(CLEANR, '', text['body'])
        return cleantext

    def basic_cleaning(sentence):
        sentence = sentence.strip()
        sentence = sentence.lower()
        sentence = ''.join(char for char in sentence if not char.isdigit())
        for punctuation in string.punctuation:
            sentence = sentence.replace(punctuation, '')
        return sentence

    def remove_stopwords(text):
        stop_words = set(stopwords.words('english'))
        tokenized = word_tokenize(text)
        without_stopwords = [word for word in tokenized if not word in stop_words]
        return without_stopwords

    def lemma(text):
        lemmatizer = WordNetLemmatizer()
        lemmatized = [lemmatizer.lemmatize(word, pos="n") for word in text]
        lemmatized_string = " ".join(lemmatized)
        return lemmatized_string

    cleaned_text = imitating_guardian(text)
    cleaned_text = just_text(cleaned_text)
    cleaned_text = basic_cleaning(cleaned_text)
    cleaned_text = remove_stopwords(cleaned_text)
    cleaned_text = lemma(cleaned_text)

    return cleaned_text
