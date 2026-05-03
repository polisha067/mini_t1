from app.models.user import User


def test_user_password_hash_roundtrip(app):
    with app.app_context():
        user = User(
            username="model_u",
            email="model_u@example.com",
            role="organizer",
        )
        user.set_password("correct_pass")
        assert user.check_password("correct_pass") is True
        assert user.check_password("wrong_pass") is False
