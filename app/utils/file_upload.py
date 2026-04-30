import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 6 * 1024 * 1024


def allowed_file(filename: str) -> bool:
    """Проверка расширения файла"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_file(file, folder: str = 'logos') -> str:
    """Сохраняет загруженный файл и возвращает относительный путь"""
    if not file or file.filename == '':
        raise ValueError("Файл не выбран")

    if not allowed_file(file.filename):
        raise ValueError(f"Разрешены только: {', '.join(ALLOWED_EXTENSIONS)}")

    if file.content_length and file.content_length > MAX_FILE_SIZE:
        raise ValueError(f"Файл слишком большой (макс. {MAX_FILE_SIZE // 1024 // 1024} MB)")

    # Генерируем уникальное имя файла
    ext = file.filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{ext}"

    # Путь для сохранения
    upload_folder = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'uploads'), folder)
    os.makedirs(upload_folder, exist_ok=True)

    file_path = os.path.join(upload_folder, unique_filename)
    file.save(file_path)

    # Возвращаем относительный путь для БД
    return f"{folder}/{unique_filename}"