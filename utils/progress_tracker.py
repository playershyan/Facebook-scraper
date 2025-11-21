"""
Progress tracking utility for the scraper.
Writes progress updates to a JSON file that can be read by the dashboard.
"""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional


class ProgressTracker:
    """Tracks and saves progress for the scraper."""
    
    def __init__(self, progress_file: str = "scraper_progress.json"):
        """
        Initialize the progress tracker.
        
        Args:
            progress_file: Path to JSON file where progress is saved
        """
        self.progress_file = progress_file
        self.start_time = datetime.now()
        self.progress = {
            "status": "initializing",
            "start_time": self.start_time.isoformat(),
            "last_update": datetime.now().isoformat(),
            "total_work": {
                "unit": "pages",
                "total": 0,
                "completed": 0,
                "remaining": 0,
                "percentage": 0.0,
            },
            "listings": {
                "found": 0,
                "extracted": 0,
                "saved": 0,
                "duplicates_skipped": 0,
                "failed": 0,
            },
            "workers": {},
            "estimated_time": {
                "elapsed_seconds": 0,
                "remaining_seconds": 0,
                "estimated_completion": None,
                "rate_per_minute": 0.0,
            },
            "errors": 0,
        }
        self._save_progress()
    
    def set_total_work(self, total: int, unit: str = "pages"):
        """
        Set the total amount of work to be done.
        
        Args:
            total: Total amount of work
            unit: Unit of measurement (e.g., "pages", "items", "urls")
        """
        self.progress["total_work"]["total"] = total
        self.progress["total_work"]["unit"] = unit
        self.progress["total_work"]["remaining"] = total
        self._save_progress()
    
    def update_work_completed(self, completed: int):
        """
        Update the amount of work completed.
        
        Args:
            completed: Number of completed work units
        """
        self.progress["total_work"]["completed"] = completed
        total = self.progress["total_work"]["total"]
        if total > 0:
            self.progress["total_work"]["remaining"] = max(0, total - completed)
            self.progress["total_work"]["percentage"] = (completed / total) * 100.0
        self._update_time_estimates()
        self._save_progress()
    
    def update_listings(self, **kwargs):
        """
        Update listing statistics.
        
        Args:
            found: Number of listing URLs found
            extracted: Number of listings extracted
            saved: Number of listings saved
            duplicates_skipped: Number of duplicates skipped
            failed: Number of failed extractions
        """
        for key, value in kwargs.items():
            if key in self.progress["listings"]:
                if isinstance(value, int):
                    self.progress["listings"][key] += value
                else:
                    self.progress["listings"][key] = value
        self._save_progress()
    
    def update_worker(self, worker_id: int, **kwargs):
        """
        Update worker-specific statistics.
        
        Args:
            worker_id: Worker identifier
            **kwargs: Worker statistics (pages_processed, listings_extracted, etc.)
        """
        if worker_id not in self.progress["workers"]:
            self.progress["workers"][worker_id] = {
                "pages_processed": 0,
                "urls_found": 0,
                "listings_extracted": 0,
                "errors": 0,
                "status": "running",
            }
        
        for key, value in kwargs.items():
            if key in self.progress["workers"][worker_id]:
                if isinstance(value, int) and key != "status":
                    self.progress["workers"][worker_id][key] += value
                else:
                    self.progress["workers"][worker_id][key] = value
        
        self._save_progress()
    
    def set_status(self, status: str):
        """
        Set the overall status.
        
        Args:
            status: Status string (e.g., "running", "completed", "error", "paused")
        """
        self.progress["status"] = status
        self._save_progress()
    
    def update_errors(self, count: int = 1):
        """Increment error count."""
        self.progress["errors"] += count
        self._save_progress()
    
    def _update_time_estimates(self):
        """Calculate time estimates based on current progress."""
        now = datetime.now()
        elapsed = (now - self.start_time).total_seconds()
        self.progress["estimated_time"]["elapsed_seconds"] = elapsed
        
        completed = self.progress["total_work"]["completed"]
        remaining = self.progress["total_work"]["remaining"]
        
        if completed > 0 and remaining > 0:
            # Calculate rate (work units per minute)
            rate_per_minute = (completed / elapsed) * 60.0
            self.progress["estimated_time"]["rate_per_minute"] = round(rate_per_minute, 2)
            
            # Estimate remaining time
            if rate_per_minute > 0:
                remaining_minutes = remaining / rate_per_minute
                remaining_seconds = remaining_minutes * 60
                self.progress["estimated_time"]["remaining_seconds"] = int(remaining_seconds)
                
                # Estimated completion time
                estimated_completion = now + timedelta(seconds=remaining_seconds)
                self.progress["estimated_time"]["estimated_completion"] = estimated_completion.isoformat()
            else:
                self.progress["estimated_time"]["remaining_seconds"] = 0
                self.progress["estimated_time"]["estimated_completion"] = None
        else:
            self.progress["estimated_time"]["rate_per_minute"] = 0.0
            self.progress["estimated_time"]["remaining_seconds"] = 0
            self.progress["estimated_time"]["estimated_completion"] = None
    
    def _save_progress(self):
        """Save progress to JSON file."""
        self.progress["last_update"] = datetime.now().isoformat()
        try:
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(self.progress, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save progress: {e}")
    
    def get_progress(self) -> Dict:
        """Get current progress dictionary."""
        self._update_time_estimates()
        return self.progress
    
    def format_time(self, seconds: float) -> str:
        """
        Format seconds into human-readable time string.
        
        Args:
            seconds: Number of seconds
        
        Returns:
            Formatted time string (e.g., "2h 15m 30s")
        """
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            return f"{hours}h {minutes}m {secs}s"


# Global progress tracker instance
_progress_tracker: Optional[ProgressTracker] = None


def get_progress_tracker(progress_file: str = "scraper_progress.json") -> ProgressTracker:
    """
    Get or create the global progress tracker instance.
    
    Args:
        progress_file: Path to progress JSON file
    
    Returns:
        ProgressTracker instance
    """
    global _progress_tracker
    if _progress_tracker is None:
        _progress_tracker = ProgressTracker(progress_file)
    return _progress_tracker


def reset_progress_tracker(progress_file: str = "scraper_progress.json") -> ProgressTracker:
    """
    Reset and create a new progress tracker instance.
    
    Args:
        progress_file: Path to progress JSON file
    
    Returns:
        New ProgressTracker instance
    """
    global _progress_tracker
    _progress_tracker = ProgressTracker(progress_file)
    return _progress_tracker

