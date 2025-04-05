import sqlite3
from datetime import datetime, timedelta
import os
from typing import List, Tuple, Optional
from utils import setup_logging, backup_database

logger = setup_logging()

class ActivityLogger:
    def __init__(self, db_path=None):
        # Get the absolute path to the database file
        if db_path is None:
            self.db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'activity.db')
        else:
            self.db_path = db_path
        logger.debug(f"Using database at: {self.db_path}")
        
        # Only initialize if the database doesn't exist
        if not os.path.exists(self.db_path):
            logger.info("Database not found, initializing new database")
            self._init_db()
        else:
            logger.info("Using existing database")
        
        # Create backup with 7-day retention
        self._backup_database()
    
    def _backup_database(self):
        """Create a backup of the database with 7-day retention"""
        if backup_database(self.db_path, keep_days=7):
            logger.info("Database backup created successfully")
        else:
            logger.warning("Failed to create database backup")
    
    def _init_db(self):
        """Initialize the database with proper error handling"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE activity (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    window TEXT,
                    process TEXT,
                    time_spent_seconds REAL
                )
            ''')
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")
            raise
    
    def log_activity(self, log_entry: dict) -> bool:
        """
        Log an activity with proper error handling
        Returns True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO activity (timestamp, window, process, time_spent_seconds)
                VALUES (?, ?, ?, ?)
            ''', (
                log_entry['timestamp'],
                log_entry['window'],
                log_entry['process'],
                log_entry['time_spent_seconds']
            ))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error logging activity: {e}")
            return False
    
    def get_activities(self, start_date: datetime = None, end_date: datetime = None, limit: int = None) -> List[Tuple]:
        """
        Get activities from the database with optional date range and limit
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = 'SELECT * FROM activity'
            params = []
            
            if start_date or end_date:
                query += ' WHERE'
                if start_date:
                    query += ' timestamp >= ?'
                    params.append(start_date.strftime('%Y-%m-%d %H:%M:%S'))
                if end_date:
                    if start_date:
                        query += ' AND'
                    query += ' timestamp <= ?'
                    params.append(end_date.strftime('%Y-%m-%d %H:%M:%S'))
            
            query += ' ORDER BY timestamp DESC'
            
            if limit:
                query += ' LIMIT ?'
                params.append(limit)
            
            cursor.execute(query, params)
            activities = cursor.fetchall()
            conn.close()
            
            logger.debug(f"Retrieved {len(activities)} activities from database")
            return activities
        except sqlite3.Error as e:
            logger.error(f"Error getting activities: {e}")
            return []
    
    def log_activities_batch(self, log_entries: List[dict]) -> bool:
        """
        Log multiple activities in a single transaction
        Returns True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Prepare the data for batch insertion
            data = [
                (
                    entry["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
                    entry["window"],
                    entry["process"],
                    entry["time_spent_seconds"]
                )
                for entry in log_entries
            ]
            
            cursor.executemany('''
                INSERT INTO activity (timestamp, window, process, time_spent_seconds)
                VALUES (?, ?, ?, ?)
            ''', data)
            
            conn.commit()
            conn.close()
            logger.debug(f"Successfully logged {len(log_entries)} activities")
            return True
        except sqlite3.Error as e:
            logger.error(f"Database error while batch logging activities: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error while batch logging activities: {e}")
            return False
    
    def cleanup_old_data(self, days_to_keep: int = 30) -> bool:
        """
        Remove old data from the database
        Returns True if successful, False otherwise
        """
        try:
            cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).strftime("%Y-%m-%d %H:%M:%S")
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM activity WHERE timestamp < ?", (cutoff_date,))
            deleted_count = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            logger.info(f"Cleaned up {deleted_count} old records")
            return True
        except sqlite3.Error as e:
            logger.error(f"Database error while cleaning up old data: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error while cleaning up old data: {e}")
            return False 