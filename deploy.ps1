$ErrorActionPreference = "Stop"

$SSH_KEY = "C:\mini_t1\ssh\ssh-key-1779860741794"
$SERVER_IP = "103.76.54.43"
$USER = "minions"
$REMOTE_DIR = "~/mini_t1_prod"

Write-Host "Deploying mini_t1..." -ForegroundColor Cyan

Write-Host "1/3 Packaging files..." -ForegroundColor Yellow
cmd.exe /c "tar -czf project.tar.gz --exclude=.git --exclude=contest-app/node_modules --exclude=contest-app/.angular --exclude=venv --exclude=__pycache__ --exclude=project.tar.gz ."
if ($LASTEXITCODE -ne 0) { throw "Error creating tar archive" }

Write-Host "2/3 Uploading to server..." -ForegroundColor Yellow
cmd.exe /c "scp -i $SSH_KEY -o StrictHostKeyChecking=no project.tar.gz ${USER}@${SERVER_IP}:${REMOTE_DIR}/"
if ($LASTEXITCODE -ne 0) { throw "Error uploading via scp" }

Write-Host "3/3 Building and restarting containers..." -ForegroundColor Yellow
$RemoteCmd = "cd ~/mini_t1_prod ; tar -xzf project.tar.gz ; sudo docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --build"
cmd.exe /c "ssh -i $SSH_KEY -o StrictHostKeyChecking=no ${USER}@${SERVER_IP} ""$RemoteCmd"""
if ($LASTEXITCODE -ne 0) { throw "Error running ssh/docker-compose" }

Write-Host "Deploy success! http://$SERVER_IP" -ForegroundColor Green

if (Test-Path project.tar.gz) {
    Remove-Item project.tar.gz -Force
}
