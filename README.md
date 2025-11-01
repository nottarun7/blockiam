# BlockIAM (v1.0.1)

Simple Python library-ish framework ??? for interacting with the deployed IAM.sol smart contract to manage IoT device identity and access control.

## 📦 Installation

```bash
pip install -e .
```

## ⚙️ Configuration

Create a `.env` file in the project root:

```env
RPC_URL=http://127.0.0.1:7545
PRIVATE_KEY=your_private_key_here
CONTRACT_ADDRESS=your_deployed_contract_address
CHAIN_ID=1337
```

**Getting these values:**
- `RPC_URL` - Your Ganache RPC endpoint (default: http://127.0.0.1:7545)
- `PRIVATE_KEY` - Copy from Ganache accounts (remove `0x` prefix)
- `CONTRACT_ADDRESS` - Address where you deployed IAM.sol
- `CHAIN_ID` - 1337 for Ganache, 1 for mainnet

## 🚀 Quick Start

### Python Usage

```python
from blockiam import IAMClient

# Initialize client
client = IAMClient()

# Register a device
client.register_device(
    address="0x1234567890123456789012345678901234567890",
    name="Smart Sensor",
    role="sensor",
    metadata="Building A, Floor 3"
)

# Grant access
client.grant_access("0x1234567890123456789012345678901234567890")

# Check access
result = client.check_access("0x1234567890123456789012345678901234567890")
print(f"Has access: {result['has_access']}")

# Log an event
client.log_access("Temperature reading")

# Get device info
device = client.get_device_info("0x1234567890123456789012345678901234567890")
print(device['data'])

# Fetch blockchain logs
logs = client.get_logs()
print(f"Found {logs['count']} log entries")

# Sync to local cache
client.sync_cache()

# Get cached logs
cached = client.get_cached_logs(limit=10)

# Cleanup
client.close()
```

### CLI Usage

```bash
# Register a device
blockiam register 0x... "Device Name" sensor --metadata "Location"

# Grant access
blockiam grant 0x...

# Check access
blockiam check 0x...

# Get device info
blockiam info 0x...

# Log an event
blockiam log "Access reason"

# View logs
blockiam logs --limit 10

# Sync to cache
blockiam sync

# View cached logs
blockiam cache
```

### Run the Demo

```bash
python examples\demo.py
```

## 📚 Available Methods

| Method | Description |
|--------|-------------|
| `register_device(address, name, role, metadata)` | Register a new device |
| `grant_access(address, expiry=0)` | Grant access to device |
| `revoke_access(address)` | Revoke device access |
| `assign_role(address, role)` | Assign role to device |
| `check_access(address)` | Check if device has access |
| `log_access(reason)` | Log an access event |
| `get_device_info(address)` | Get device information |
| `get_logs(from_block=0, to_block='latest')` | Fetch blockchain logs |
| `sync_cache()` | Sync data to local SQLite cache |
| `get_cached_logs(limit=100)` | Get logs from cache |

## 📁 Project Structure

```
iot_iam/
├── iot_iam/              # Main package
│   ├── __init__.py      # Package exports
│   ├── core.py          # IAMClient implementation
│   ├── config.py        # Configuration management
│   ├── db.py            # SQLite cache
│   ├── exceptions.py    # Custom exceptions
│   ├── logger.py        # Logging setup
│   ├── utils.py         # Helper functions
│   └── cli.py           # CLI interface
├── examples/
│   └── demo.py          # Working example
├── ABI.json             # Contract ABI
├── setup.py             # Package setup
└── README.md            # This file
```

## 🔧 Dependencies

- web3 >= 6.0.0
- python-dotenv >= 0.19.0
- rich >= 12.0.0
- click >= 8.0.0

## ❓ Troubleshooting

**Connection Error:**
- Make sure Ganache is running
- Check `RPC_URL` in `.env`

**Transaction Fails:**
- Ensure account has ETH for gas
- Verify private key has permissions

**Import Error:**
- Run `pip install -e .`
- Check you're in the correct directory

## 📝 License

MIT License

