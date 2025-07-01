from pydantic import BaseModel


class SimpleStringResponse(BaseModel):
    response: str