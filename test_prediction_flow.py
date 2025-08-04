#!/usr/bin/env python3
"""
Test script untuk menguji endpoint /predict dengan data IoT
Simulasi flow: Reset Device -> Send IoT Data -> Predict Stunting
"""

import requests
import json
import time
from datetime import datetime, timedelta

# Konfigurasi server
BASE_URL = "http://localhost:5000"
DEVICE_ID = "IOT_001"

def test_reset_device():
    """Reset device data"""
    print(f"🔄 Resetting device: {DEVICE_ID}")
    
    url = f"{BASE_URL}/reset/{DEVICE_ID}"
    response = requests.post(url)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_send_iot_data(tb=120.5, bb=25.3):
    """Send IoT data (simulate IoT device)"""
    print(f"📡 Sending IoT data: TB={tb}cm, BB={bb}kg")
    
    url = f"{BASE_URL}/recive"
    data = {
        "did": DEVICE_ID,
        "tb": tb,
        "bb": bb
    }
    
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=data, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_predict_stunting(child_data):
    """Test prediction endpoint"""
    print(f"🔮 Testing prediction for: {child_data['nama']}")
    
    url = f"{BASE_URL}/predict"
    headers = {"Content-Type": "application/json"}
    
    print(f"Request Data: {json.dumps(child_data, indent=2)}")
    
    response = requests.post(url, json=child_data, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Prediction successful!")
        print(f"Result: {json.dumps(result, indent=2)}")
        
        # Parse prediction result
        data = result.get('data', {})
        prediction_class = data.get('class', 'Unknown')
        confidence = data.get('confidence', 0)
        
        print(f"\n📊 PREDICTION SUMMARY:")
        print(f"Child Name: {child_data['nama']}")
        print(f"Prediction: {prediction_class}")
        print(f"Confidence: {confidence:.2%}")
        print(f"Current Weight: {child_data['berat']} kg")
        print(f"Current Height: {child_data['tinggi']} cm")
        
        return True
    else:
        print(f"❌ Prediction failed: {response.text}")
        return False

def run_complete_flow_test():
    """Run complete flow test: Reset -> IoT Data -> Predict"""
    print("🚀 Starting Complete ML Stunting Flow Test")
    print("=" * 60)
    
    # Test Data
    test_cases = [
        {
            "nama": "Ahmad Budi",
            "tanggal_lahir": "2021-05-15",
            "jenis_kelamin": "L",
            "bb_lahir": 3.2,
            "tb_lahir": 50.0,
            "iot_tb": 95.5,  # Height from IoT
            "iot_bb": 15.2   # Weight from IoT
        },
        {
            "nama": "Siti Aisyah", 
            "tanggal_lahir": "2020-12-10",
            "jenis_kelamin": "P",
            "bb_lahir": 3.0,
            "tb_lahir": 48.5,
            "iot_tb": 105.3,
            "iot_bb": 18.7
        },
        {
            "nama": "Bayu Saputra",
            "tanggal_lahir": "2022-03-22",
            "jenis_kelamin": "L", 
            "bb_lahir": 2.8,
            "tb_lahir": 47.0,
            "iot_tb": 82.1,  # Potentially stunted case
            "iot_bb": 11.5
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 TEST CASE {i}: {test_case['nama']}")
        print("-" * 40)
        
        # Step 1: Reset device
        print("Step 1: Reset Device")
        reset_success = test_reset_device()
        time.sleep(1)
        
        if not reset_success:
            print("❌ Reset failed, skipping this test case")
            continue
        
        # Step 2: Send IoT data
        print("\nStep 2: Send IoT Data")
        iot_success = test_send_iot_data(
            tb=test_case['iot_tb'], 
            bb=test_case['iot_bb']
        )
        time.sleep(1)
        
        if not iot_success:
            print("❌ IoT data send failed, skipping prediction")
            continue
        
        # Step 3: Predict
        print("\nStep 3: Predict Stunting")
        predict_data = {
            "nama": test_case['nama'],
            "tanggal_lahir": test_case['tanggal_lahir'],
            "jenis_kelamin": test_case['jenis_kelamin'],
            "bb_lahir": test_case['bb_lahir'],
            "tb_lahir": test_case['tb_lahir'],
            "berat": test_case['iot_bb'],  # From IoT
            "tinggi": test_case['iot_tb']  # From IoT
        }
        
        predict_success = test_predict_stunting(predict_data)
        
        if predict_success:
            print("✅ Test case completed successfully!")
        else:
            print("❌ Test case failed at prediction step")
        
        print("\n" + "="*60)
        time.sleep(2)  # Wait between test cases

def test_edge_cases():
    """Test edge cases and error handling"""
    print("\n🔍 Testing Edge Cases")
    print("=" * 40)
    
    # Test 1: Invalid data
    print("Test 1: Invalid birth date")
    invalid_data = {
        "nama": "Test Child",
        "tanggal_lahir": "invalid-date",
        "jenis_kelamin": "L",
        "bb_lahir": 3.0,
        "tb_lahir": 50.0,
        "berat": 15.0,
        "tinggi": 95.0
    }
    test_predict_stunting(invalid_data)
    
    time.sleep(1)
    
    # Test 2: Missing required fields
    print("\nTest 2: Missing required fields")
    incomplete_data = {
        "nama": "Test Child",
        "jenis_kelamin": "P"
        # Missing other required fields
    }
    test_predict_stunting(incomplete_data)
    
    time.sleep(1)
    
    # Test 3: Invalid gender
    print("\nTest 3: Invalid gender")
    invalid_gender_data = {
        "nama": "Test Child",
        "tanggal_lahir": "2022-01-01",
        "jenis_kelamin": "X",  # Invalid gender
        "bb_lahir": 3.0,
        "tb_lahir": 50.0,
        "berat": 15.0,
        "tinggi": 95.0
    }
    test_predict_stunting(invalid_gender_data)

if __name__ == "__main__":
    try:
        # Run complete flow test
        run_complete_flow_test()
        
        # Run edge case tests
        test_edge_cases()
        
        print("\n🎉 All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to server.")
        print("Make sure the server is running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Error: {e}")
