from src.core.system.router import get_health
from src.core.models import SystemHealthResponse


def test_health_check():
    # Arrange

    # Act
    response = get_health()

    # Assert
    assert isinstance(response, SystemHealthResponse)
    assert response.status == "ok"
