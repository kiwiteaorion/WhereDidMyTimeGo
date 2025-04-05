import logging
import os
from datetime import datetime, timedelta
import shutil

logger = logging.getLogger(__name__)

def setup_logging():
    """Set up logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def backup_database(db_path: str, keep_days: int = 7) -> bool:
    """
    Create a backup of the database with timestamp and clean up old backups
    Returns True if successful, False otherwise
    """
    try:
        # Create backups directory if it doesn't exist
        backup_dir = os.path.join(os.path.dirname(db_path), 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'activity_backup_{timestamp}.db'
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # Create the backup
        shutil.copy2(db_path, backup_path)
        logger.info(f"Created backup: {backup_filename}")
        
        # Clean up old backups
        cleanup_old_backups(backup_dir, keep_days)
        
        return True
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        return False

def cleanup_old_backups(backup_dir: str, keep_days: int):
    """
    Remove backups older than keep_days
    """
    try:
        now = datetime.now()
        for filename in os.listdir(backup_dir):
            if filename.startswith('activity_backup_') and filename.endswith('.db'):
                # Extract timestamp from filename
                try:
                    timestamp_str = filename.split('_')[2].split('.')[0]
                    backup_date = datetime.strptime(timestamp_str, '%Y%m%d')
                    
                    # Calculate age of backup
                    age = now - backup_date
                    
                    # Remove if older than keep_days
                    if age.days > keep_days:
                        backup_path = os.path.join(backup_dir, filename)
                        os.remove(backup_path)
                        logger.info(f"Removed old backup: {filename}")
                except (ValueError, IndexError):
                    # Skip files with invalid timestamps
                    continue
    except Exception as e:
        logger.error(f"Error cleaning up old backups: {e}")

class Cache:
    """Simple cache implementation for window and process information"""
    def __init__(self, max_size=1000):
        self.cache = {}
        self.max_size = max_size
    
    def get(self, key):
        return self.cache.get(key)
    
    def set(self, key, value):
        if len(self.cache) >= self.max_size:
            # Remove oldest item
            self.cache.pop(next(iter(self.cache)))
        self.cache[key] = value
    
    def clear(self):
        self.cache.clear() 