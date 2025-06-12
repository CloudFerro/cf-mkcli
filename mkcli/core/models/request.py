from pydantic import BaseModel
import json


class RequestPayload(BaseModel):
    @classmethod
    def from_json(cls, data: str) -> "RequestPayload":
        json_data = json.loads(data)
        obj = cls(**json_data)
        return obj
