.PHONY: train run-script

train:
    python3 main.py

run-script:
    python3 fmedia/fetch_articles.py --year $(year)