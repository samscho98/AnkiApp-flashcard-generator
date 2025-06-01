"""
Generic History Manager for Language Learning Flashcard Generator
Tracks learning progress, completed sessions, and generated files for any language
"""

import json
import os
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
import logging

logger = logging.getLogger(__name__)


class HistoryManager:
    """Manages learning progress and history tracking for language learning"""
    
    def __init__(self, history_file: str = "history.json"):
        """
        Initialize History Manager
        
        Args:
            history_file: Path to history JSON file
        """
        self.history_file = Path(history_file)
        self.history_data = self._load_history()
        
    def _load_history(self) -> Dict:
        """
        Load history data from JSON file
        
        Returns:
            Dictionary with history data
        """
        default_history = {
            "created_date": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "app_version": "1.0.0",
            "study_sessions": [],  # List of study session records
            "completed_files": [],  # List of completed file paths
            "generated_files": [],  # List of generated CSV files with metadata
            "current_targets": {  # Current study targets
                "target_language": "",
                "current_file": "",
                "current_section": "",
                "progress_percentage": 0.0
            },
            "statistics": {
                "total_items_learned": 0,
                "total_study_time": 0,  # minutes
                "study_streak": 0,  # days of consecutive study
                "items_per_session": {},  # Session ID -> item count
                "session_durations": {},  # Session ID -> duration in minutes
                "difficulty_ratings": {},  # Item -> difficulty (1-5)
                "language_progress": {}  # Language -> progress stats
            },
            "preferences": {
                "daily_target": 20,
                "reminder_enabled": True,
                "reminder_time": "09:00",
                "preferred_content_types": ["vocabulary"]
            },
            "bookmarks": [],  # Bookmarked items for review
            "achievements": []  # Learning achievements/milestones
        }
        
        if not self.history_file.exists():
            logger.info("Creating new history file")
            self._save_history(default_history)
            return default_history
        
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
                # Update last_updated timestamp
                history["last_updated"] = datetime.now().isoformat()
                # Merge with defaults to ensure all keys exist
                merged_history = self._merge_with_defaults(default_history, history)
                return merged_history
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"Error loading history file: {e}")
            logger.info("Creating new history file")
            self._save_history(default_history)
            return default_history
    
    def _merge_with_defaults(self, defaults: Dict, loaded: Dict) -> Dict:
        """Merge loaded history with defaults to ensure all keys exist"""
        merged = defaults.copy()
        
        for key, value in loaded.items():
            if key in merged and isinstance(value, dict) and isinstance(merged[key], dict):
                merged[key].update(value)
            else:
                merged[key] = value
        
        return merged
    
    def _save_history(self, history_data: Optional[Dict] = None) -> bool:
        """
        Save history data to JSON file
        
        Args:
            history_data: History data to save (uses self.history_data if None)
            
        Returns:
            True if successful, False otherwise
        """
        if history_data is None:
            history_data = self.history_data
        
        # Update timestamp
        history_data["last_updated"] = datetime.now().isoformat()
        
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Error saving history file: {e}")
            return False
    
    def start_study_session(self, target_language: str = "", content_type: str = "vocabulary", 
                           source_file: str = "") -> str:
        """
        Start a new study session
        
        Args:
            target_language: Language being studied
            content_type: Type of content (vocabulary, grammar, etc.)
            source_file: Source file being studied
            
        Returns:
            Session ID
        """
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        session_data = {
            "session_id": session_id,
            "start_time": datetime.now().isoformat(),
            "target_language": target_language,
            "content_type": content_type,
            "source_file": source_file,
            "items_studied": 0,
            "items_learned": 0,
            "status": "active"
        }
        
        self.history_data["study_sessions"].append(session_data)
        
        # Update current targets
        self.history_data["current_targets"].update({
            "target_language": target_language,
            "current_file": source_file,
            "current_session": session_id
        })
        
        self._save_history()
        logger.info(f"Started study session: {session_id}")
        return session_id
    
    def end_study_session(self, session_id: str, items_studied: int = 0, 
                         items_learned: int = 0) -> bool:
        """
        End a study session
        
        Args:
            session_id: Session identifier
            items_studied: Number of items studied
            items_learned: Number of items learned/mastered
            
        Returns:
            True if successful
        """
        # Find the session
        session = None
        for s in self.history_data["study_sessions"]:
            if s["session_id"] == session_id:
                session = s
                break
        
        if not session:
            logger.error(f"Session not found: {session_id}")
            return False
        
        # Update session data
        end_time = datetime.now()
        start_time = datetime.fromisoformat(session["start_time"])
        duration_minutes = (end_time - start_time).total_seconds() / 60
        
        session.update({
            "end_time": end_time.isoformat(),
            "duration_minutes": round(duration_minutes, 1),
            "items_studied": items_studied,
            "items_learned": items_learned,
            "status": "completed"
        })
        
        # Update statistics
        self.history_data["statistics"]["total_items_learned"] += items_learned
        self.history_data["statistics"]["total_study_time"] += round(duration_minutes, 1)
        self.history_data["statistics"]["items_per_session"][session_id] = items_studied
        self.history_data["statistics"]["session_durations"][session_id] = round(duration_minutes, 1)
        
        # Update language progress
        target_lang = session.get("target_language", "unknown")
        if target_lang:
            lang_stats = self.history_data["statistics"]["language_progress"].setdefault(target_lang, {
                "total_items": 0,
                "total_time": 0,
                "sessions": 0
            })
            lang_stats["total_items"] += items_learned
            lang_stats["total_time"] += round(duration_minutes, 1)
            lang_stats["sessions"] += 1
        
        # Update study streak
        self._update_study_streak()
        
        # Check for achievements
        self._check_achievements(items_learned, duration_minutes)
        
        self._save_history()
        logger.info(f"Ended study session: {session_id} ({items_learned} items learned)")
        return True
    
    def _update_study_streak(self) -> None:
        """Update the study streak based on recent sessions"""
        try:
            today = date.today()
            
            # Get unique study dates from recent sessions
            study_dates = set()
            for session in self.history_data["study_sessions"]:
                if session.get("status") == "completed" and session.get("end_time"):
                    try:
                        session_date = datetime.fromisoformat(session["end_time"]).date()
                        study_dates.add(session_date)
                    except (ValueError, TypeError):
                        continue
            
            # Calculate streak
            streak = 0
            current_date = today
            
            while current_date in study_dates:
                streak += 1
                # Safely subtract one day
                try:
                    from datetime import timedelta
                    current_date = current_date - timedelta(days=1)
                except Exception as e:
                    logger.warning(f"Error calculating streak date: {e}")
                    break
            
            self.history_data["statistics"]["study_streak"] = streak
            
        except Exception as e:
            logger.error(f"Error updating study streak: {e}")
            # Set a safe default
            self.history_data["statistics"]["study_streak"] = 0
    
    def _check_achievements(self, items_learned: int, duration_minutes: float) -> None:
        """Check and award achievements"""
        achievements = self.history_data["achievements"]
        total_items = self.history_data["statistics"]["total_items_learned"]
        streak = self.history_data["statistics"]["study_streak"]
        
        # Achievement definitions
        achievement_checks = [
            (total_items >= 10, "first_10", "First 10 Items", "Learned your first 10 items!"),
            (total_items >= 50, "half_century", "Half Century", "Learned 50 items!"),
            (total_items >= 100, "century", "Century", "Learned 100 items!"),
            (total_items >= 500, "five_hundred", "Five Hundred", "Learned 500 items!"),
            (streak >= 3, "three_day_streak", "Three Day Streak", "Studied for 3 consecutive days!"),
            (streak >= 7, "week_streak", "Week Streak", "Studied for a whole week!"),
            (streak >= 30, "month_streak", "Month Streak", "Studied for 30 consecutive days!"),
            (duration_minutes >= 60, "hour_session", "Hour Session", "Studied for a full hour!"),
            (items_learned >= 50, "big_session", "Big Session", "Learned 50+ items in one session!")
        ]
        
        # Check each achievement
        for condition, achievement_id, title, description in achievement_checks:
            if condition and not any(a.get("id") == achievement_id for a in achievements):
                achievement = {
                    "id": achievement_id,
                    "title": title,
                    "description": description,
                    "earned_date": datetime.now().isoformat(),
                    "category": "learning"
                }
                achievements.append(achievement)
                logger.info(f"Achievement earned: {title}")
    
    def mark_file_completed(self, filepath: str, items_count: int = 0) -> bool:
        """
        Mark a file as completed
        
        Args:
            filepath: Path to completed file
            items_count: Number of items in the file
            
        Returns:
            True if successful
        """
        if filepath not in self.history_data["completed_files"]:
            self.history_data["completed_files"].append({
                "filepath": filepath,
                "completed_date": datetime.now().isoformat(),
                "items_count": items_count
            })
            
            logger.info(f"Marked file as completed: {filepath}")
            return self._save_history()
        
        return True
    
    def is_file_completed(self, filepath: str) -> bool:
        """
        Check if a file is marked as completed
        
        Args:
            filepath: Path to file
            
        Returns:
            True if completed
        """
        completed_files = self.history_data.get("completed_files", [])
        
        # Handle both old format (strings) and new format (dicts)
        for item in completed_files:
            if isinstance(item, str):
                if item == filepath:
                    return True
            elif isinstance(item, dict):
                if item.get("filepath") == filepath:
                    return True
        
        return False
    
    def add_generated_file(self, filepath: str, source_file: str = "", 
                          content_type: str = "vocabulary", item_count: int = 0) -> bool:
        """
        Record a generated CSV file
        
        Args:
            filepath: Path to generated file
            source_file: Source JSON file used
            content_type: Type of content generated
            item_count: Number of items in the file
            
        Returns:
            True if successful
        """
        file_entry = {
            "filepath": filepath,
            "filename": os.path.basename(filepath),
            "generated_date": datetime.now().isoformat(),
            "source_file": source_file,
            "content_type": content_type,
            "item_count": item_count,
            "file_size": os.path.getsize(filepath) if os.path.exists(filepath) else 0
        }
        
        self.history_data["generated_files"].append(file_entry)
        return self._save_history()
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """
        Get a comprehensive progress summary
        
        Returns:
            Dictionary with progress information
        """
        stats = self.history_data["statistics"]
        sessions = self.history_data["study_sessions"]
        completed_sessions = [s for s in sessions if s.get("status") == "completed"]
        
        # Calculate averages
        avg_items_per_session = 0
        avg_session_duration = 0
        if completed_sessions:
            total_items = sum(s.get("items_learned", 0) for s in completed_sessions)
            total_duration = sum(s.get("duration_minutes", 0) for s in completed_sessions)
            avg_items_per_session = total_items / len(completed_sessions)
            avg_session_duration = total_duration / len(completed_sessions)
        
        return {
            "total_items_learned": stats.get("total_items_learned", 0),
            "total_study_time_minutes": stats.get("total_study_time", 0),
            "total_study_time_hours": round(stats.get("total_study_time", 0) / 60, 1),
            "study_streak": stats.get("study_streak", 0),
            "total_sessions": len(completed_sessions),
            "average_items_per_session": round(avg_items_per_session, 1),
            "average_session_duration": round(avg_session_duration, 1),
            "completed_files_count": len(self.history_data.get("completed_files", [])),
            "generated_files_count": len(self.history_data.get("generated_files", [])),
            "achievements_count": len(self.history_data.get("achievements", [])),
            "languages_studied": list(stats.get("language_progress", {}).keys()),
            "last_updated": self.history_data.get("last_updated")
        }
    
    def get_language_progress(self, language: str) -> Dict[str, Any]:
        """
        Get progress information for a specific language
        
        Args:
            language: Target language
            
        Returns:
            Dictionary with language progress
        """
        lang_stats = self.history_data["statistics"]["language_progress"].get(language, {})
        
        # Get sessions for this language
        language_sessions = [
            s for s in self.history_data["study_sessions"] 
            if s.get("target_language", "").lower() == language.lower() 
            and s.get("status") == "completed"
        ]
        
        # Calculate recent activity (last 7 days)
        recent_activity = []
        seven_days_ago = datetime.now().replace(day=datetime.now().day - 7)
        
        for session in language_sessions:
            if session.get("end_time"):
                try:
                    session_time = datetime.fromisoformat(session["end_time"])
                    if session_time >= seven_days_ago:
                        recent_activity.append(session)
                except ValueError:
                    continue
        
        recent_items = sum(s.get("items_learned", 0) for s in recent_activity)
        recent_time = sum(s.get("duration_minutes", 0) for s in recent_activity)
        
        return {
            "language": language,
            "total_items": lang_stats.get("total_items", 0),
            "total_time_minutes": lang_stats.get("total_time", 0),
            "total_sessions": lang_stats.get("sessions", 0),
            "recent_items_7_days": recent_items,
            "recent_time_7_days": round(recent_time, 1),
            "recent_sessions_7_days": len(recent_activity),
            "average_items_per_session": round(lang_stats.get("total_items", 0) / max(lang_stats.get("sessions", 1), 1), 1)
        }
    
    def get_recent_sessions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent study sessions
        
        Args:
            limit: Maximum number of sessions to return
            
        Returns:
            List of recent sessions
        """
        sessions = self.history_data["study_sessions"]
        # Sort by start time (most recent first)
        sorted_sessions = sorted(
            sessions, 
            key=lambda x: x.get("start_time", ""), 
            reverse=True
        )
        
        return sorted_sessions[:limit]
    
    def add_bookmark(self, item_data: Dict[str, Any], notes: str = "") -> bool:
        """
        Add an item to bookmarks for later review
        
        Args:
            item_data: The learning item to bookmark
            notes: Optional notes about why it's bookmarked
            
        Returns:
            True if successful
        """
        bookmark = {
            "id": f"bookmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "item_data": item_data,
            "notes": notes,
            "bookmarked_date": datetime.now().isoformat(),
            "review_count": 0,
            "last_reviewed": None
        }
        
        self.history_data["bookmarks"].append(bookmark)
        return self._save_history()
    
    def get_bookmarks(self) -> List[Dict[str, Any]]:
        """Get all bookmarked items"""
        return self.history_data.get("bookmarks", [])
    
    def remove_bookmark(self, bookmark_id: str) -> bool:
        """Remove a bookmark"""
        bookmarks = self.history_data.get("bookmarks", [])
        self.history_data["bookmarks"] = [b for b in bookmarks if b.get("id") != bookmark_id]
        return self._save_history()
    
    def set_daily_target(self, target: int) -> bool:
        """Set daily learning target"""
        self.history_data["preferences"]["daily_target"] = target
        return self._save_history()
    
    def get_daily_target(self) -> int:
        """Get daily learning target"""
        return self.history_data["preferences"].get("daily_target", 20)
    
    def get_today_progress(self) -> Dict[str, Any]:
        """
        Get today's progress towards daily target
        
        Returns:
            Dictionary with today's progress
        """
        today = date.today()
        today_sessions = []
        
        for session in self.history_data["study_sessions"]:
            if session.get("status") == "completed" and session.get("end_time"):
                try:
                    session_date = datetime.fromisoformat(session["end_time"]).date()
                    if session_date == today:
                        today_sessions.append(session)
                except ValueError:
                    continue
        
        items_learned_today = sum(s.get("items_learned", 0) for s in today_sessions)
        time_studied_today = sum(s.get("duration_minutes", 0) for s in today_sessions)
        daily_target = self.get_daily_target()
        
        return {
            "date": today.isoformat(),
            "items_learned": items_learned_today,
            "time_studied_minutes": round(time_studied_today, 1),
            "sessions_completed": len(today_sessions),
            "daily_target": daily_target,
            "target_progress": round((items_learned_today / daily_target) * 100, 1) if daily_target > 0 else 0,
            "target_met": items_learned_today >= daily_target
        }
    
    def get_achievements(self) -> List[Dict[str, Any]]:
        """Get all earned achievements"""
        return self.history_data.get("achievements", [])
    
    def export_progress_csv(self, output_path: str) -> bool:
        """
        Export progress data to CSV for analysis
        
        Args:
            output_path: Path for the CSV file
            
        Returns:
            True if successful
        """
        try:
            import csv
            
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'Session_ID', 'Date', 'Target_Language', 'Content_Type', 
                    'Duration_Minutes', 'Items_Studied', 'Items_Learned', 'Source_File'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for session in self.history_data["study_sessions"]:
                    if session.get("status") == "completed":
                        try:
                            session_date = datetime.fromisoformat(session.get("start_time", "")).date()
                        except (ValueError, TypeError):
                            session_date = ""
                        
                        writer.writerow({
                            'Session_ID': session.get("session_id", ""),
                            'Date': session_date,
                            'Target_Language': session.get("target_language", ""),
                            'Content_Type': session.get("content_type", ""),
                            'Duration_Minutes': session.get("duration_minutes", 0),
                            'Items_Studied': session.get("items_studied", 0),
                            'Items_Learned': session.get("items_learned", 0),
                            'Source_File': session.get("source_file", "")
                        })
            
            logger.info(f"Progress exported to: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting progress: {e}")
            return False
    
    def reset_progress(self, confirm: bool = False) -> bool:
        """
        Reset all progress (use with caution!)
        
        Args:
            confirm: Must be True to actually reset
            
        Returns:
            True if successful
        """
        if not confirm:
            logger.warning("Reset not confirmed - no action taken")
            return False
        
        logger.warning("Resetting all progress!")
        
        # Keep preferences and some basic info, reset progress
        app_info = {
            "created_date": self.history_data.get("created_date"),
            "app_version": self.history_data.get("app_version"),
            "reset_date": datetime.now().isoformat()
        }
        preferences = self.history_data.get("preferences", {})
        
        # Create fresh history but keep preferences
        fresh_history = self._load_history()
        fresh_history.update(app_info)
        fresh_history["preferences"] = preferences
        
        self.history_data = fresh_history
        return self._save_history()
    
    def get_study_statistics(self, days: int = 30) -> Dict[str, Any]:
        """
        Get study statistics for the last N days
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary with statistics
        """
        cutoff_date = datetime.now().replace(day=datetime.now().day - days)
        recent_sessions = []
        
        for session in self.history_data["study_sessions"]:
            if session.get("status") == "completed" and session.get("end_time"):
                try:
                    session_time = datetime.fromisoformat(session["end_time"])
                    if session_time >= cutoff_date:
                        recent_sessions.append(session)
                except ValueError:
                    continue
        
        if not recent_sessions:
            return {
                "period_days": days,
                "sessions": 0,
                "total_items": 0,
                "total_time": 0,
                "average_per_day": 0,
                "most_active_day": None,
                "languages": []
            }
        
        # Calculate statistics
        total_items = sum(s.get("items_learned", 0) for s in recent_sessions)
        total_time = sum(s.get("duration_minutes", 0) for s in recent_sessions)
        
        # Group by language
        language_stats = {}
        for session in recent_sessions:
            lang = session.get("target_language", "unknown")
            if lang not in language_stats:
                language_stats[lang] = {"sessions": 0, "items": 0, "time": 0}
            language_stats[lang]["sessions"] += 1
            language_stats[lang]["items"] += session.get("items_learned", 0)
            language_stats[lang]["time"] += session.get("duration_minutes", 0)
        
        # Group by day to find most active day
        daily_activity = {}
        for session in recent_sessions:
            try:
                day = datetime.fromisoformat(session["end_time"]).date()
                if day not in daily_activity:
                    daily_activity[day] = {"sessions": 0, "items": 0}
                daily_activity[day]["sessions"] += 1
                daily_activity[day]["items"] += session.get("items_learned", 0)
            except ValueError:
                continue
        
        most_active_day = None
        if daily_activity:
            most_active_day = max(daily_activity.keys(), key=lambda d: daily_activity[d]["items"])
        
        return {
            "period_days": days,
            "sessions": len(recent_sessions),
            "total_items": total_items,
            "total_time_minutes": round(total_time, 1),
            "average_items_per_day": round(total_items / days, 1),
            "average_session_duration": round(total_time / len(recent_sessions), 1) if recent_sessions else 0,
            "most_active_day": most_active_day.isoformat() if most_active_day else None,
            "languages": [
                {
                    "language": lang,
                    "sessions": stats["sessions"],
                    "items": stats["items"],
                    "time_minutes": round(stats["time"], 1)
                }
                for lang, stats in language_stats.items()
            ]
        }


# Example usage and testing
if __name__ == "__main__":
    # Create history manager
    history = HistoryManager()
    
    # Start a study session
    session_id = history.start_study_session("french", "vocabulary", "french_basics.json")
    print(f"Started session: {session_id}")
    
    # Simulate study session
    import time
    time.sleep(2)  # Simulate 2 seconds of study
    
    # End session
    history.end_study_session(session_id, items_studied=15, items_learned=12)
    
    # Get progress summary
    summary = history.get_progress_summary()
    print(f"Progress summary: {summary}")
    
    # Get today's progress
    today_progress = history.get_today_progress()
    print(f"Today's progress: {today_progress}")
    
    # Get study statistics
    stats = history.get_study_statistics(30)
    print(f"30-day statistics: {stats}")
    
    # Add a bookmark
    sample_item = {
        "target": "bonjour",
        "native": "hello",
        "example": "Bonjour, comment allez-vous?"
    }
    history.add_bookmark(sample_item, "Need to practice pronunciation")
    
    # Get achievements
    achievements = history.get_achievements()
    print(f"Achievements: {achievements}")
    
    # Mark a file as completed
    history.mark_file_completed("french_basics.json", 25)
    
    # Get language progress
    french_progress = history.get_language_progress("french")
    print(f"French progress: {french_progress}")