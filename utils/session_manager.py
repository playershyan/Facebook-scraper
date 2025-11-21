"""
Session Manager for tracking scraping sessions and enabling resume capability.
Similar to browser history - accessible anytime, tracks all sessions.
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path


class SessionManager:
    """Manages scraping sessions and tracks progress for recovery."""
    
    def __init__(self, sessions_dir: str = "sessions"):
        """
        Initialize session manager.
        
        Args:
            sessions_dir: Directory to store session data
        """
        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(exist_ok=True)
        self.current_session = None
        self.sessions_file = self.sessions_dir / "sessions_history.json"
        self.checkpoints_dir = self.sessions_dir / "checkpoints"
        self.checkpoints_dir.mkdir(exist_ok=True)
        
        # Load session history
        self.sessions_history = self._load_sessions_history()
    
    def _load_sessions_history(self) -> List[Dict]:
        """Load session history from file."""
        if not self.sessions_file.exists():
            return []
        
        try:
            with open(self.sessions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load session history: {e}")
            return []
    
    def _save_sessions_history(self):
        """Save session history to file."""
        try:
            with open(self.sessions_file, 'w', encoding='utf-8') as f:
                json.dump(self.sessions_history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save session history: {e}")
    
    def create_session(self, session_id: Optional[str] = None, metadata: Optional[Dict] = None) -> str:
        """
        Create a new scraping session.
        
        Args:
            session_id: Optional custom session ID
            metadata: Optional metadata (config, total_pages, etc.)
        
        Returns:
            Session ID
        """
        if session_id is None:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        session_data = {
            "session_id": session_id,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "status": "running",
            "metadata": metadata or {},
            "stats": {
                "pages_processed": 0,
                "total_urls_found": 0,
                "listings_extracted": 0,
                "listings_saved": 0,
                "errors": 0,
                "duplicates_skipped": 0,
                "failed_urls": [],
            },
            "checkpoints": [],
            "last_checkpoint": None,
            "resumable": True,
            "error_history": [],
        }
        
        # Add to history
        self.sessions_history.append(session_data)
        self._save_sessions_history()
        
        # Set as current session
        self.current_session = session_data
        
        # Create session directory
        session_dir = self.sessions_dir / session_id
        session_dir.mkdir(exist_ok=True)
        
        print(f"Created session: {session_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session data by ID."""
        for session in self.sessions_history:
            if session["session_id"] == session_id:
                return session
        return None
    
    def get_current_session(self) -> Optional[Dict]:
        """Get current active session."""
        return self.current_session
    
    def update_session(self, **kwargs):
        """Update current session with new data."""
        if not self.current_session:
            return
        
        for key, value in kwargs.items():
            if key == "stats" and isinstance(value, dict):
                # Merge stats
                self.current_session["stats"].update(value)
            elif key == "error" and isinstance(value, dict):
                # Add to error history
                error_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "error_type": value.get("type", "unknown"),
                    "message": value.get("message", ""),
                    "details": value.get("details", {}),
                }
                self.current_session["error_history"].append(error_entry)
            else:
                self.current_session[key] = value
        
        # Save to history
        self._update_history()
    
    def _update_history(self):
        """Update session in history."""
        if not self.current_session:
            return
        
        for i, session in enumerate(self.sessions_history):
            if session["session_id"] == self.current_session["session_id"]:
                self.sessions_history[i] = self.current_session
                break
        
        self._save_sessions_history()
    
    def save_checkpoint(self, checkpoint_data: Dict) -> str:
        """
        Save a checkpoint for the current session.
        
        Args:
            checkpoint_data: Checkpoint data (pages processed, URLs seen, etc.)
        
        Returns:
            Checkpoint file path
        """
        if not self.current_session:
            raise ValueError("No active session to save checkpoint")
        
        checkpoint_id = f"checkpoint_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        checkpoint_file = self.checkpoints_dir / f"{self.current_session['session_id']}_{checkpoint_id}.json"
        
        checkpoint = {
            "checkpoint_id": checkpoint_id,
            "timestamp": datetime.now().isoformat(),
            "session_id": self.current_session["session_id"],
            "data": checkpoint_data,
            "stats": self.current_session["stats"].copy(),
        }
        
        try:
            with open(checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint, f, indent=2, ensure_ascii=False)
            
            # Update session
            checkpoint_info = {
                "checkpoint_id": checkpoint_id,
                "timestamp": checkpoint["timestamp"],
                "file": str(checkpoint_file),
            }
            self.current_session["checkpoints"].append(checkpoint_info)
            self.current_session["last_checkpoint"] = checkpoint_info
            
            self._update_history()
            
            print(f"Checkpoint saved: {checkpoint_id}")
            return str(checkpoint_file)
        except Exception as e:
            print(f"Error saving checkpoint: {e}")
            raise
    
    def load_checkpoint(self, checkpoint_file: str) -> Optional[Dict]:
        """Load checkpoint data from file."""
        checkpoint_path = Path(checkpoint_file)
        
        if not checkpoint_path.exists():
            return None
        
        try:
            with open(checkpoint_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading checkpoint: {e}")
            return None
    
    def get_latest_checkpoint(self, session_id: Optional[str] = None) -> Optional[Dict]:
        """Get the latest checkpoint for a session."""
        target_session_id = session_id or (self.current_session["session_id"] if self.current_session else None)
        
        if not target_session_id:
            return None
        
        session = self.get_session(target_session_id)
        if not session or not session.get("last_checkpoint"):
            return None
        
        checkpoint_file = session["last_checkpoint"]["file"]
        return self.load_checkpoint(checkpoint_file)
    
    def end_session(self, status: str = "completed", error: Optional[Dict] = None):
        """
        End the current session.
        
        Args:
            status: Session status ("completed", "error", "interrupted", "cancelled")
            error: Optional error information
        """
        if not self.current_session:
            return
        
        self.current_session["end_time"] = datetime.now().isoformat()
        self.current_session["status"] = status
        
        if error:
            self.update_session(error=error)
        
        self._update_history()
        print(f"Session ended: {self.current_session['session_id']} - Status: {status}")
    
    def list_sessions(self, status: Optional[str] = None) -> List[Dict]:
        """
        List all sessions, optionally filtered by status.
        
        Args:
            status: Optional status filter ("running", "completed", "error", etc.)
        
        Returns:
            List of session dictionaries
        """
        if status:
            return [s for s in self.sessions_history if s.get("status") == status]
        return self.sessions_history.copy()
    
    def get_resumable_sessions(self) -> List[Dict]:
        """Get all sessions that can be resumed."""
        return [s for s in self.sessions_history if s.get("resumable") and s.get("status") == "running"]
    
    def mark_resume_point(self, page_number: int, seen_urls: set, stats: Dict):
        """
        Mark a resume point for recovery.
        
        Args:
            page_number: Last successfully processed page
            seen_urls: Set of already processed URLs
            stats: Current statistics
        """
        checkpoint_data = {
            "last_page": page_number,
            "seen_urls": list(seen_urls),
            "stats": stats,
            "resume_point": True,
        }
        self.save_checkpoint(checkpoint_data)
    
    def get_resume_data(self, session_id: Optional[str] = None) -> Optional[Dict]:
        """
        Get data needed to resume a session.
        
        Args:
            session_id: Optional session ID (uses current session if None)
        
        Returns:
            Resume data dictionary
        """
        checkpoint = self.get_latest_checkpoint(session_id)
        if not checkpoint:
            return None
        
        return {
            "last_page": checkpoint["data"].get("last_page", 0),
            "seen_urls": set(checkpoint["data"].get("seen_urls", [])),
            "stats": checkpoint["data"].get("stats", {}),
        }


# Global session manager instance
_session_manager: Optional[SessionManager] = None


def get_session_manager(sessions_dir: str = "sessions") -> SessionManager:
    """Get or create global session manager instance."""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager(sessions_dir)
    return _session_manager


def reset_session_manager(sessions_dir: str = "sessions") -> SessionManager:
    """Reset and create a new session manager instance."""
    global _session_manager
    _session_manager = SessionManager(sessions_dir)
    return _session_manager

