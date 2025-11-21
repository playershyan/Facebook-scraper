"""
Session viewer utility - view and manage scraping sessions.
Similar to browser history - accessible anytime.
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional


class SessionViewer:
    """View and manage scraping sessions."""
    
    def __init__(self, sessions_dir: str = "sessions"):
        """
        Initialize session viewer.
        
        Args:
            sessions_dir: Directory containing sessions
        """
        self.sessions_dir = Path(sessions_dir)
        self.sessions_file = self.sessions_dir / "sessions_history.json"
    
    def load_sessions(self) -> List[Dict]:
        """Load all sessions from history."""
        if not self.sessions_file.exists():
            return []
        
        try:
            with open(self.sessions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading sessions: {e}")
            return []
    
    def list_sessions(self, status: Optional[str] = None) -> List[Dict]:
        """
        List all sessions, optionally filtered by status.
        
        Args:
            status: Optional status filter
        
        Returns:
            List of session dictionaries
        """
        sessions = self.load_sessions()
        
        if status:
            return [s for s in sessions if s.get("status") == status]
        
        return sessions
    
    def get_session_details(self, session_id: str) -> Optional[Dict]:
        """Get detailed information about a session."""
        sessions = self.load_sessions()
        
        for session in sessions:
            if session["session_id"] == session_id:
                return session
        
        return None
    
    def print_sessions_summary(self):
        """Print a summary of all sessions."""
        sessions = self.load_sessions()
        
        if not sessions:
            print("No sessions found.")
            return
        
        print("=" * 80)
        print("SESSION HISTORY SUMMARY")
        print("=" * 80)
        print(f"Total sessions: {len(sessions)}\n")
        
        # Group by status
        by_status = {}
        for session in sessions:
            status = session.get("status", "unknown")
            by_status[status] = by_status.get(status, 0) + 1
        
        print("Sessions by status:")
        for status, count in sorted(by_status.items()):
            print(f"  {status}: {count}")
        print()
        
        # List all sessions
        print("All Sessions:")
        print("-" * 80)
        
        for i, session in enumerate(sessions, 1):
            session_id = session["session_id"]
            start_time = session.get("start_time", "Unknown")
            end_time = session.get("end_time", "In progress")
            status = session.get("status", "unknown")
            stats = session.get("stats", {})
            
            print(f"\n{i}. Session: {session_id}")
            print(f"   Status: {status}")
            print(f"   Start: {start_time}")
            print(f"   End: {end_time}")
            print(f"   Pages processed: {stats.get('pages_processed', 0)}")
            print(f"   Listings extracted: {stats.get('listings_extracted', 0)}")
            print(f"   Errors: {stats.get('errors', 0)}")
            
            checkpoints = session.get("checkpoints", [])
            if checkpoints:
                last_checkpoint = session.get("last_checkpoint")
                if last_checkpoint:
                    print(f"   Last checkpoint: {last_checkpoint.get('timestamp', 'Unknown')}")
        
        print("\n" + "=" * 80)
    
    def get_resumable_sessions(self) -> List[Dict]:
        """Get sessions that can be resumed."""
        sessions = self.load_sessions()
        return [
            s for s in sessions
            if s.get("status") == "running" and s.get("resumable", True)
        ]
    
    def print_resume_instructions(self, session_id: str):
        """Print instructions for resuming a session."""
        session = self.get_session_details(session_id)
        
        if not session:
            print(f"Session {session_id} not found.")
            return
        
        if session.get("status") != "running":
            print(f"Session {session_id} cannot be resumed (status: {session.get('status')})")
            return
        
        last_checkpoint = session.get("last_checkpoint")
        if not last_checkpoint:
            print(f"Session {session_id} has no checkpoint to resume from.")
            return
        
        print("=" * 80)
        print(f"RESUME INSTRUCTIONS FOR SESSION: {session_id}")
        print("=" * 80)
        print(f"\nTo resume this session, run:")
        print(f"\n  python riyasewana_main_robust.py --resume {session_id}\n")
        print(f"Session details:")
        print(f"  Start time: {session.get('start_time')}")
        print(f"  Last checkpoint: {last_checkpoint.get('timestamp')}")
        print(f"  Progress: {session.get('stats', {}).get('pages_processed', 0)} pages processed")
        print("\n" + "=" * 80)


def main():
    """CLI for viewing sessions."""
    import argparse
    
    parser = argparse.ArgumentParser(description='View and manage scraping sessions')
    parser.add_argument('--list', action='store_true', help='List all sessions')
    parser.add_argument('--resumable', action='store_true', help='List resumable sessions')
    parser.add_argument('--session', type=str, help='Show details for specific session')
    parser.add_argument('--resume-instructions', type=str, help='Show resume instructions for session')
    
    args = parser.parse_args()
    
    viewer = SessionViewer()
    
    if args.list:
        viewer.print_sessions_summary()
    elif args.resumable:
        resumable = viewer.get_resumable_sessions()
        print(f"\nResumable sessions: {len(resumable)}\n")
        for session in resumable:
            print(f"  {session['session_id']} - {session.get('stats', {}).get('pages_processed', 0)} pages processed")
    elif args.session:
        session = viewer.get_session_details(args.session)
        if session:
            print(json.dumps(session, indent=2, ensure_ascii=False))
        else:
            print(f"Session {args.session} not found.")
    elif args.resume_instructions:
        viewer.print_resume_instructions(args.resume_instructions)
    else:
        viewer.print_sessions_summary()


if __name__ == "__main__":
    main()

