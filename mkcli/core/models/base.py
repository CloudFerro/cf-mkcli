import datetime
from typing import ClassVar
from pydantic import BaseModel, ConfigDict, field_serializer


def keys_to_attrs(keys: list[str]) -> list[str]:
    return [k.replace(" ", "_").strip().lower() for k in keys]


class BaseResourceModel(BaseModel):
    """Mk8s Base Resource Model"""

    model_config = ConfigDict(extra="allow")

    table_columns: ClassVar[list[str]]
    created_at: datetime.datetime
    updated_at: datetime.datetime

    # TODO(EA): consider using pendulum for datetime handling
    @field_serializer("created_at", "updated_at")
    def serialize_created_at(self, value: datetime.datetime):
        return value.isoformat(timespec="microseconds").replace("+00:00", "") + "Z"

    def as_table_row(self) -> list[str]:
        keys = keys_to_attrs(self.table_columns)
        try:
            for key in keys:
                _ = self.__getattribute__(key)
        except AttributeError as e:
            raise AttributeError(
                f"AttributeError: {e}. Available attributes: {list(self.model_fields.keys())}"
            ) from e

        _dict = self.model_dump()  # TODO(EA): format datetimes explicitly and leave serialize_created_at for json dumps
        return [  # or for properties, model dump for serialisation
            _dict.get(x) or self.__getattribute__(x) for x in keys
        ]
