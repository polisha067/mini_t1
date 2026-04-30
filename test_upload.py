#!/usr/bin/env python3
"""
🧪 Тест загрузки, обновления и удаления логотипов конкурсов
Запуск: python test_upload.py
"""

import requests
import os
import shutil
import time
import uuid

# =============================================================================
# 🔧 НАСТРОЙКИ
# =============================================================================
BASE_URL = "http://localhost:5000/api"
IMAGE_PATH = "C:/mini_t1/test.jpg"
IMAGE_PATH_V2 = "C:/mini_t1/test_v2.jpg"
EMAIL = "org@test.com"
PASSWORD = "TestPass123!"
UPLOADS_DIR = "C:/mini_t1/uploads/logos"


def log(msg: str, color: str = "white"):
    colors = {"green": "\033[92m", "red": "\033[91m", "yellow": "\033[93m", "cyan": "\033[96m", "white": "\033[0m"}
    print(f"{colors.get(color, '')}{msg}\033[0m")


def wait_for_file(path: str, timeout: int = 5) -> bool:
    for _ in range(timeout * 2):
        if os.path.exists(path): return True
        time.sleep(0.5)
    return False


def get_organizer_token():
    """Пытается войти, а при 401/409 автоматически регистрирует нового уникального организатора"""
    # 1. Пробуем логин со стандартными учётками
    login_resp = requests.post(f"{BASE_URL}/auth/login", json={"email": EMAIL, "password": PASSWORD})
    if login_resp.status_code == 200:
        return login_resp.json()["access_token"]

    # 2. Если вход не удался — создаём уникального тестового пользователя
    log("⚠️ Вход не удался. Регистрация нового тестового организатора...", "yellow")
    unique_id = uuid.uuid4().hex[:8]
    unique_email = f"test_org_{unique_id}@local.test"
    unique_username = f"test_org_{unique_id}"

    reg_resp = requests.post(f"{BASE_URL}/auth/register", json={
        "username": unique_username,
        "email": unique_email,
        "password": PASSWORD,
        "role": "organizer"
    })

    if reg_resp.status_code in (200, 201, 409):  # 409 = уже есть, пробуем залогиниться
        log(f"✅ Аккаунт готов: {unique_email}", "green")
        login_resp = requests.post(f"{BASE_URL}/auth/login", json={"email": unique_email, "password": PASSWORD})
        if login_resp.status_code == 200:
            return login_resp.json()["access_token"]

    raise Exception(f"❌ Не удалось получить токен. Ответ сервера: {reg_resp.text}")


def test_upload_flow():
    log("\n🔍 Проверка окружения...", "cyan")

    if not os.path.exists(IMAGE_PATH):
        log(f"❌ Файл не найден: {IMAGE_PATH}", "red")
        return False
    log(f"✅ Файл найден: {IMAGE_PATH}", "green")

    # Копируем файл для теста обновления
    if os.path.exists(IMAGE_PATH_V2): os.remove(IMAGE_PATH_V2)
    shutil.copy2(IMAGE_PATH, IMAGE_PATH_V2)
    log(f"✅ Создан тестовый файл для обновления", "green")

    # Получаем токен
    log("\n🔐 Авторизация...", "cyan")
    try:
        token = get_organizer_token()
        log(f"✅ Токен получен: {token[:30]}...", "green")
    except Exception as e:
        log(str(e), "red")
        return False
    headers = {"Authorization": f"Bearer {token}"}

    # =============================================================================
    # 📤 ТЕСТ 1: Создание конкурса с логотипом
    # =============================================================================
    log("\n📤 ТЕСТ 1: Создание конкурса с загрузкой логотипа...", "cyan")
    with open(IMAGE_PATH, "rb") as f:
        files = {"logo": ("test.jpg", f, "image/jpeg")}
        data = {"name": f"Тест загрузки {uuid.uuid4().hex[:4]}", "description": "Авто-тест",
                "start_date": "2024-06-01T00:00:00", "end_date": "2024-06-30T23:59:59"}
        create_resp = requests.post(f"{BASE_URL}/contests", headers=headers, data=data, files=files)

    if create_resp.status_code not in (200, 201):
        log(f"❌ Ошибка создания ({create_resp.status_code}): {create_resp.text}", "red")
        return False

    contest = create_resp.json()["contest"]
    contest_id = contest["id"]
    logo_path_1 = contest.get("logo_path")
    log(f"✅ Конкурс создан (ID: {contest_id})", "green")

    if logo_path_1:
        local_path_1 = os.path.join(UPLOADS_DIR, os.path.basename(logo_path_1))
        if wait_for_file(local_path_1):
            size = os.path.getsize(local_path_1) / 1024
            log(f"✅ Файл сохранён: {os.path.basename(logo_path_1)} ({size:.1f} KB)", "green")

        url = f"http://localhost:5000/uploads/{logo_path_1}"
        if requests.get(url).status_code == 200:
            log(f"✅ Файл доступен по URL", "green")
        else:
            log(f"⚠️ Файл недоступен по URL (проверьте nginx или порт)", "yellow")

    # =============================================================================
    # 🔄 ТЕСТ 2: Обновление с заменой логотипа
    # =============================================================================
    log("\n🔄 ТЕСТ 2: Обновление конкурса...", "cyan")
    old_local = os.path.join(UPLOADS_DIR, os.path.basename(logo_path_1)) if logo_path_1 else None

    with open(IMAGE_PATH_V2, "rb") as f:
        files = {"logo": ("test_v2.jpg", f, "image/jpeg")}
        data = {"name": "Обновлённый тест"}
        update_resp = requests.put(f"{BASE_URL}/contests/{contest_id}", headers=headers, data=data, files=files)

    if update_resp.status_code != 200:
        log(f"❌ Ошибка обновления: {update_resp.text}", "red")
        return False

    logo_path_2 = update_resp.json()["contest"].get("logo_path")
    log(f"✅ Конкурс обновлён. Новый файл: {os.path.basename(logo_path_2)}", "green")

    if old_local and logo_path_1 != logo_path_2:
        if not os.path.exists(old_local):
            log(f"✅ Старый логотип успешно удалён с диска", "green")
        else:
            log(f"⚠️ Старый логотип остался на диске", "yellow")

    # =============================================================================
    # 🗑️ ТЕСТ 3: Удаление конкурса
    # =============================================================================
    log("\n🗑️ ТЕСТ 3: Удаление конкурса...", "cyan")
    del_resp = requests.delete(f"{BASE_URL}/contests/{contest_id}", headers=headers)
    if del_resp.status_code != 200:
        log(f"❌ Ошибка удаления: {del_resp.text}", "red")
        return False
    log(f"✅ Конкурс удалён", "green")

    final_path = os.path.join(UPLOADS_DIR, os.path.basename(logo_path_2)) if logo_path_2 else None
    if final_path and not os.path.exists(final_path):
        log(f"✅ Логотип конкурса очищен с диска", "green")

    # Очистка временных файлов
    if os.path.exists(IMAGE_PATH_V2): os.remove(IMAGE_PATH_V2)
    log("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!", "green")
    return True


if __name__ == "__main__":
    try:
        success = test_upload_flow()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        log("\n⚠️ Тест прерван", "yellow")
    except Exception as e:
        log(f"\n❌ Ошибка: {e}", "red")
        import traceback;

        traceback.print_exc()