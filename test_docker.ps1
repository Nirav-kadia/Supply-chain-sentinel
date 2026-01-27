Write-Host "=== Testing Docker Container ===" -ForegroundColor Green

Set-Location Backend

Write-Host "`n=== Building Docker Image ===" -ForegroundColor Yellow
docker build -f Dockerfile.simple -t supplychain-test .
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker build failed!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "`n=== Stopping any existing container ===" -ForegroundColor Yellow
docker stop supplychain-test-container 2>$null
docker rm supplychain-test-container 2>$null

Write-Host "`n=== Starting Container on port 8001 ===" -ForegroundColor Yellow
docker run -d --name supplychain-test-container -p 8001:8000 supplychain-test
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to start container!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "`n=== Waiting for container to start ===" -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host "`n=== Testing API ===" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8001/" -TimeoutSec 10
    Write-Host "✅ Container is working!" -ForegroundColor Green
    Write-Host "Status Code: $($response.StatusCode)" -ForegroundColor Cyan
    Write-Host "Response: $($response.Content)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ API test failed: $($_.Exception.Message)" -ForegroundColor Red
    
    Write-Host "`n=== Container Logs ===" -ForegroundColor Yellow
    docker logs supplychain-test-container
}

Write-Host "`n=== Cleaning up ===" -ForegroundColor Yellow
docker stop supplychain-test-container
docker rm supplychain-test-container

Write-Host "`nTest completed!" -ForegroundColor Green
Read-Host "Press Enter to exit"