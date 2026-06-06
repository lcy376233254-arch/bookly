from pydantic import BaseModel
from datetime import datetime,date
import uuid
from typing import List
from pydantic import Field
from src.reviews.schemas import ReviewModel
from src.tags.schemas import TagModel

class BookModel(BaseModel):
    uid: uuid.UUID
    title: str
    author: str
    publisher: str
    publish_date: date
    page_count: int
    language: str
    created_at: datetime
    updated_at: datetime

class BookDetailModel(BookModel):
    reviews: List[ReviewModel] = Field(default_factory=list)
    tags: List[TagModel] = Field(default_factory=list)

class BookCreateModel(BaseModel):
    title: str
    author: str
    publisher: str
    publish_date: date
    page_count: int
    language: str

class BookUpdateModel(BaseModel):
    title: str
    author: str
    publisher: str
    page_count: int
    language: str