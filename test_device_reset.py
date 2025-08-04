#!/usr/bin/env python3
"""
Test script untuk menguji implementasi Device ID dan Reset functionality
"""

import random
import requests
import json
import time

# Konfigurasi server
BASE_URL = "http://localhost:5000"
DEVICE_ID = "IOT_001"

def test_reset_device():
    """Test reset device endpoint"""
    print(f"🔄 Testing reset for device: {DEVICE_ID}")
    
    url = f"{BASE_URL}/reset/{DEVICE_ID}"
    response = requests.post(url)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_send_data():
    """Test sending data dari IoT device"""
    print(f"📡 Testing send data for device: {DEVICE_ID}")
    
    url = f"{BASE_URL}/recive"
    data = {
        "did": DEVICE_ID,
        "tb": random.uniform(60.0, 75.0),  # Simulasi tinggi badan
        "bb": random.uniform(30.0, 32.0)  # Simulasi berat badan
    }
    
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=data, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_get_device_data():
    """Test mendapatkan data device"""
    print(f"📊 Testing get device data: {DEVICE_ID}")
    
    url = f"{BASE_URL}/devices/{DEVICE_ID}"
    response = requests.get(url)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"Device Data: {response.json()}")
    else:
        print(f"Error: {response.text}")

def test_get_all_devices():
    """Test mendapatkan semua devices"""
    print("📋 Testing get all devices")
    
    url = f"{BASE_URL}/devices"
    response = requests.get(url)
    
    print(f"Status Code: {response.status_code}")
    print(f"All Devices: {response.json()}")

def test_websocket_status():
    """Test status WebSocket"""
    print("🌐 Testing WebSocket status")
    
    url = f"{BASE_URL}/ws/status"
    response = requests.get(url)
    
    print(f"Status Code: {response.status_code}")
    print(f"WebSocket Status: {response.json()}")

def run_full_test():
    """Menjalankan semua test secara berurutan"""
    print("🚀 Starting Device Reset & Data Flow Tests")
    print("=" * 50)
    
    # Test 1: Reset device
    print("\n1. Test Reset Device")
    reset_success = test_reset_device()
    time.sleep(1)
    
    # Test 2: Send data (simulasi IoT device)
    print("\n2. Test Send Data")
    if reset_success:
        send_success = test_send_data()
        time.sleep(1)
    else:
        print("❌ Skip send data karena reset gagal")
        send_success = False
    
    # Test 3: Get device data
    print("\n3. Test Get Device Data")
    test_get_device_data()
    time.sleep(1)
    
    # Test 4: Get all devices
    print("\n4. Test Get All Devices")
    test_get_all_devices()
    time.sleep(1)
    
    # Test 5: WebSocket status
    print("\n5. Test WebSocket Status")
    test_websocket_status()
    
    print("\n" + "=" * 50)
    print("✅ Test completed!")
    
    if reset_success and send_success:
        print("✅ All tests passed! Device reset and data flow working correctly.")
    else:
        print("❌ Some tests failed. Check server logs.")

if __name__ == "__main__":
    try:
        run_full_test()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to server. Make sure the server is running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Error: {e}")
