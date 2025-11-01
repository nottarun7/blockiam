"""
SQLite database helper for local caching of devices and access logs
"""

import sqlite3
from typing import List, Dict, Any, Optional
from pathlib import Path
from contextlib import contextmanager

from .exceptions import CacheError
from .logger import logger


class DeviceDB:
    """SQLite database manager for IAM data caching"""
    
    def __init__(self, db_path: str = "iot_iam_cache.db"):
        """
        Initialize database connection and create tables if needed
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.conn: Optional[sqlite3.Connection] = None
        self._connect()
        self._create_tables()
    
    def _connect(self) -> None:
        """Establish database connection"""
        try:
            self.conn = sqlite3.connect(str(self.db_path))
            self.conn.row_factory = sqlite3.Row
            logger.debug(f"Connected to database: {self.db_path}")
        except Exception as e:
            raise CacheError(f"Failed to connect to database: {str(e)}")
    
    @contextmanager
    def _get_cursor(self):
        """Context manager for database cursor"""
        if not self.conn:
            raise CacheError("Database connection not established")
        
        cursor = self.conn.cursor()
        try:
            yield cursor
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise CacheError(f"Database operation failed: {str(e)}")
        finally:
            cursor.close()
    
    def _create_tables(self) -> None:
        """Create database tables if they don't exist"""
        with self._get_cursor() as cursor:
            # Devices table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS devices (
                    address TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    metadata TEXT,
                    registeredAt INTEGER NOT NULL,
                    updatedAt INTEGER DEFAULT (strftime('%s', 'now'))
                )
            ''')
            
            # Logs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device TEXT NOT NULL,
                    success INTEGER NOT NULL,
                    reason TEXT NOT NULL,
                    timestamp INTEGER NOT NULL,
                    txHash TEXT UNIQUE NOT NULL,
                    createdAt INTEGER DEFAULT (strftime('%s', 'now'))
                )
            ''')
            
            # Create indexes for better query performance
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_logs_device 
                ON logs(device)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_logs_timestamp 
                ON logs(timestamp DESC)
            ''')
        
        logger.debug("Database tables initialized")
    
    def insert_device(
        self,
        address: str,
        name: str,
        role: str,
        metadata: str,
        registered_at: int
    ) -> bool:
        """
        Insert or update a device in the cache
        
        Args:
            address: Device Ethereum address
            name: Device name
            role: Device role
            metadata: Additional metadata
            registered_at: Registration timestamp
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self._get_cursor() as cursor:
                cursor.execute('''
                    INSERT OR REPLACE INTO devices 
                    (address, name, role, metadata, registeredAt, updatedAt)
                    VALUES (?, ?, ?, ?, ?, strftime('%s', 'now'))
                ''', (address, name, role, metadata, registered_at))
            
            logger.debug(f"Device cached: {name} ({address})")
            return True
        except CacheError as e:
            logger.error(f"Error caching device: {e}")
            return False
    
    def insert_log(
        self,
        device: str,
        success: bool,
        reason: str,
        timestamp: int,
        tx_hash: str
    ) -> bool:
        """
        Insert an access log entry
        
        Args:
            device: Device address
            success: Whether access was successful
            reason: Access reason
            timestamp: Event timestamp
            tx_hash: Transaction hash
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self._get_cursor() as cursor:
                cursor.execute('''
                    INSERT OR IGNORE INTO logs 
                    (device, success, reason, timestamp, txHash)
                    VALUES (?, ?, ?, ?, ?)
                ''', (device, int(success), reason, timestamp, tx_hash))
            
            logger.debug(f"Log cached: {tx_hash[:10]}...")
            return True
        except CacheError as e:
            logger.error(f"Error caching log: {e}")
            return False
    
    def fetch_all_devices(self) -> List[Dict[str, Any]]:
        """
        Fetch all devices from cache
        
        Returns:
            List of device dictionaries
        """
        try:
            with self._get_cursor() as cursor:
                cursor.execute('SELECT * FROM devices ORDER BY name')
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except CacheError as e:
            logger.error(f"Error fetching devices: {e}")
            return []
    
    def fetch_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch recent logs from cache
        
        Args:
            limit: Maximum number of logs to retrieve
            
        Returns:
            List of log dictionaries
        """
        try:
            with self._get_cursor() as cursor:
                cursor.execute('''
                    SELECT * FROM logs 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (limit,))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except CacheError as e:
            logger.error(f"Error fetching logs: {e}")
            return []
    
    def get_device(self, address: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific device by address
        
        Args:
            address: Device address
            
        Returns:
            Device dictionary or None if not found
        """
        try:
            with self._get_cursor() as cursor:
                cursor.execute('SELECT * FROM devices WHERE address = ?', (address,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except CacheError as e:
            logger.error(f"Error getting device: {e}")
            return None
    
    def get_device_logs(
        self,
        address: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get logs for a specific device
        
        Args:
            address: Device address
            limit: Maximum number of logs
            
        Returns:
            List of log dictionaries
        """
        try:
            with self._get_cursor() as cursor:
                cursor.execute('''
                    SELECT * FROM logs 
                    WHERE device = ?
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (address, limit))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except CacheError as e:
            logger.error(f"Error fetching device logs: {e}")
            return []
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get database statistics
        
        Returns:
            Dictionary with counts
        """
        try:
            with self._get_cursor() as cursor:
                cursor.execute('SELECT COUNT(*) FROM devices')
                device_count = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM logs')
                log_count = cursor.fetchone()[0]
                
                return {
                    'total_devices': device_count,
                    'total_logs': log_count
                }
        except CacheError as e:
            logger.error(f"Error fetching stats: {e}")
            return {'total_devices': 0, 'total_logs': 0}
    
    def clear_logs(self) -> bool:
        """
        Clear all logs from cache
        
        Returns:
            True if successful
        """
        try:
            with self._get_cursor() as cursor:
                cursor.execute('DELETE FROM logs')
            logger.info("Cache logs cleared")
            return True
        except CacheError as e:
            logger.error(f"Error clearing logs: {e}")
            return False
    
    def clear_devices(self) -> bool:
        """
        Clear all devices from cache
        
        Returns:
            True if successful
        """
        try:
            with self._get_cursor() as cursor:
                cursor.execute('DELETE FROM devices')
            logger.info("Cache devices cleared")
            return True
        except CacheError as e:
            logger.error(f"Error clearing devices: {e}")
            return False
    
    def close(self) -> None:
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.debug("Database connection closed")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
    
    def __del__(self):
        """Ensure connection is closed on deletion"""
        self.close()


class CacheManager(DeviceDB):
    """
    Extended cache manager with additional high-level operations
    
    Provides a more convenient interface for common caching operations.
    """
    
    def sync_device(self, device_info: Dict[str, Any]) -> bool:
        """
        Sync a device from blockchain data
        
        Args:
            device_info: Device information dictionary
            
        Returns:
            True if successful
        """
        return self.insert_device(
            address=device_info.get('address', ''),
            name=device_info.get('name', ''),
            role=device_info.get('role', ''),
            metadata=device_info.get('metadata', ''),
            registered_at=device_info.get('registered_at', 0)
        )
    
    def sync_log(self, log_entry: Dict[str, Any]) -> bool:
        """
        Sync a log entry from blockchain data
        
        Args:
            log_entry: Log entry dictionary
            
        Returns:
            True if successful
        """
        return self.insert_log(
            device=log_entry.get('device', ''),
            success=log_entry.get('success', False),
            reason=log_entry.get('reason', ''),
            timestamp=log_entry.get('timestamp', 0),
            tx_hash=log_entry.get('tx_hash', '')
        )
