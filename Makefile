.PHONY: train

train:
    python3 main.py

.PHONY: fetch_articles

fetch_articles: 
    python3 fmedia/fetch_articles.py --start_date $(start_date) --end_date $$(date +%Y-%m-%d)