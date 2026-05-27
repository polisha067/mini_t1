$ErrorActionPreference = "Stop"

$SSH_KEY = "C:\mini_t1\ssh\ssh-key-1779860741794"
$SERVER_IP = "103.76.54.43"
$USER = "minions"
$REMOTE_DIR = "~/mini_t1_prod"

Write-Host " Начинаем автоматический деплой проекта mini_t1..." -ForegroundColor Cyan

Write-Host "1/3 Упаковка файлов в архив..." -ForegroundColor Yellow
tar.exe -czf project.tar.gz --exclude=.git --exclude=contest-app/node_modules --exclude=contest-app/.angular --exclude=venv --exclude=__pycache__ --exclude=project.tar.gz .

Write-Host "2/3 Отправка архива на сервер $SERVER_IP..." -ForegroundColor Yellow
scp -i $SSH_KEY -o StrictHostKeyChecking=no project.tar.gz ${USER}@${SERVER_IP}:${REMOTE_DIR}/

Write-Host "3/3 Сборка и перезапуск контейнеров на сервере..." -ForegroundColor Yellow
ssh -i $SSH_KEY -o StrictHostKeyChecking=no ${USER}@${SERVER_IP} 'cd ~/mini_t1_prod ; tar -xzf project.tar.gz ; sudo docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --build'

Write-Host "Деплой успешно завершен!" -ForegroundColor Green
Write-Host "сайт доступен по адресу: http://$SERVER_IP" -ForegroundColor Green

# Удаляем временный архив локально, чтобы не засорять папку
Remove-Item project.tar.gz -Force
