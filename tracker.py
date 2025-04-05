import time
import win32gui
import win32process
import psutil
from datetime import datetime
from typing import Optional, Tuple
from logger import ActivityLogger
from rich.console import Console
from rich.live import Live
from rich.table import Table
import sys
from utils import Cache, setup_logging

logger = setup_logging()

class TimeTracker:
    def __init__(self):
        self.logger = ActivityLogger()
        self.console = Console()
        self.previous_window = None
        self.previous_process = None
        self.start_time = None
        self.blocklist = ["keepass.exe", "lastpass.exe"]
        self.window_cache = Cache()
        self.process_cache = Cache()
        self.batch_size = 10
        self.pending_logs = []
    
    def get_active_window_info(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Get information about the active window with caching
        Returns: (window_title, process_name)
        """
        try:
            window = win32gui.GetForegroundWindow()
            window_title = win32gui.GetWindowText(window)
            
            # Check cache first
            cached_info = self.window_cache.get(window)
            if cached_info:
                return cached_info
            
            if not window_title:
                _, pid = win32process.GetWindowThreadProcessId(window)
                process = psutil.Process(pid)
                window_title = process.name()
            else:
                _, pid = win32process.GetWindowThreadProcessId(window)
                process = psutil.Process(pid)
            
            process_name = process.name()
            
            # Cache the result
            self.window_cache.set(window, (window_title, process_name))
            return window_title, process_name
        except Exception as e:
            logger.error(f"Error getting window info: {e}")
            return None, None
    
    def create_status_table(self) -> Table:
        """Create a status table for display"""
        table = Table(show_header=True, header_style="bold magenta", box=None)
        table.add_column("Current Window", style="cyan")
        table.add_column("Process", style="green")
        table.add_column("Time Spent", style="yellow")
        return table
    
    def _log_pending_activities(self):
        """Log any pending activities in batch"""
        if self.pending_logs:
            self.logger.log_activities_batch(self.pending_logs)
            self.pending_logs.clear()
    
    def start_tracking(self):
        """Start tracking time with improved error handling and batching"""
        self.start_time = time.time()
        
        try:
            with Live(self.create_status_table(), refresh_per_second=1, vertical_overflow="visible") as live:
                while True:
                    current_title, current_process = self.get_active_window_info()
                    
                    if current_title is None or current_process is None:
                        time.sleep(1)
                        continue
                    
                    # Check for privacy mode
                    if current_process.lower() in self.blocklist:
                        current_title = "PRIVATE"
                        current_process = "PRIVATE"
                    
                    if current_title != self.previous_window:
                        if self.previous_window is not None:
                            end_time = time.time()
                            time_spent = end_time - self.start_time
                            
                            log_entry = {
                                "timestamp": datetime.fromtimestamp(self.start_time),
                                "window": self.previous_window,
                                "process": self.previous_process,
                                "time_spent_seconds": time_spent
                            }
                            
                            self.pending_logs.append(log_entry)
                            
                            # Log in batches to improve performance
                            if len(self.pending_logs) >= self.batch_size:
                                self._log_pending_activities()
                        
                        self.previous_window = current_title
                        self.previous_process = current_process
                        self.start_time = time.time()
                    
                    # Update the display
                    table = self.create_status_table()
                    current_time_spent = time.time() - self.start_time
                    table.add_row(
                        current_title[:50],  # Limit title length
                        current_process,
                        f"{current_time_spent:.1f}s"
                    )
                    live.update(table)
                    
                    time.sleep(1)
        except KeyboardInterrupt:
            # Save the last entry when stopping
            if self.previous_window is not None:
                end_time = time.time()
                time_spent = end_time - self.start_time
                
                log_entry = {
                    "timestamp": datetime.fromtimestamp(self.start_time),
                    "window": self.previous_window,
                    "process": self.previous_process,
                    "time_spent_seconds": time_spent
                }
                
                self.pending_logs.append(log_entry)
                self._log_pending_activities()
            
            self.console.print("\n[green]Tracking stopped. Data saved.[/green]")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Unexpected error in tracking: {e}")
            self._log_pending_activities()
            raise 