from datetime import datetime
from typing import List

from pydantic import BaseModel


class MongoBookData(BaseModel):
    title: str
    book_type: str
    book_path: str
    cover_path: str
    audio_parent_path: str
    image_parent_path: str
    audio_paths: List[str] | None = None
    image_paths: List[str] | None = None
    like: bool = False
    bookmark: bool = False
    uploaded_on: datetime