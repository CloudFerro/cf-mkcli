import datetime

from pydantic import BaseModel, field_serializer


class Token(BaseModel):
    access_token: str | None = None
    refresh_token: str | None = None
    expires_in: datetime.datetime | None = None
    renew_after: datetime.datetime | None = None
    refresh_expires_in: datetime.datetime | None = None

    @field_serializer("expires_in", "renew_after", "refresh_expires_in")
    def serialize_created_at(self, value: datetime.datetime):
        if value is None:
            return None
        if value.tzinfo is None:
            value = value.replace(tzinfo=datetime.timezone.utc)
        return value.isoformat(timespec="microseconds")

    def clear(self):
        """Clear the token and its related fields"""
        self.access_token = None
        self.refresh_token = None
        self.expires_in = None
        self.renew_after = None
        self.refresh_expires_in = None

    def is_valid(self) -> bool:
        """Check if the token is valid"""
        return (
            self.access_token is not None
            and self.expires_in is not None
            and self.expires_in > datetime.datetime.now(tz=datetime.timezone.utc)
        )

    def is_refresh_token_valid(self) -> bool:
        return (
            self.refresh_expires_in is not None
            and self.refresh_expires_in
            > datetime.datetime.now(tz=datetime.timezone.utc)
        )

    def should_be_renew(self) -> bool:
        return (
            self.renew_after is not None
            and self.renew_after < datetime.datetime.now(tz=datetime.timezone.utc)
        )
