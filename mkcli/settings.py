from pydantic_settings import BaseSettings


class DefaultContext(BaseSettings):
    name: str = "creodias"
    realm: str = "Creodias-new"
    client_id: str = "auth-portal"
    scope: str = "openid aud-public"
    identity_server_url: str = "https://identity.cloudferro.com/auth/"
    token: str = None
    public_key: str = None


default_context = DefaultContext()
