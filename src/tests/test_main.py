from main import get_health

def test_health_check():
    """Unit test for the synchronous health check function."""
    # Arrange
    # No complex setup required for synchronous health check

    # Act
    response = get_health()

    # Assert
    assert response == {"status": "ok"}
