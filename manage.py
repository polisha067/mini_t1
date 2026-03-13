from app import create_app
import app.models  # чтобы Alembic видел модели

app = create_app()
