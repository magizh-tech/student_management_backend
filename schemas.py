

from typing import Optional
from pydantic import BaseModel


class CreateUser(BaseModel):
    username: str
    email: str
    password: str
    phone_number: str
    address:Optional[str]=None

