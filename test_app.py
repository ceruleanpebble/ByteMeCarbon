"""Test the Flask app endpoint directly."""

import json
import sys
sys.path.insert(0, '.')

from app import app

# Create test client
client = app.test_client()

# Create a test Python file
test_code = """import os
import sys

def unused():
    pass

if True:
    x = 2 + 3

print(x)
"""

print("=" * 60)
print("TESTING FLASK APP ENDPOINT")
print("=" * 60)

# Test 1: GET root
print("\n1. Testing GET /")
response = client.get('/')
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    print("   ✓ HTML page loads")
else:
    print(f"   ✗ Failed: {response.status_code}")

# Test 2: POST upload with valid Python
print("\n2. Testing POST /upload with valid Python code")
data = {
    'file': (open(__file__).read()[:100].encode(), 'test.py')
}
try:
    from io import BytesIO
    data = {
        'file': (BytesIO(test_code.encode('utf-8')), 'test.py')
    }
    response = client.post('/upload', data=data, content_type='multipart/form-data')
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.get_json()
        print("   ✓ Response received")
        
        # Check response structure
        if 'original' in result and 'optimized' in result and 'report' in result:
            print("   ✓ Response structure valid")
            
            # Check report structure
            report = result['report']
            if all(k in report for k in ['complexity', 'performance', 'energy', 'real_world_impact']):
                print("   ✓ Report structure valid")
                print(f"\n   Original code ({len(result['original'])} chars)")
                print(f"   Optimized code ({len(result['optimized'])} chars)")
                print(f"\n   Optimization Results:")
                print(f"     Complexity: {report['complexity']['before']} → {report['complexity']['after']}")
                print(f"     Performance: {report['performance']['status']}")
                print(f"     Energy: {report['energy']['status']}")
                
                impact = report['real_world_impact']
                if 'per_run' in impact:
                    print(f"     Impact: {impact['per_run']['co2_saved']}")
                elif 'message' in impact:
                    print(f"     Impact: {impact['message']}")
            else:
                print("   ✗ Report structure invalid")
                print(f"   Keys: {list(report.keys())}")
        else:
            print("   ✗ Response structure invalid")
            print(f"   Keys: {list(result.keys())}")
    else:
        print(f"   ✗ Failed with status {response.status_code}")
        print(f"   Error: {response.get_json()}")
        
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Invalid Python
print("\n3. Testing POST /upload with invalid Python")
try:
    data = {
        'file': (BytesIO(b'x = '), 'invalid.py')
    }
    response = client.post('/upload', data=data, content_type='multipart/form-data')
    print(f"   Status: {response.status_code}")
    if response.status_code in [400, 422]:
        result = response.get_json()
        if 'error' in result:
            print(f"   ✓ Error handled: {result['error']}")
        else:
            print(f"   ✗ No error message")
    else:
        print(f"   ✗ Should reject invalid code")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "=" * 60)
print("✓ FLASK APP TEST COMPLETE")
print("=" * 60)
