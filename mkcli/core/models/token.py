import datetime

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str | None = None
    refresh_token: str | None = None
    expires_in: datetime.datetime | None = None
    renew_after: datetime.datetime | None = None
    refresh_expires_in: datetime.datetime | None = None

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
            self.access_token is not None and self.expires_in > datetime.datetime.now()
        )

    def is_refresh_token_valid(self) -> bool:
        return self.refresh_expires_in > datetime.datetime.now()

    def should_be_renew(self) -> bool:
        return self.renew_after < datetime.datetime.now()
