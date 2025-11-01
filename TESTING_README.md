# BlockIAM Testing Guide

Complete guide to test each function individually and integrate BlockIAM into your codebase.

---

## 🚀 Quick Setup

### 1. Install BlockIAM
```bash
cd "c:\Projects\New folder"
pip install -e .
```

### 2. Configure Environment
Create `.env` file:
```env
RPC_URL=http://127.0.0.1:7545
PRIVATE_KEY=your_ganache_private_key_here
CONTRACT_ADDRESS=your_deployed_contract_address
CHAIN_ID=1337
```

### 3. Start Ganache
Make sure Ganache is running on `http://127.0.0.1:7545`

---

## 📋 Test Each Function

### Test 1: Initialize Client

**Purpose:** Verify connection to blockchain and contract

```python
# test_1_initialize.py
from blockiam import IAMClient

try:
    client = IAMClient()
    print("✓ Client initialized successfully")
    print(f"  Chain ID: {client.config.chain_id}")
    print(f"  Account: {client.account.address}")
    print(f"  Contract: {client.config.contract_address}")
    client.close()
except Exception as e:
    print(f"✗ Error: {e}")
```

**Run:**
```bash
python test_1_initialize.py
```

**Expected Output:**
```
✓ Client initialized successfully
  Chain ID: 1337
  Account: 0x...
  Contract: 0x...
```

---

### Test 2: Register Device

**Purpose:** Register a new IoT device on blockchain

```python
# test_2_register.py
from blockiam import IAMClient

client = IAMClient()

# Use a Ganache address or generate one
device_address = "0x1234567890123456789012345678901234567890"

result = client.register_device(
    address=device_address,
    name="Test Device 1",
    role="sensor",
    metadata="Test metadata"
)

print(f"Status: {result['status']}")
if result['status'] == 'success':
    print(f"✓ Device registered")
    print(f"  Transaction: {result['tx_hash']}")
    print(f"  Gas used: {result['gas_used']}")
else:
    print(f"✗ Error: {result.get('message')}")

client.close()
```

**Run:**
```bash
python test_2_register.py
```

**Expected Output:**
```
Status: success
✓ Device registered
  Transaction: 0x123...
  Gas used: 12345
```

---

### Test 3: Grant Access

**Purpose:** Grant access permission to a device

```python
# test_3_grant_access.py
from blockiam import IAMClient

client = IAMClient()

device_address = "0x1234567890123456789012345678901234567890"

# Grant permanent access (expiry=0)
result = client.grant_access(device_address, expiry=0)

print(f"Status: {result['status']}")
if result['status'] == 'success':
    print(f"✓ Access granted")
    print(f"  Transaction: {result['tx_hash']}")
else:
    print(f"✗ Error: {result.get('message')}")

client.close()
```

**Run:**
```bash
python test_3_grant_access.py
```

---

### Test 4: Check Access

**Purpose:** Verify if a device has access

```python
# test_4_check_access.py
from blockiam import IAMClient

client = IAMClient()

device_address = "0x1234567890123456789012345678901234567890"

result = client.check_access(device_address)

print(f"Status: {result['status']}")
if result['status'] == 'success':
    has_access = result['has_access']
    print(f"Has Access: {has_access}")
    if has_access:
        print("✓ Device has access")
    else:
        print("✗ Device does not have access")
else:
    print(f"✗ Error: {result.get('message')}")

client.close()
```

**Run:**
```bash
python test_4_check_access.py
```

---

### Test 5: Revoke Access

**Purpose:** Revoke access from a device

```python
# test_5_revoke_access.py
from blockiam import IAMClient

client = IAMClient()

device_address = "0x1234567890123456789012345678901234567890"

result = client.revoke_access(device_address)

print(f"Status: {result['status']}")
if result['status'] == 'success':
    print(f"✓ Access revoked")
    print(f"  Transaction: {result['tx_hash']}")
else:
    print(f"✗ Error: {result.get('message')}")

client.close()
```

**Run:**
```bash
python test_5_revoke_access.py
```

---

### Test 6: Assign Role

**Purpose:** Change device role

```python
# test_6_assign_role.py
from blockiam import IAMClient

client = IAMClient()

device_address = "0x1234567890123456789012345678901234567890"

result = client.assign_role(device_address, "actuator")

print(f"Status: {result['status']}")
if result['status'] == 'success':
    print(f"✓ Role assigned")
    print(f"  Transaction: {result['tx_hash']}")
else:
    print(f"✗ Error: {result.get('message')}")

client.close()
```

**Run:**
```bash
python test_6_assign_role.py
```

---

### Test 7: Log Access Event

**Purpose:** Log an access event to blockchain

```python
# test_7_log_access.py
from blockiam import IAMClient

client = IAMClient()

result = client.log_access("Temperature sensor reading at 23.5°C")

print(f"Status: {result['status']}")
if result['status'] == 'success':
    print(f"✓ Access logged")
    print(f"  Transaction: {result['tx_hash']}")
else:
    print(f"✗ Error: {result.get('message')}")

client.close()
```

**Run:**
```bash
python test_7_log_access.py
```

---

### Test 8: Get Device Info

**Purpose:** Retrieve device information from blockchain

```python
# test_8_get_device_info.py
from blockiam import IAMClient
from datetime import datetime

client = IAMClient()

device_address = "0x1234567890123456789012345678901234567890"

result = client.get_device_info(device_address)

print(f"Status: {result['status']}")
if result['status'] == 'success':
    data = result['data']
    print("✓ Device Information:")
    print(f"  Address: {data['address']}")
    print(f"  Name: {data['name']}")
    print(f"  Role: {data['role']}")
    print(f"  Metadata: {data['metadata']}")
    print(f"  Registered At: {datetime.fromtimestamp(data['registered_at'])}")
    print(f"  Is Registered: {data['is_registered']}")
else:
    print(f"✗ Error: {result.get('message')}")

client.close()
```

**Run:**
```bash
python test_8_get_device_info.py
```

---

### Test 9: Get Blockchain Logs

**Purpose:** Fetch access logs from blockchain

```python
# test_9_get_logs.py
from blockiam import IAMClient
from datetime import datetime

client = IAMClient()

# Get all logs from genesis block
result = client.get_logs(from_block=0, to_block='latest')

print(f"Status: {result['status']}")
if result['status'] == 'success':
    print(f"✓ Found {result['count']} log entries")
    
    if result['count'] > 0:
        print("\nRecent logs:")
        for i, log in enumerate(result['data'][:5], 1):
            print(f"\n  {i}. Device: {log['device'][:10]}...")
            print(f"     Reason: {log['reason']}")
            print(f"     Success: {log['success']}")
            print(f"     Time: {datetime.fromtimestamp(log['timestamp'])}")
            print(f"     TX: {log['tx_hash'][:10]}...")
else:
    print(f"✗ Error: {result.get('message')}")

client.close()
```

**Run:**
```bash
python test_9_get_logs.py
```

---

### Test 10: Sync to Cache

**Purpose:** Sync blockchain data to local SQLite cache

```python
# test_10_sync_cache.py
from blockiam import IAMClient

client = IAMClient()

print("Syncing blockchain data to local cache...")
result = client.sync_cache()

print(f"Status: {result['status']}")
if result['status'] == 'success':
    print("✓ Cache synced successfully")
else:
    print(f"✗ Error: {result.get('message')}")

client.close()
```

**Run:**
```bash
python test_10_sync_cache.py
```

---

### Test 11: Get Cached Logs

**Purpose:** Retrieve logs from local cache (faster, works offline)

```python
# test_11_get_cached_logs.py
from blockiam import IAMClient
from datetime import datetime

client = IAMClient()

result = client.get_cached_logs(limit=10)

print(f"Status: {result['status']}")
if result['status'] == 'success':
    logs = result['data']
    print(f"✓ Retrieved {len(logs)} cached logs")
    
    if logs:
        print("\nCached logs:")
        for log in logs[:5]:
            print(f"\n  ID: {log['id']}")
            print(f"  Device: {log['device'][:10]}...")
            print(f"  Reason: {log['reason']}")
            print(f"  Time: {datetime.fromtimestamp(log['timestamp'])}")
else:
    print(f"✗ Error: {result.get('message')}")

client.close()
```

**Run:**
```bash
python test_11_get_cached_logs.py
```

---

## 🏗️ Integration into Your Codebase

### Example 1: Flask Web API

```python
# app.py - Flask REST API
from flask import Flask, request, jsonify
from blockiam import IAMClient

app = Flask(__name__)

# Initialize client once
client = IAMClient()

@app.route('/devices', methods=['POST'])
def register_device():
    """Register a new device"""
    data = request.json
    result = client.register_device(
        address=data['address'],
        name=data['name'],
        role=data['role'],
        metadata=data.get('metadata', '')
    )
    return jsonify(result)

@app.route('/devices/<address>/access', methods=['POST'])
def grant_access(address):
    """Grant access to device"""
    result = client.grant_access(address)
    return jsonify(result)

@app.route('/devices/<address>/access', methods=['GET'])
def check_access(address):
    """Check device access"""
    result = client.check_access(address)
    return jsonify(result)

@app.route('/devices/<address>', methods=['GET'])
def get_device(address):
    """Get device info"""
    result = client.get_device_info(address)
    return jsonify(result)

@app.route('/logs', methods=['GET'])
def get_logs():
    """Get access logs"""
    result = client.get_logs()
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

**Test API:**
```bash
# Register device
curl -X POST http://localhost:5000/devices -H "Content-Type: application/json" -d "{\"address\":\"0x123...\",\"name\":\"Device1\",\"role\":\"sensor\"}"

# Check access
curl http://localhost:5000/devices/0x123.../access

# Get logs
curl http://localhost:5000/logs
```

---

### Example 2: IoT Device Handler

```python
# iot_device_manager.py
from blockiam import IAMClient
from typing import Dict, Optional
import time

class IoTDeviceManager:
    """Manager for IoT devices with blockchain IAM"""
    
    def __init__(self):
        self.client = IAMClient()
        self.devices = {}
    
    def register_device(self, mac_address: str, name: str, role: str) -> bool:
        """Register IoT device"""
        # Generate device address from MAC
        device_address = self._mac_to_address(mac_address)
        
        result = self.client.register_device(
            address=device_address,
            name=name,
            role=role,
            metadata=f"MAC:{mac_address}"
        )
        
        if result['status'] == 'success':
            self.devices[mac_address] = {
                'address': device_address,
                'name': name,
                'role': role
            }
            return True
        return False
    
    def authorize_operation(self, mac_address: str, operation: str) -> bool:
        """Check if device is authorized for operation"""
        device = self.devices.get(mac_address)
        if not device:
            return False
        
        # Check access on blockchain
        result = self.client.check_access(device['address'])
        
        if result['status'] == 'success' and result['has_access']:
            # Log the operation
            self.client.log_access(f"{device['name']}: {operation}")
            return True
        
        return False
    
    def _mac_to_address(self, mac: str) -> str:
        """Convert MAC to Ethereum address"""
        import hashlib
        from web3 import Web3
        
        mac_clean = mac.replace(":", "").lower()
        hash_hex = hashlib.sha256(mac_clean.encode()).hexdigest()
        return Web3.to_checksum_address("0x" + hash_hex[:40])
    
    def close(self):
        """Cleanup"""
        self.client.close()

# Usage
if __name__ == "__main__":
    manager = IoTDeviceManager()
    
    # Register device
    manager.register_device("AA:BB:CC:DD:EE:FF", "Smart Lock", "actuator")
    
    # Authorize operation
    if manager.authorize_operation("AA:BB:CC:DD:EE:FF", "unlock door"):
        print("✓ Operation authorized and logged")
    else:
        print("✗ Operation denied")
    
    manager.close()
```

---

### Example 3: Background Task Processor

```python
# task_processor.py
from blockiam import IAMClient
import time
from datetime import datetime

class DeviceTaskProcessor:
    """Process tasks with blockchain verification"""
    
    def __init__(self):
        self.client = IAMClient()
    
    def process_task(self, device_address: str, task: dict):
        """Process a task with access verification"""
        print(f"[{datetime.now()}] Processing task for {device_address}")
        
        # Check access
        access = self.client.check_access(device_address)
        
        if access['status'] == 'success' and access['has_access']:
            print("  ✓ Access verified")
            
            # Execute task
            self._execute_task(task)
            
            # Log to blockchain
            self.client.log_access(f"Task executed: {task['type']}")
            print("  ✓ Task completed and logged")
        else:
            print("  ✗ Access denied - task rejected")
    
    def _execute_task(self, task: dict):
        """Execute the actual task"""
        # Your task logic here
        time.sleep(1)
        print(f"  → Executing: {task['type']}")
    
    def close(self):
        self.client.close()

# Usage
if __name__ == "__main__":
    processor = DeviceTaskProcessor()
    
    tasks = [
        {"type": "read_sensor", "sensor": "temperature"},
        {"type": "control_actuator", "action": "turn_on"},
    ]
    
    device_address = "0x1234567890123456789012345678901234567890"
    
    for task in tasks:
        processor.process_task(device_address, task)
        time.sleep(2)
    
    processor.close()
```

---

### Example 4: Context Manager Usage

```python
# context_usage.py
from blockiam import IAMClient

# Automatic cleanup with context manager
with IAMClient() as client:
    # Register device
    result = client.register_device(
        "0x123...", 
        "Device", 
        "sensor"
    )
    print(f"Registered: {result['status']}")
    
    # Grant access
    client.grant_access("0x123...")
    
    # Check access
    access = client.check_access("0x123...")
    print(f"Has access: {access['has_access']}")

# Client automatically closed here
```

---

### Example 5: Batch Operations

```python
# batch_operations.py
from blockiam import IAMClient

def batch_register_devices(devices: list):
    """Register multiple devices"""
    client = IAMClient()
    results = []
    
    for device in devices:
        result = client.register_device(
            address=device['address'],
            name=device['name'],
            role=device['role'],
            metadata=device.get('metadata', '')
        )
        results.append({
            'device': device['name'],
            'status': result['status'],
            'tx_hash': result.get('tx_hash')
        })
    
    client.close()
    return results

# Usage
devices = [
    {'address': '0x123...', 'name': 'Sensor-1', 'role': 'sensor'},
    {'address': '0x456...', 'name': 'Actuator-1', 'role': 'actuator'},
    {'address': '0x789...', 'name': 'Gateway-1', 'role': 'gateway'},
]

results = batch_register_devices(devices)
for r in results:
    print(f"{r['device']}: {r['status']}")
```

---

## 🧪 Run All Tests

Create a master test script:

```python
# run_all_tests.py
import subprocess
import sys

tests = [
    "test_1_initialize.py",
    "test_2_register.py",
    "test_3_grant_access.py",
    "test_4_check_access.py",
    "test_7_log_access.py",
    "test_8_get_device_info.py",
    "test_9_get_logs.py",
    "test_10_sync_cache.py",
]

print("=" * 60)
print("Running BlockIAM Test Suite")
print("=" * 60)

for i, test in enumerate(tests, 1):
    print(f"\n[{i}/{len(tests)}] Running {test}...")
    print("-" * 60)
    result = subprocess.run([sys.executable, test], capture_output=False)
    if result.returncode != 0:
        print(f"✗ Test failed: {test}")
        break
    print("-" * 60)

print("\n" + "=" * 60)
print("Test suite completed!")
print("=" * 60)
```

**Run:**
```bash
python run_all_tests.py
```

---

## 📚 Additional Resources

- **Full Demo:** `python examples\demo.py`
- **CLI Help:** `blockiam --help`
- **Check Contract Functions:** See your `ABI.json` file

## 🆘 Troubleshooting

**Connection Error:**
```python
# Verify connection
from blockiam import IAMClient
client = IAMClient()
print(f"Connected: {client.w3.is_connected()}")
```

**Wrong Function Names:**
```python
# List available functions
client = IAMClient()
for func in client.contract.abi:
    if func.get('type') == 'function':
        print(func['name'])
```

---

**Happy Testing! 🚀**
