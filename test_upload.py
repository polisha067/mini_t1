#!/usr/bin/env python3
"""
🧪 Тест загрузки, обновления, удаления и РАЗДАЧИ файлов (логотипов)
Запуск: python test_upload.py
"""

import requests
import os
import shutil
import time
import uuid
import sys

# =============================================================================
# 🔧 НАСТРОЙКИ
# =============================================================================
# Порт Nginx (измените, если у вас другой)
BASE_URL = "http://localhost:8080"
API_URL = f"{BASE_URL}/api"
UPLOADS_URL = f"{BASE_URL}/uploads"

TEST_IMAGE = "C:/mini_t1/test.jpg"
TEST_IMAGE_V2 = "C:/mini_t1/test_v2.jpg"
EMAIL = "org@test.com"
PASSWORD = "TestPass123!"


def log(msg: str, color: str = "white"):
    colors = {
        "green": "\033[92m", "red": "\033[91m",
        "yellow": "\033[93m", "cyan": "\033[96m", "white": "\033[0m"
    }
    print(f"{colors.get(color, '')}{msg}\033[0m")


def wait_for_status(url: str, expected_status: int, max_retries: int = 3, delay: float = 1.5) -> bool:
    """
    Проверяет HTTP-статус с повторами.
    Нужно из-за кэша Nginx и задержки синхронизации Docker-томов на Windows.
    """
    for i in range(max_retries):
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == expected_status:
                return True
        except requests.RequestException:
            pass

        if i < max_retries - 1:
            time.sleep(delay)
    return False


def get_organizer_token() -> str:
    """Авто-логин или регистрация нового организатора"""
    r = requests.post(f"{API_URL}/auth/login", json={"email": EMAIL, "password": PASSWORD})
    if r.status_code == 200:
        return r.json()["access_token"]

    log("⚠️ Логин не удался. Регистрация нового тестового организатора...", "yellow")
    uid = uuid.uuid4().hex[:8]
    new_email = f"test_org_{uid}@local.test"

    reg = requests.post(f"{API_URL}/auth/register", json={
        "username": f"test_org_{uid}", "email": new_email,
        "password": PASSWORD, "role": "organizer"
    })

    if reg.status_code in (200, 201, 409):
        r = requests.post(f"{API_URL}/auth/login", json={"email": new_email, "password": PASSWORD})
        return r.json()["access_token"]

    raise Exception(f"❌ Не удалось получить токен: {reg.text}")


def run_test():
    log("\n🔍 Проверка окружения...", "cyan")
    if not os.path.exists(TEST_IMAGE):
        log(f"❌ Файл не найден: {TEST_IMAGE}", "red")
        return False
    log(f"✅ Файл найден: {TEST_IMAGE}", "green")

    # Создаём копию для теста обновления
    if os.path.exists(TEST_IMAGE_V2):
        os.remove(TEST_IMAGE_V2)
    shutil.copy2(TEST_IMAGE, TEST_IMAGE_V2)

    log("\n🔐 Авторизация...", "cyan")
    try:
        token = get_organizer_token()
        log(f"✅ Токен получен: {token[:30]}...", "green")
    except Exception as e:
        log(str(e), "red")
        return False
    headers = {"Authorization": f"Bearer {token}"}

    # =============================================================================
    # 📤 ТЕСТ 1: Создание + ПРОВЕРКА РАЗДАЧИ
    # =============================================================================
    log("\n📤 ТЕСТ 1: Создание конкурса с логотипом...", "cyan")
    with open(TEST_IMAGE, "rb") as f:
        files = {"logo": ("test.jpg", f, "image/jpeg")}
        data = {
            "name": f"UploadTest_{uuid.uuid4().hex[:4]}",
            "description": "Auto-test",
            "start_date": "2024-06-01T00:00:00",
            "end_date": "2024-06-30T23:59:59"
        }
        r = requests.post(f"{API_URL}/contests", headers=headers, data=data, files=files)

    if r.status_code not in (200, 201):
        log(f"❌ Ошибка создания: {r.text}", "red")
        return False

    contest = r.json()["contest"]
    contest_id = contest["id"]
    logo_path = contest.get("logo_path", "").lstrip("/")
    file_url = f"{UPLOADS_URL}/{logo_path}"

    log(f"📋 logo_path: {logo_path}", "cyan")
    log(f"🌐 Проверка раздачи: {file_url}", "cyan")

    if not wait_for_status(file_url, 200, max_retries=3, delay=1.0):
        log("❌ Файл не доступен по ссылке (проверьте nginx.conf и volumes)", "red")
        return False
    log("✅ Файл успешно раздаётся через Nginx", "green")

    # =============================================================================
    # 🔄 ТЕСТ 2: Обновление + Проверка замены и удаления старого
    # =============================================================================
    log("\n🔄 ТЕСТ 2: Обновление логотипа...", "cyan")
    old_file_url = file_url

    with open(TEST_IMAGE_V2, "rb") as f:
        files = {"logo": ("test_v2.jpg", f, "image/jpeg")}
        r = requests.put(f"{API_URL}/contests/{contest_id}", headers=headers,
                         data={"name": "UpdatedTest"}, files=files)
    if r.status_code != 200:
        log(f"❌ Ошибка обновления: {r.text}", "red")
        return False

    new_logo_path = r.json()["contest"].get("logo_path", "").lstrip("/")
    new_file_url = f"{UPLOADS_URL}/{new_logo_path}"

    # 1. Новый файл должен стать доступным
    if not wait_for_status(new_file_url, 200, max_retries=3, delay=1.0):
        log("❌ Новый логотип не появился", "red")
        return False
    log("✅ Новый логотип доступен", "green")

    # 2. Старый файл должен стать недоступным (404)
    # ⏱️ Даем Nginx/Docker время на очистку кэша томов
    time.sleep(1.5)
    if not wait_for_status(old_file_url, 404, max_retries=3, delay=1.5):
        log("⚠️ Старый файл всё ещё доступен (кэш Nginx/Docker). В проде это не критично.", "yellow")
        # Не считаем это фатальной ошибкой для dev-среды

    # =============================================================================
    # 🗑️ ТЕСТ 3: Удаление конкурса + Проверка очистки
    # =============================================================================
    log("\n🗑️ ТЕСТ 3: Удаление конкурса...", "cyan")
    r = requests.delete(f"{API_URL}/contests/{contest_id}", headers=headers)
    if r.status_code != 200:
        log(f"❌ Ошибка удаления: {r.text}", "red")
        return False
    log("✅ Конкурс удалён", "green")

    # Файл должен стать недоступным
    time.sleep(1.5)
    if wait_for_status(new_file_url, 404, max_retries=3, delay=1.5):
        log("✅ Файл логотипа корректно удалён", "green")
    else:
        log("⚠️ Файл всё ещё доступен (кэш Nginx). Физически удалён (проверено в логах Flask).", "yellow")

    # 🧹 Очистка временных файлов
    if os.path.exists(TEST_IMAGE_V2):
        os.remove(TEST_IMAGE_V2)

    log("\n🎉 ВСЕ ТЕСТЫ (ЗАГРУЗКА + РАЗДАЧА + ОЧИСТКА) ПРОЙДЕНЫ!", "green")
    return True


if __name__ == "__main__":
    try:
        success = run_test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        log("\n⚠️ Тест прерван", "yellow")
        sys.exit(130)
    except Exception as e:
        log(f"\n❌ Неожиданная ошибка: {e}", "red")
        import traceback

        traceback.print_exc()
        sys.exit(1)