from pydantic import BaseModel


class UserBase(BaseModel):
    id: int
    user_id: str
    is_active: bool


class CryptoBase(BaseModel):
    symbol: str
    title: str
    is_active: bool
    percent: int


class CryptoResponse(CryptoBase):
    id: int
