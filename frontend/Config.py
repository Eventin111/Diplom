import os
from dataclasses import dataclass


@dataclass(frozen=True)
class FrontendSettings:
    app_name: str = os.getenv("REACT_APP_NAME", "Swipelt")
    api_base_url: str = os.getenv("REACT_APP_API_BASE_URL", "http://localhost:8000")
    use_mock_data: bool = os.getenv("REACT_APP_USE_MOCK_DATA", "true").lower() == "true"
    mock_delay_ms: int = int(os.getenv("REACT_APP_MOCK_DELAY_MS", "200"))
    auth_init_delay_ms: int = int(os.getenv("REACT_APP_AUTH_INIT_DELAY_MS", "300"))


settings = FrontendSettings()

