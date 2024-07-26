from pydantic import BaseModel


class SearchQuery(BaseModel):
    user_id: int
    message: str
