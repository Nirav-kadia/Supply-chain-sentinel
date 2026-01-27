#!/usr/bin/env python3
"""
Test script to build and run the container locally
"""
import subprocess
import time
import sys
import json

def run_command(cmd, cwd=None):
    """Run a command and return the result"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False, result.stderr
    print(f"Success: {result.stdout}")
    return True, result.stdout

def test_container():
    """Test the container locally"""
    backend_dir = "Backend"
    
    print("=== Building Docker Image ===")
    success, output = run_command("docker build -f Dockerfile.simple -t supplychain-test .", backend_dir)
    if not success:
        print("❌ Docker build failed!")
        return False
    
    print("\n=== Starting Container ===")
    # Stop any existing container
    subprocess.run("docker stop supplychain-test-container", shell=True, capture_output=True)
    subprocess.run("docker rm supplychain-test-container", shell=True, capture_output=True)
    
    # Start new container
    cmd = "docker run -d --name supplychain-test-container -p 8000:8000 supplychain-test"
    success, output = run_command(cmd)
    if not success:
        print("❌ Failed to start container!")
        return False
    
    print("\n=== Waiting for container to start ===")
    time.sleep(10)
    
    print("\n=== Testing API with curl ===")
    # Use curl instead of requests
    success, output = run_command("curl -f http://localhost:8000/ || echo 'CURL_FAILED'")
    
    if success and "CURL_FAILED" not in output:
        print("✅ Container is working!")
        print(f"API Response: {output}")
        return True
    else:
        print("❌ API test failed")
        
        # Get container logs
        print("\n=== Container Logs ===")
        result = subprocess.run("docker logs supplychain-test-container", 
                              shell=True, capture_output=True, text=True)
        print("STDOUT:", result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return False
    
    finally:
        # Cleanup
        print("\n=== Cleaning up ===")
        subprocess.run("docker stop supplychain-test-container", shell=True, capture_output=True)
        subprocess.run("docker rm supplychain-test-container", shell=True, capture_output=True)

if __name__ == "__main__":
    success = test_container()
    sys.exit(0 if success else 1)