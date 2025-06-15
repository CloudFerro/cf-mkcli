from pydantic import BaseModel
import json


class RequestPayload(BaseModel):
    @classmethod
    def from_json(cls, data: str) -> "RequestPayload":
        try:
            json_data = json.loads(data)
            obj = cls(**json_data)
        except Exception as e:
            raise ValueError(f"Invalid JSON data: {e}")
        return obj
