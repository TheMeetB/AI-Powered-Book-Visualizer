from datetime import datetime

from pydantic import BaseModel, EmailStr


class MongoUserData(BaseModel):
    username: str
    email: EmailStr
    password: str | None
    created_at: datetime
    updated_on: datetime
    is_deleted: bool = False
