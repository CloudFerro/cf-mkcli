from pydantic import BaseModel
from typing import Optional
import json


class RequestPayload(BaseModel):
    _raw_data: Optional[str] = None

    @classmethod
    def from_json(cls, data: str) -> "RequestPayload":
        json_data = json.loads(data)
        obj = cls(**json_data, _raw_data=data)
        return obj

    @property
    def raw_data(self) -> str:
        if self._raw_data:
            return self._raw_data
        return json.dumps(self.dict(), indent=2)
