from main import get_health


def test_health_check():
    # Arrange

    # Act
    response = get_health()

    # Assert
    assert response == {"status": "ok"}
