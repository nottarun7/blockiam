"""
Custom exceptions for the iot_iam library
"""


class IAMException(Exception):
    """Base exception for all IAM-related errors"""
    pass


class ConnectionError(IAMException):
    """Raised when connection to blockchain fails"""
    pass


class ConfigurationError(IAMException):
    """Raised when configuration is invalid or missing"""
    pass


class TransactionError(IAMException):
    """Raised when a transaction fails"""
    pass


class ContractError(IAMException):
    """Raised when contract interaction fails"""
    pass


class CacheError(IAMException):
    """Raised when cache operations fail"""
    pass
