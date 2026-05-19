$ErrorActionPreference = "Stop"

Write-Host "Python:"
python --version

Write-Host "Docker:"
docker --version

Write-Host "Docker Compose config:"
docker compose -f docker/docker-compose.yml config | Out-Null
Write-Host "OK"
