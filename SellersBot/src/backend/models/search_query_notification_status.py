from typing import Union

from pydantic import BaseModel


class SearchQueryNotificationStatus(BaseModel):
    message: str
    data: Union[int, str, None]
