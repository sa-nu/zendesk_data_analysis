import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class ZendeskConfig:
    subdomain: str
    email: str
    api_token: str

    @property
    def base_url(self) -> str:
        return f"https://{self.subdomain}.zendesk.com/api/v2"

    @property
    def auth(self) -> tuple[str, str]:
        return (f"{self.email}/token", self.api_token)


def load_config() -> ZendeskConfig:
    load_dotenv()

    subdomain = os.getenv("ZENDESK_SUBDOMAIN")
    email = os.getenv("ZENDESK_EMAIL")
    api_token = os.getenv("ZENDESK_API_TOKEN")

    missing = []
    if not subdomain:
        missing.append("ZENDESK_SUBDOMAIN")
    if not email:
        missing.append("ZENDESK_EMAIL")
    if not api_token:
        missing.append("ZENDESK_API_TOKEN")

    if missing:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}. "
            "Please set them in a .env file."
        )

    return ZendeskConfig(subdomain=subdomain, email=email, api_token=api_token)
