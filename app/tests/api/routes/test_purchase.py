from unittest.mock import patch

from fastapi.testclient import TestClient


def test_purchase_lower_ten(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    pass
