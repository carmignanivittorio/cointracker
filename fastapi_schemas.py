from pydantic import BaseModel


class Pong(BaseModel):
    message: str = "pong"
