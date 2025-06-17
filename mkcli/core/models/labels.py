from pydantic import BaseModel


class Label(BaseModel):
    key: str
    value: str

    def as_table_cell(self):
        return f"{self.key}={self.value}"


class Taint(BaseModel):
    key: str
    value: str
    effect: str

    def as_table_cell(self):
        return f"{self.key}={self.value}:{self.effect}"
