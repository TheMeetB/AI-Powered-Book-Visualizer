from pydantic import BaseModel


class MongoUserBookData(BaseModel):
    user_id: str
    book_id: str
