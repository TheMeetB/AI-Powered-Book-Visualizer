from typing import Union, Dict

from pydantic import BaseModel


class MongoBookAiData(BaseModel):
    book_id: str
    chapter_id: str
    summary: str
    character: Union[str, Dict[str, str]]
    places: Union[str, Dict[str, str]]
