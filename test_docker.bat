@echo off
echo === Testing Docker Container ===

cd Backend

echo.
echo === Building Docker Image ===
docker build -f Dockerfile.simple -t supplychain-test .
if %ERRORLEVEL% neq 0 (
    echo ❌ Docker build failed!
    pause
    exit /b 1
)

echo.
echo === Stopping any existing container ===
docker stop supplychain-test-container 2>nul
docker rm supplychain-test-container 2>nul

echo.
echo === Starting Container ===
docker run -d --name supplychain-test-container -p 8000:8000 supplychain-test
if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to start container!
    pause
    exit /b 1
)

echo.
echo === Waiting for container to start ===
timeout /t 10 /nobreak

echo.
echo === Testing API ===
curl -f http://localhost:8000/
if %ERRORLEVEL% equ 0 (
    echo.
    echo ✅ Container is working!
) else (
    echo.
    echo ❌ API test failed, checking logs...
    echo.
    echo === Container Logs ===
    docker logs supplychain-test-container
)

echo.
echo === Cleaning up ===
docker stop supplychain-test-container
docker rm supplychain-test-container

echo.
echo Test completed!
pause