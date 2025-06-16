from pydantic import BaseModel


class Label(BaseModel):
    key: str
    value: str


class Taint(BaseModel):
    key: str
    value: str
    effect: str
