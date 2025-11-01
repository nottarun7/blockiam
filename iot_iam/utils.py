"""
Utility functions for iot_iam library
"""

from typing import Dict, Any, Optional
from datetime import datetime
from web3 import Web3


def format_address(address: str) -> str:
    """
    Format an Ethereum address to checksum format
    
    Args:
        address: Ethereum address
        
    Returns:
        Checksummed address
    """
    return Web3.to_checksum_address(address)


def format_timestamp(timestamp: int) -> str:
    """
    Format Unix timestamp to human-readable string
    
    Args:
        timestamp: Unix timestamp
        
    Returns:
        Formatted datetime string
    """
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def validate_address(address: str) -> bool:
    """
    Validate if string is a valid Ethereum address
    
    Args:
        address: Address to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        Web3.to_checksum_address(address)
        return True
    except (ValueError, TypeError):
        return False


def build_response(
    status: str,
    data: Optional[Any] = None,
    tx_hash: Optional[str] = None,
    message: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Build standardized response dictionary
    
    Args:
        status: Response status ('success', 'failed', 'error')
        data: Response data
        tx_hash: Transaction hash
        message: Error or info message
        **kwargs: Additional key-value pairs
        
    Returns:
        Standardized response dictionary
    """
    response = {"status": status}
    
    if data is not None:
        response["data"] = data
    
    if tx_hash:
        response["tx_hash"] = tx_hash
    
    if message:
        response["message"] = message
    
    response.update(kwargs)
    
    return response


def truncate_address(address: str, chars: int = 8) -> str:
    """
    Truncate Ethereum address for display
    
    Args:
        address: Full Ethereum address
        chars: Number of characters to show at start/end
        
    Returns:
        Truncated address (e.g., "0x1234...5678")
    """
    if len(address) <= chars * 2:
        return address
    return f"{address[:chars]}...{address[-chars:]}"


def wei_to_ether(wei: int) -> float:
    """
    Convert Wei to Ether
    
    Args:
        wei: Amount in Wei
        
    Returns:
        Amount in Ether
    """
    return Web3.from_wei(wei, 'ether')


def ether_to_wei(ether: float) -> int:
    """
    Convert Ether to Wei
    
    Args:
        ether: Amount in Ether
        
    Returns:
        Amount in Wei
    """
    return Web3.to_wei(ether, 'ether')
