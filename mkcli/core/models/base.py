import datetime
from typing import ClassVar, Optional
from pydantic import BaseModel, ConfigDict, field_serializer


def keys_to_attrs(keys: list[str]) -> list[str]:
    return [k.replace(" ", "_").strip().lower() for k in keys]


class BaseResourceModel(BaseModel):
    """Mk8s Base Resource Model"""

    model_config = ConfigDict(extra="allow")

    table_columns: ClassVar[list[str]]
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

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

        result = []  # TODO(EA): refactor it later
        for key in keys:
            value = self.__getattribute__(key)
            # Format datetime fields for table display
            if isinstance(value, datetime.datetime):
                value = value.strftime("%Y-%m-%d %H:%M:%S")
            result.append(value)
        return result
