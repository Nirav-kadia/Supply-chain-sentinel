# Docker Testing Guide

## Quick Fix for 503 Error

The issue is that `uvicorn` is not found in the container. Here are the steps to fix it:

### Option 1: Use PowerShell Script (Recommended)
```powershell
.\test_docker.ps1
```

### Option 2: Manual Commands

1. **Build the simple Docker image:**
```bash
cd Backend
docker build -f Dockerfile.simple -t supplychain-test .
```

2. **Run the container:**
```bash
docker run -d --name supplychain-test-container -p 8000:8000 supplychain-test
```

3. **Test the API:**
```bash
curl http://localhost:8000/
```
Or open http://localhost:8000/ in your browser

4. **Check logs if it fails:**
```bash
docker logs supplychain-test-container
```

5. **Clean up:**
```bash
docker stop supplychain-test-container
docker rm supplychain-test-container
```

### Option 3: Direct Deploy Fix

If local testing works, push the changes:

```bash
git add .
git commit -m "Fix uvicorn path issue in Docker"
git push
```

This will trigger GitHub Actions to build and deploy the fixed container.

### What the Fix Does:

1. **Uses `python -m uvicorn`** instead of just `uvicorn` - this ensures Python can find the module
2. **Installs essential packages first** - FastAPI, uvicorn, pydantic
3. **Creates stub files** for missing modules to prevent import errors
4. **Simplified dependencies** to avoid conflicts

### Expected Result:

- Local test should return: `{"status": "running", "service": "SupplyChain Sentinel API"}`
- ECS service should become healthy
- ALB should return 200 instead of 503

### Troubleshooting:

If you still get errors:
1. Check the container logs: `docker logs supplychain-test-container`
2. Make sure Docker is running
3. Make sure port 8000 is not in use: `netstat -an | findstr :8000`