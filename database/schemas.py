from pydantic import BaseModel


class UserBase(BaseModel):
    user_id: str
