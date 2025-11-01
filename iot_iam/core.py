"""
Core IAMClient class for interacting with the IAM smart contract
"""

import json
from typing import Dict, Any, Optional, List
from pathlib import Path

from web3 import Web3
from web3.contract import Contract
from web3.exceptions import ContractLogicError

from .config import Config
from .db import CacheManager
from .exceptions import ConnectionError, TransactionError, ContractError
from .logger import logger
from .utils import format_address, build_response, validate_address

# Try to import POA middleware for compatibility with POA chains
try:
    from web3.middleware import geth_poa_middleware
    POA_MIDDLEWARE_AVAILABLE = True
except ImportError:
    try:
        from web3.middleware.geth_poa import geth_poa_middleware
        POA_MIDDLEWARE_AVAILABLE = True
    except ImportError:
        POA_MIDDLEWARE_AVAILABLE = False
        geth_poa_middleware = None


class IAMClient:
    """
    Main client for interacting with IAM smart contract
    
    Provides a high-level interface for device registration, access control,
    and event logging on the blockchain.
    
    Example:
        >>> client = IAMClient()
        >>> client.register_device("0x123...", "Device1", "sensor")
        {'status': 'success', 'tx_hash': '0xabc...'}
    """
    
    def __init__(self, config: Optional[Config] = None, env_file: str = ".env"):
        """
        Initialize IAMClient with configuration
        
        Args:
            config: Configuration object (if None, loads from env_file)
            env_file: Path to .env file (default: ".env")
            
        Raises:
            ConnectionError: If connection to blockchain fails
            ConfigurationError: If configuration is invalid
        """
        self.config = config or Config(env_file)
        self._w3: Optional[Web3] = None
        self._contract: Optional[Contract] = None
        self._account = None
        self._cache_manager = CacheManager()
        
        self._initialize_web3()
        self._load_contract()
        
        logger.info(f"Connected to network (Chain ID: {self.config.chain_id})")
        logger.info(f"Using account: {self.account.address}")
        logger.info(f"Contract address: {self.config.contract_address}")
    
    @property
    def w3(self) -> Web3:
        """Get Web3 instance"""
        if self._w3 is None:
            raise ConnectionError("Web3 not initialized")
        return self._w3
    
    @property
    def contract(self) -> Contract:
        """Get contract instance"""
        if self._contract is None:
            raise ContractError("Contract not initialized")
        return self._contract
    
    @property
    def account(self):
        """Get account instance"""
        return self._account
    
    def _initialize_web3(self) -> None:
        """Initialize Web3 connection"""
        try:
            self._w3 = Web3(Web3.HTTPProvider(self.config.rpc_url))
            
            # Inject POA middleware if available
            if POA_MIDDLEWARE_AVAILABLE and geth_poa_middleware:
                try:
                    self._w3.middleware_onion.inject(geth_poa_middleware, layer=0)
                    logger.debug("POA middleware injected")
                except Exception as e:
                    logger.debug(f"POA middleware injection skipped: {e}")
            
            if not self._w3.is_connected():
                raise ConnectionError(f"Failed to connect to {self.config.rpc_url}")
            
            # Load account
            self._account = self._w3.eth.account.from_key(self.config.private_key)
            
        except Exception as e:
            raise ConnectionError(f"Failed to initialize Web3: {str(e)}")
    
    def _load_contract(self) -> None:
        """Load contract ABI and initialize contract instance"""
        try:
            # Find ABI file
            abi_path = Path(self.config.abi_path)
            if not abi_path.is_absolute():
                # Look in package directory
                package_dir = Path(__file__).parent.parent
                abi_path = package_dir / self.config.abi_path
            
            if not abi_path.exists():
                raise ContractError(f"ABI file not found: {abi_path}")
            
            with open(abi_path, "r") as f:
                contract_abi = json.load(f)
            
            self._contract = self.w3.eth.contract(
                address=format_address(self.config.contract_address),
                abi=contract_abi
            )
            
        except Exception as e:
            raise ContractError(f"Failed to load contract: {str(e)}")
    
    def _send_transaction(self, function, *args) -> Dict[str, Any]:
        """
        Helper to send a transaction to the contract
        
        Args:
            function: Contract function to call
            *args: Function arguments
            
        Returns:
            Response dictionary with status and transaction details
        """
        try:
            # Build transaction
            tx = function(*args).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': self.config.gas_limit,
                'gasPrice': self.w3.eth.gas_price,
                'chainId': self.config.chain_id
            })
            
            # Sign transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx, self.config.private_key)
            
            # Send transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            logger.debug(f"Transaction sent: {tx_hash.hex()}")
            
            # Wait for receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt['status'] == 1:
                logger.debug(f"Transaction successful (Gas used: {receipt['gasUsed']})")
                return build_response(
                    status='success',
                    tx_hash=tx_hash.hex(),
                    gas_used=receipt['gasUsed']
                )
            else:
                logger.warning(f"Transaction failed: {tx_hash.hex()}")
                return build_response(
                    status='failed',
                    tx_hash=tx_hash.hex(),
                    message="Transaction reverted"
                )
                
        except ContractLogicError as e:
            logger.error(f"Contract logic error: {str(e)}")
            return build_response(status='error', message=f"Contract error: {str(e)}")
        except Exception as e:
            logger.error(f"Transaction error: {str(e)}")
            return build_response(status='error', message=str(e))
    
    def register_device(
        self,
        address: str,
        name: str,
        role: str,
        metadata: str = ""
    ) -> Dict[str, Any]:
        """
        Register a new IoT device on the blockchain
        
        Args:
            address: Ethereum address of the device
            name: Human-readable device name
            role: Device role (e.g., 'sensor', 'actuator')
            metadata: Additional metadata (optional)
            
        Returns:
            Response dictionary with status and transaction hash
            
        Raises:
            ValueError: If address is invalid
        """
        if not validate_address(address):
            return build_response(status='error', message="Invalid Ethereum address")
        
        logger.info(f"Registering device: {name} ({address})")
        result = self._send_transaction(
            self.contract.functions.registerDevice,
            format_address(address),
            name,
            role,
            metadata
        )
        
        if result['status'] == 'success':
            logger.info(f"✓ Device registered successfully: {name}")
        else:
            logger.error(f"Failed to register device: {name}")
        
        return result
    
    def grant_access(self, address: str, expiry: int = 0) -> Dict[str, Any]:
        """
        Grant access to a device
        
        Args:
            address: Device address
            expiry: Access expiry timestamp (0 for permanent)
            
        Returns:
            Response dictionary
        """
        if not validate_address(address):
            return build_response(status='error', message="Invalid Ethereum address")
        
        logger.info(f"Granting access to: {address}")
        result = self._send_transaction(
            self.contract.functions.grantAccess,
            format_address(address),
            expiry
        )
        
        if result['status'] == 'success':
            logger.info("✓ Access granted successfully")
        
        return result
    
    def revoke_access(self, address: str) -> Dict[str, Any]:
        """
        Revoke access from a device
        
        Args:
            address: Device address
            
        Returns:
            Response dictionary
        """
        if not validate_address(address):
            return build_response(status='error', message="Invalid Ethereum address")
        
        logger.info(f"Revoking access from: {address}")
        result = self._send_transaction(
            self.contract.functions.revokeAccess,
            format_address(address)
        )
        
        if result['status'] == 'success':
            logger.info("✓ Access revoked successfully")
        
        return result
    
    def assign_role(self, address: str, role: str) -> Dict[str, Any]:
        """
        Assign a role to a device
        
        Args:
            address: Device address
            role: New role to assign
            
        Returns:
            Response dictionary
        """
        if not validate_address(address):
            return build_response(status='error', message="Invalid Ethereum address")
        
        logger.info(f"Assigning role '{role}' to: {address}")
        result = self._send_transaction(
            self.contract.functions.assignRole,
            format_address(address),
            role
        )
        
        if result['status'] == 'success':
            logger.info("✓ Role assigned successfully")
        
        return result
    
    def check_access(self, address: str) -> Dict[str, Any]:
        """
        Check if a device has access
        
        Args:
            address: Device address
            
        Returns:
            Response dictionary with has_access boolean
        """
        if not validate_address(address):
            return build_response(status='error', message="Invalid Ethereum address")
        
        try:
            # Try different possible function names in the contract
            contract_functions = self.contract.functions
            
            # Check which function exists
            if hasattr(contract_functions, 'checkAccess'):
                has_access = contract_functions.checkAccess(format_address(address)).call()
            elif hasattr(contract_functions, 'hasAccess'):
                has_access = contract_functions.hasAccess(format_address(address)).call()
            elif hasattr(contract_functions, 'isAuthorized'):
                has_access = contract_functions.isAuthorized(format_address(address)).call()
            else:
                return build_response(status='error', message="Access check function not found in contract")
            
            status_str = "GRANTED" if has_access else "DENIED"
            logger.info(f"Access for {address}: {status_str}")
            
            return build_response(status='success', has_access=has_access)
        except Exception as e:
            logger.error(f"Error checking access: {str(e)}")
            return build_response(status='error', message=str(e))
    
    def log_access(self, reason: str) -> Dict[str, Any]:
        """
        Log an access event on the blockchain
        
        Args:
            reason: Reason for access
            
        Returns:
            Response dictionary
        """
        logger.info(f"Logging access: {reason}")
        result = self._send_transaction(
            self.contract.functions.logAccess,
            reason
        )
        
        if result['status'] == 'success':
            logger.info("✓ Access logged successfully")
        
        return result
    
    def get_device_info(self, address: str) -> Dict[str, Any]:
        """
        Get information about a device
        
        Args:
            address: Device address
            
        Returns:
            Response dictionary with device information
        """
        if not validate_address(address):
            return build_response(status='error', message="Invalid Ethereum address")
        
        try:
            # Try different possible function names
            contract_functions = self.contract.functions
            
            if hasattr(contract_functions, 'getDevice'):
                device = contract_functions.getDevice(format_address(address)).call()
            elif hasattr(contract_functions, 'devices'):
                device = contract_functions.devices(format_address(address)).call()
            elif hasattr(contract_functions, 'getDeviceInfo'):
                device = contract_functions.getDeviceInfo(format_address(address)).call()
            else:
                return build_response(status='error', message="Device info function not found in contract")
            
            device_info = {
                'address': address,
                'name': device[0] if len(device) > 0 else '',
                'role': device[1] if len(device) > 1 else '',
                'metadata': device[2] if len(device) > 2 else '',
                'registered_at': device[3] if len(device) > 3 else 0,
                'is_registered': device[4] if len(device) > 4 else False
            }
            
            logger.info(f"Retrieved device info: {device_info['name']}")
            
            return build_response(status='success', data=device_info)
        except Exception as e:
            logger.error(f"Error getting device info: {str(e)}")
            return build_response(status='error', message=str(e))
    
    def get_logs(
        self,
        from_block: int = 0,
        to_block: str = 'latest'
    ) -> Dict[str, Any]:
        """
        Fetch AccessLogged events from the blockchain
        
        Args:
            from_block: Starting block number
            to_block: Ending block number or 'latest'
            
        Returns:
            Response dictionary with log entries
        """
        try:
            logger.info(f"Fetching logs from block {from_block} to {to_block}")
            
            # Get the event - try different event names
            if hasattr(self.contract.events, 'AccessLogged'):
                event = self.contract.events.AccessLogged
            elif hasattr(self.contract.events, 'AccessGranted'):
                event = self.contract.events.AccessGranted
            elif hasattr(self.contract.events, 'DeviceAccess'):
                event = self.contract.events.DeviceAccess
            else:
                logger.warning("No access log event found in contract")
                return build_response(status='success', data=[], count=0)
            
            # Create filter with correct parameter names (from_block, to_block)
            event_filter = event.create_filter(
                from_block=from_block,
                to_block=to_block
            )
            
            events = event_filter.get_all_entries()
            logs = []
            
            for event_entry in events:
                log_entry = {
                    'device': event_entry['args'].get('device', ''),
                    'success': event_entry['args'].get('success', True),
                    'reason': event_entry['args'].get('reason', ''),
                    'timestamp': event_entry['args'].get('timestamp', 0),
                    'tx_hash': event_entry['transactionHash'].hex(),
                    'block_number': event_entry['blockNumber']
                }
                logs.append(log_entry)
            
            logger.info(f"✓ Found {len(logs)} log entries")
            return build_response(status='success', data=logs, count=len(logs))
        except Exception as e:
            logger.error(f"Error fetching logs: {str(e)}")
            return build_response(status='error', message=str(e))
    
    def sync_cache(self) -> Dict[str, Any]:
        """
        Sync blockchain data to local SQLite cache
        
        Returns:
            Response dictionary
        """
        logger.info("Syncing data to local cache...")
        
        try:
            # Get all logs and cache them
            logs_result = self.get_logs()
            if logs_result['status'] == 'success':
                for log in logs_result['data']:
                    self._cache_manager.insert_log(
                        log['device'],
                        log['success'],
                        log['reason'],
                        log['timestamp'],
                        log['tx_hash']
                    )
            
            logger.info("✓ Cache synced successfully")
            return build_response(status='success', message='Cache synced')
        except Exception as e:
            logger.error(f"Error syncing cache: {str(e)}")
            return build_response(status='error', message=str(e))
    
    def get_cached_logs(self, limit: int = 100) -> Dict[str, Any]:
        """
        Get logs from local cache
        
        Args:
            limit: Maximum number of logs to retrieve
            
        Returns:
            Response dictionary with cached logs
        """
        try:
            logs = self._cache_manager.fetch_logs(limit)
            logger.info(f"Retrieved {len(logs)} logs from cache")
            return build_response(status='success', data=logs)
        except Exception as e:
            logger.error(f"Error fetching cached logs: {str(e)}")
            return build_response(status='error', message=str(e))
    
    def close(self) -> None:
        """Close all connections and cleanup resources"""
        if hasattr(self, '_cache_manager') and self._cache_manager:
            self._cache_manager.close()
        logger.info("IAMClient closed")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
    
    def __del__(self):
        """Ensure cleanup on deletion"""
        try:
            self.close()
        except Exception:
            pass  # Ignore errors during cleanup
