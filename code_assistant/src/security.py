# security.py
from pathlib import Path
import os
import hashlib
import re
from typing import List, Optional, Set
from dataclasses import dataclass
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class SecurityConfig:
    """Configuration class for security settings"""
    allowed_file_types: Set[str] = frozenset({'.py', '.js', '.ts', '.txt'})
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_directories: Set[str] = frozenset({'src', 'scripts', 'output'})
    
class SecurityValidator:
    """
    Handles security validation for file operations and code execution.
    Implements various security checks and maintains audit logs.
    """
    
    def __init__(self, config: Optional[SecurityConfig] = None):
        """
        Initialize the security validator with optional custom configuration.
        
        Args:
            config: Optional SecurityConfig object with custom settings
        """
        self.config = config or SecurityConfig()
        self._setup_audit_log()
    
    def _setup_audit_log(self) -> None:
        """Sets up the security audit log file"""
        audit_path = Path('security_audit.log')
        if not audit_path.exists():
            audit_path.touch()
            logger.info("Created new security audit log file")
    
    def log_security_event(self, event_type: str, details: str) -> None:
        """
        Logs security-related events with timestamp and details.
        
        Args:
            event_type: Type of security event (e.g., 'FILE_ACCESS', 'VALIDATION_FAIL')
            details: Detailed description of the event
        """
        timestamp = datetime.now().isoformat()
        with open('security_audit.log', 'a') as f:
            f.write(f"{timestamp} - {event_type} - {details}\n")
        logger.info(f"Security event logged: {event_type}")

    def validate_file_path(self, file_path: str) -> bool:
        """
        Validates if a file path is secure for operations.
        
        Args:
            file_path: Path to validate
            
        Returns:
            bool: True if path is secure, False otherwise
            
        Raises:
            ValueError: If path contains suspicious patterns
        """
        path = Path(file_path)
        
        # Check for directory traversal attempts
        if '..' in path.parts:
            self.log_security_event('VALIDATION_FAIL', f'Directory traversal attempt: {file_path}')
            raise ValueError("Directory traversal not allowed")
        
        # Validate file extension
        if path.suffix not in self.config.allowed_file_types:
            self.log_security_event('VALIDATION_FAIL', f'Invalid file type: {path.suffix}')
            return False
        
        # Validate parent directory
        if not any(allowed_dir in str(path.parent) for allowed_dir in self.config.allowed_directories):
            self.log_security_event('VALIDATION_FAIL', f'Invalid directory: {path.parent}')
            return False
            
        return True
    
    def scan_file_content(self, content: str) -> List[str]:
        """
        Scans file content for potentially dangerous patterns.
        
        Args:
            content: File content to scan
            
        Returns:
            List of identified security concerns
        """
        concerns = []
        
        # Patterns to check for
        dangerous_patterns = {
            r'os\.system\(': 'Direct system command execution',
            r'subprocess\.': 'Subprocess execution',
            r'eval\(': 'Code evaluation',
            r'exec\(': 'Code execution',
            r'__import__\(': 'Dynamic imports',
            r'open\(.*,.*w.*\)': 'File write operations',
            r'requests\.': 'Network requests',
            r'socket\.': 'Socket operations'
        }
        
        for pattern, description in dangerous_patterns.items():
            if re.search(pattern, content):
                concerns.append(f"Found potentially dangerous pattern: {description}")
                self.log_security_event('CONTENT_SCAN', f'Found pattern: {pattern}')
                
        return concerns
    
    def compute_file_hash(self, file_path: str) -> str:
        """
        Computes SHA-256 hash of a file for integrity checking.
        
        Args:
            file_path: Path to the file
            
        Returns:
            str: Hex digest of file hash
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        sha256_hash = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
                
        return sha256_hash.hexdigest()
    
    def verify_file_size(self, file_path: str) -> bool:
        """
        Verifies that a file doesn't exceed the maximum allowed size.
        
        Args:
            file_path: Path to the file
            
        Returns:
            bool: True if file size is acceptable
        """
        path = Path(file_path)
        if not path.exists():
            return True
            
        file_size = path.stat().st_size
        if file_size > self.config.max_file_size:
            self.log_security_event('SIZE_LIMIT', f'File exceeds size limit: {file_path}')
            return False
            
        return True

def create_security_context(custom_config: Optional[SecurityConfig] = None) -> SecurityValidator:
    """
    Factory function to create a configured SecurityValidator instance.
    
    Args:
        custom_config: Optional custom security configuration
        
    Returns:
        SecurityValidator: Configured security validator instance
    """
    return SecurityValidator(custom_config)


__all__ = ['create_security_context', 'SecurityValidator', 'SecurityConfig']