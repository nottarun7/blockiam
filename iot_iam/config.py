"""
Configuration management for iot_iam library
"""

import os
from typing import Optional
from dotenv import load_dotenv
from .exceptions import ConfigurationError


class Config:
    """Configuration handler for IAM client"""
    
    def __init__(self, env_file: str = ".env"):
        """
        Initialize configuration from environment file
        
        Args:
            env_file: Path to .env file
            
        Raises:
            ConfigurationError: If required variables are missing
        """
        load_dotenv(env_file)
        
        self.rpc_url = os.getenv("RPC_URL")
        self.private_key = os.getenv("PRIVATE_KEY")
        self.contract_address = os.getenv("CONTRACT_ADDRESS")
        self.chain_id = int(os.getenv("CHAIN_ID", 1337))
        self.gas_limit = int(os.getenv("GAS_LIMIT", 3000000))
        self.abi_path = os.getenv("ABI_PATH", "ABI.json")
        
        self._validate()
    
    def _validate(self) -> None:
        """Validate that all required configuration is present"""
        if not self.rpc_url:
            raise ConfigurationError("RPC_URL is required in environment variables")
        
        if not self.private_key:
            raise ConfigurationError("PRIVATE_KEY is required in environment variables")
        
        if not self.contract_address:
            raise ConfigurationError("CONTRACT_ADDRESS is required in environment variables")
    
    @property
    def is_valid(self) -> bool:
        """Check if configuration is valid"""
        return all([self.rpc_url, self.private_key, self.contract_address])


class ConfigBuilder:
    """Builder pattern for creating Config objects"""
    
    def __init__(self):
        self._rpc_url: Optional[str] = None
        self._private_key: Optional[str] = None
        self._contract_address: Optional[str] = None
        self._chain_id: int = 1337
        self._gas_limit: int = 3000000
    
    def with_rpc_url(self, url: str) -> 'ConfigBuilder':
        """Set RPC URL"""
        self._rpc_url = url
        return self
    
    def with_private_key(self, key: str) -> 'ConfigBuilder':
        """Set private key"""
        self._private_key = key
        return self
    
    def with_contract_address(self, address: str) -> 'ConfigBuilder':
        """Set contract address"""
        self._contract_address = address
        return self
    
    def with_chain_id(self, chain_id: int) -> 'ConfigBuilder':
        """Set chain ID"""
        self._chain_id = chain_id
        return self
    
    def with_gas_limit(self, gas_limit: int) -> 'ConfigBuilder':
        """Set gas limit"""
        self._gas_limit = gas_limit
        return self
    
    def build(self) -> Config:
        """Build Config object"""
        # Temporarily set env vars for Config initialization
        if self._rpc_url:
            os.environ["RPC_URL"] = self._rpc_url
        if self._private_key:
            os.environ["PRIVATE_KEY"] = self._private_key
        if self._contract_address:
            os.environ["CONTRACT_ADDRESS"] = self._contract_address
        os.environ["CHAIN_ID"] = str(self._chain_id)
        os.environ["GAS_LIMIT"] = str(self._gas_limit)
        
        return Config()
