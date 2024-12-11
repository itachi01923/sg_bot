from pydantic import BaseModel


class UserBase(BaseModel):
    id: int
    user_id: str
    is_active: bool
