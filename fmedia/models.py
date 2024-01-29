from pydantic import BaseModel
from typing import List, Optional

class PostcodeInfo(BaseModel):
    Name_Display_As: Optional[str] = None
    Name_List_As: Optional[str] = None
    Party: Optional[str] = None
    Constituency: Optional[str] = None
    Email: Optional[str] = None
    Name: Optional[str] = None
    pcon: Optional[str] = None
    pcds: Optional[str] = None
    PCON23CD: Optional[str] = None
    PCON23NM: Optional[str] = None
    constituency: Optional[str] = None
    party_before_election: Optional[str] = None
    party_after_election: Optional[str] = None
    normalized_pcds: Optional[str] = None

class PredictionResponse(BaseModel):
    prediction: bool

class Article(BaseModel):
    id: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    thumbnail: Optional[str] = None
    type: Optional[str] = None
    sectionId: Optional[str] = None
    sectionName: Optional[str] = None
    webPublicationDate: Optional[str] = None
    webUrl: Optional[str] = None
    apiUrl: Optional[str] = None

class ArticleSummary(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    total_articles_processed: int
    total_true_predictions: int

class ArticlesResponse(BaseModel):
    summary: dict
    articles: List[Article]