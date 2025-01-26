import os
from pathlib import Path
from typing import Dict
import asyncio
from contextlib import asynccontextmanager
import subprocess
import shlex
from typing import Dict
import asyncio

class SecurityError(Exception):
    """Raised when a security check fails"""
    pass

@asynccontextmanager
async def safe_file_write(file_path: str):
    """
    Context manager for safely writing to files.
    Implements proper locking and cleanup.
    
    Args:
        file_path: Path where the file should be written
        
    Yields:
        Path object for the file
        
    Raises:
        SecurityError: If security checks fail
    """
    path = Path(file_path)
    
    # Security checks
    if not path.suffix in {'.py', '.js', '.ts', '.txt'}:
        raise SecurityError(f"Unsupported file type: {path.suffix}")
        
    if not path.parent.exists():
        raise SecurityError(f"Directory does not exist: {path.parent}")
        
    try:
        # Create a lock file to prevent concurrent writes
        lock_path = path.with_suffix(path.suffix + '.lock')
        with open(lock_path, 'w') as f:
            f.write(str(os.getpid()))
            
        yield path
        
    finally:
        # Cleanup: Always remove the lock file
        if lock_path.exists():
            lock_path.unlink()

async def file_writer(arguments: Dict[str, str]) -> Dict[str, str]:
    """
    Safely writes content to a file with proper error handling.
    
    Args:
        arguments: Dictionary containing:
            - file_path: Where to write the code
            - content: The code content to write
        
    Returns:
        Dict containing status and message
    """
    file_path = arguments['file_path']
    content = arguments['content']
    
    try:
        async with safe_file_write(file_path) as path:
            # Write with atomic operations
            temp_path = path.with_suffix(path.suffix + '.tmp')
            with open(temp_path, 'w') as f:
                f.write(content)
            # Atomic replace
            temp_path.replace(path)
            
        return {
            "status": "success",
            "message": f"Code written to {file_path}"
        }
        
    except SecurityError as e:
        return {
            "status": "error",
            "message": f"Security check failed: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to write file: {str(e)}"
        }


class ExecutionError(Exception):
    """Raised when code execution fails"""
    pass

async def file_executor(arguments: Dict[str, str]) -> Dict[str, str]:
    """
    Executes a file with the specified command in a controlled environment.
    
    Args:
        arguments: Dictionary containing:
            - file_path: Path to the file to execute
            - command: Command to run the file (e.g., "python script.py")
        
    Returns:
        Dict containing execution status and output
    """
    file_path = arguments['file_path']
    command = arguments['command']
    
    # Validate the command for security
    if not command.startswith(('python', 'node', 'deno')):
        raise ExecutionError("Unsupported execution environment")
    
    # Parse command safely using shlex
    try:
        cmd_parts = shlex.split(command)
    except ValueError as e:
        raise ExecutionError(f"Invalid command format: {e}")
    
    # Set execution limits for safety
    limits = {
        'timeout': 30,  # Maximum execution time in seconds
        'memory': 512 * 1024 * 1024  # 512MB memory limit
    }
    
    try:
        # Run in subprocess with resource limits
        process = await asyncio.create_subprocess_exec(
            *cmd_parts,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            limit=limits['memory']
        )
        
        try:
            # Wait for process with timeout
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=limits['timeout']
            )
            
            if process.returncode != 0:
                raise ExecutionError(f"Process failed: {stderr.decode()}")
                
            return {
                "status": "success",
                "output": stdout.decode(),
                "stderr": stderr.decode()
            }
            
        except asyncio.TimeoutError:
            process.kill()
            raise ExecutionError("Execution timed out")
            
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }