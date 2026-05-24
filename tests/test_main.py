from src.core.system.router import get_health
from src.core.system.models import SystemHealthResponse, HealthStatus


def test_health_check():
    # Arrange

    # Act
    response = get_health()

    # Assert
    assert isinstance(response, SystemHealthResponse)
    assert response.status == HealthStatus.OK
