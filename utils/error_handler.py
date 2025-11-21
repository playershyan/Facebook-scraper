"""
Comprehensive error handling for the scraper.
Handles network errors, API errors, technical errors, and crashes.
"""
import asyncio
import sys
import traceback
from datetime import datetime
from typing import Dict, Optional, Callable, Any
from enum import Enum


class ErrorType(Enum):
    """Types of errors that can occur."""
    NETWORK_ERROR = "network_error"
    API_ERROR = "api_error"
    TIMEOUT_ERROR = "timeout_error"
    PARSE_ERROR = "parse_error"
    FILE_ERROR = "file_error"
    SYSTEM_ERROR = "system_error"
    UNKNOWN_ERROR = "unknown_error"


class ScraperErrorHandler:
    """Handles errors and implements recovery strategies."""
    
    def __init__(self, session_manager=None, max_retries: int = 3, retry_delays: Dict[str, float] = None):
        """
        Initialize error handler.
        
        Args:
            session_manager: Session manager instance for saving errors
            max_retries: Maximum retry attempts
            retry_delays: Delays for different error types (seconds)
        """
        self.session_manager = session_manager
        self.max_retries = max_retries
        self.retry_delays = retry_delays or {
            ErrorType.NETWORK_ERROR: 5.0,
            ErrorType.API_ERROR: 10.0,
            ErrorType.TIMEOUT_ERROR: 3.0,
            ErrorType.PARSE_ERROR: 1.0,
            ErrorType.FILE_ERROR: 1.0,
            ErrorType.SYSTEM_ERROR: 30.0,
        }
        self.error_log = []
    
    def classify_error(self, exception: Exception) -> ErrorType:
        """
        Classify an exception into an error type.
        
        Args:
            exception: The exception to classify
        
        Returns:
            ErrorType enum value
        """
        error_name = type(exception).__name__
        error_msg = str(exception).lower()
        
        # Network errors
        if any(keyword in error_name.lower() or keyword in error_msg 
               for keyword in ['connection', 'network', 'dns', 'resolve', 'unreachable']):
            return ErrorType.NETWORK_ERROR
        
        # Timeout errors
        if any(keyword in error_name.lower() or keyword in error_msg 
               for keyword in ['timeout', 'timed out', 'deadline exceeded']):
            return ErrorType.TIMEOUT_ERROR
        
        # API errors
        if any(keyword in error_name.lower() or keyword in error_msg 
               for keyword in ['api', 'http', '429', '503', '502', '500', 'rate limit']):
            return ErrorType.API_ERROR
        
        # Parse errors
        if any(keyword in error_name.lower() 
               for keyword in ['json', 'parse', 'decode', 'syntax']):
            return ErrorType.PARSE_ERROR
        
        # File errors
        if any(keyword in error_name.lower() 
               for keyword in ['file', 'io', 'permission', 'not found', 'exists']):
            return ErrorType.FILE_ERROR
        
        # System errors
        if any(keyword in error_name.lower() 
               for keyword in ['memory', 'disk', 'resource', 'oserror']):
            return ErrorType.SYSTEM_ERROR
        
        return ErrorType.UNKNOWN_ERROR
    
    def log_error(self, error_type: ErrorType, exception: Exception, context: Optional[Dict] = None):
        """
        Log an error to session manager and error log.
        
        Args:
            error_type: Type of error
            exception: The exception
            context: Additional context information
        """
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type.value,
            "error_name": type(exception).__name__,
            "error_message": str(exception),
            "traceback": traceback.format_exc(),
            "context": context or {},
        }
        
        self.error_log.append(error_entry)
        
        # Save to session manager if available
        if self.session_manager:
            self.session_manager.update_session(
                error={
                    "type": error_type.value,
                    "message": str(exception),
                    "details": error_entry,
                }
            )
        
        # Print error (but don't crash)
        print(f"\n[ERROR] {error_type.value.upper()}: {type(exception).__name__}")
        print(f"  Message: {str(exception)}")
        if context:
            print(f"  Context: {context}")
    
    async def retry_with_backoff(
        self,
        func: Callable,
        error_type: Optional[ErrorType] = None,
        max_retries: Optional[int] = None,
        context: Optional[Dict] = None,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute a function with retry logic and exponential backoff.
        
        Args:
            func: Async function to execute
            error_type: Expected error type (auto-detected if None)
            max_retries: Maximum retry attempts (uses default if None)
            context: Context information for error logging
            *args, **kwargs: Arguments to pass to func
        
        Returns:
            Result of func execution
        
        Raises:
            Exception: If all retries fail
        """
        retries = max_retries or self.max_retries
        last_exception = None
        
        for attempt in range(retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                # Classify error if not provided
                if error_type is None:
                    error_type = self.classify_error(e)
                
                # Log error
                self.log_error(error_type, e, {**(context or {}), "attempt": attempt + 1})
                
                # Don't retry on last attempt
                if attempt >= retries:
                    break
                
                # Calculate delay based on error type and attempt
                base_delay = self.retry_delays.get(error_type, 5.0)
                delay = base_delay * (2 ** attempt)  # Exponential backoff
                
                print(f"  Retrying in {delay:.1f} seconds... (attempt {attempt + 1}/{retries})")
                await asyncio.sleep(delay)
        
        # All retries failed
        raise last_exception
    
    def is_recoverable_error(self, exception: Exception) -> bool:
        """
        Check if an error is recoverable (should be retried).
        
        Args:
            exception: The exception to check
        
        Returns:
            True if error is recoverable
        """
        error_type = self.classify_error(exception)
        
        # Most errors are recoverable except some system errors
        unrecoverable = [
            ErrorType.SYSTEM_ERROR,  # Some system errors might not be recoverable
        ]
        
        return error_type not in unrecoverable
    
    def get_recovery_strategy(self, error_type: ErrorType) -> Dict[str, Any]:
        """
        Get recovery strategy for an error type.
        
        Args:
            error_type: Type of error
        
        Returns:
            Recovery strategy dictionary
        """
        strategies = {
            ErrorType.NETWORK_ERROR: {
                "retry": True,
                "max_retries": 5,
                "delay": 5.0,
                "action": "Wait and retry connection",
            },
            ErrorType.API_ERROR: {
                "retry": True,
                "max_retries": 3,
                "delay": 10.0,
                "action": "Wait for API rate limit or server recovery",
            },
            ErrorType.TIMEOUT_ERROR: {
                "retry": True,
                "max_retries": 3,
                "delay": 3.0,
                "action": "Retry with longer timeout",
            },
            ErrorType.PARSE_ERROR: {
                "retry": True,
                "max_retries": 2,
                "delay": 1.0,
                "action": "Retry parsing or skip this item",
            },
            ErrorType.FILE_ERROR: {
                "retry": True,
                "max_retries": 3,
                "delay": 1.0,
                "action": "Retry file operation",
            },
            ErrorType.SYSTEM_ERROR: {
                "retry": False,
                "max_retries": 1,
                "delay": 30.0,
                "action": "Save checkpoint and exit",
            },
        }
        
        return strategies.get(error_type, {
            "retry": True,
            "max_retries": 3,
            "delay": 5.0,
            "action": "Retry operation",
        })
    
    def save_checkpoint_on_error(self, checkpoint_data: Dict):
        """
        Save a checkpoint when an error occurs to prevent data loss.
        
        Args:
            checkpoint_data: Checkpoint data to save
        """
        if self.session_manager:
            try:
                self.session_manager.save_checkpoint(checkpoint_data)
                print("Checkpoint saved after error to prevent data loss")
            except Exception as e:
                print(f"Warning: Could not save checkpoint: {e}")
    
    def get_error_summary(self) -> Dict:
        """Get summary of all errors logged."""
        if not self.error_log:
            return {"total_errors": 0, "by_type": {}}
        
        by_type = {}
        for error in self.error_log:
            error_type = error["error_type"]
            by_type[error_type] = by_type.get(error_type, 0) + 1
        
        return {
            "total_errors": len(self.error_log),
            "by_type": by_type,
            "latest_errors": self.error_log[-10:],  # Last 10 errors
        }


def handle_crash_recovery(session_manager, checkpoint_data: Dict):
    """
    Handle recovery after a crash (e.g., laptop died, process killed).
    
    Args:
        session_manager: Session manager instance
        checkpoint_data: Data to save as checkpoint
    """
    try:
        # Mark session as interrupted
        if session_manager.current_session:
            session_manager.end_session(status="interrupted")
        
        # Save emergency checkpoint
        session_manager.save_checkpoint(checkpoint_data)
        print("\n[CRASH RECOVERY] Emergency checkpoint saved")
        print("You can resume from this checkpoint on next run")
    except Exception as e:
        print(f"\n[CRASH RECOVERY] Warning: Could not save recovery data: {e}")


async def safe_operation(
    func: Callable,
    error_handler: ScraperErrorHandler,
    checkpoint_data: Optional[Dict] = None,
    *args,
    **kwargs
) -> Optional[Any]:
    """
    Execute an operation safely with error handling and checkpoint saving.
    
    Args:
        func: Async function to execute
        error_handler: Error handler instance
        checkpoint_data: Optional checkpoint data to save on error
        *args, **kwargs: Arguments for func
    
    Returns:
        Result of func or None if failed
    """
    try:
        return await error_handler.retry_with_backoff(func, context={"operation": func.__name__}, *args, **kwargs)
    except Exception as e:
        # Save checkpoint if provided
        if checkpoint_data:
            error_handler.save_checkpoint_on_error(checkpoint_data)
        
        # Log final error
        error_type = error_handler.classify_error(e)
        error_handler.log_error(error_type, e, {"operation": func.__name__})
        
        return None

