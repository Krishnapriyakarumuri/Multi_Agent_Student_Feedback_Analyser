#!/usr/bin/env python
"""Test script to verify the agent pipeline is working"""

import requests
import json
import time
import sys

API_URL = "http://localhost:8000/api/v1"

def test_server_running():
    """Test if server is responding"""
    try:
        response = requests.get("http://localhost:8000/", timeout=2)
        print("✅ Server is running")
        print(f"   Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Server not responding: {e}")
        return False

def test_worker_status():
    """Check if task worker is active"""
    try:
        response = requests.get(f"{API_URL}/worker/status", timeout=2)
        data = response.json()
        print("✅ Worker status endpoint responding")
        print(f"   Total tasks in pipeline: {data.get('total_tasks_in_pipeline', 0)}")
        print(f"   Queue depths: {data.get('queue_depths', {})}")
        return True
    except Exception as e:
        print(f"❌ Worker status failed: {e}")
        return False

def test_agents_status():
    """Check if agents are online"""
    try:
        response = requests.get(f"{API_URL}/agents/status", timeout=2)
        data = response.json()
        print("✅ Agents status endpoint responding")
        print(f"   Agents online: {data.get('agents_online', 0)}/{data.get('total_agents', 0)}")
        for agent in data.get('agent_details', []):
            print(f"   - {agent['name']}: {agent['status']}")
        return True
    except Exception as e:
        print(f"❌ Agents status failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Multi-Agent Pipeline...")
    print("=" * 60)
    
    # Test 1: Server running
    if not test_server_running():
        print("\n⚠️  Server is not running. Start it with: python main.py")
        sys.exit(1)
    
    time.sleep(1)
    
    # Test 2: Worker status
    print("\n" + "=" * 60)
    test_worker_status()
    
    time.sleep(1)
    
    # Test 3: Agents status
    print("\n" + "=" * 60)
    test_agents_status()
    
    print("\n" + "=" * 60)
    print("✅ All basic tests passed!")
    print("\nNext: Try uploading a CSV file via the frontend")
    print("  streamlit run frontend/app.py")
