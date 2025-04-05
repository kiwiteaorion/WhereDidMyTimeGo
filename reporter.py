from datetime import datetime, timedelta
from collections import defaultdict
from logger import ActivityLogger
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from categories import categorize_activity

class ReportGenerator:
    def __init__(self):
        self.logger = ActivityLogger()
        self.console = Console()
    
    def _get_time_range(self, days=0):
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        # Set time to start/end of day
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        return start_date, end_date
    
    def _format_time(self, seconds):
        hours = seconds / 3600
        if hours < 1:
            minutes = seconds / 60
            return f"{minutes:.1f} minutes"
        return f"{hours:.2f} hours"
    
    def _simplify_app_name(self, window_title, process_name):
        # Common browser names
        browsers = ["chrome", "firefox", "edge", "safari", "opera"]
        
        # Check if it's a browser
        for browser in browsers:
            if browser.lower() in process_name.lower():
                # Extract domain or service name from window title
                if " - " in window_title:
                    service = window_title.split(" - ")[-1]
                    return f"{browser.capitalize()} - {service}"
                return browser.capitalize()
        
        # For standalone apps, just return the process name
        return process_name
    
    def _create_productivity_table(self, productive_time, unproductive_time, neutral_time):
        table = Table(show_header=True, header_style="bold magenta", title="Productivity Summary")
        table.add_column("Type", style="cyan")
        table.add_column("Time Spent", style="yellow")
        table.add_column("Percentage", style="green")
        
        total_time = productive_time + unproductive_time + neutral_time
        
        table.add_row(
            "Productive",
            self._format_time(productive_time),
            f"{(productive_time/total_time)*100:.1f}%"
        )
        table.add_row(
            "Unproductive",
            self._format_time(unproductive_time),
            f"{(unproductive_time/total_time)*100:.1f}%"
        )
        table.add_row(
            "Neutral",
            self._format_time(neutral_time),
            f"{(neutral_time/total_time)*100:.1f}%"
        )
        
        return table
    
    def _create_category_table(self, time_by_category):
        table = Table(show_header=True, header_style="bold magenta", title="Time by Category")
        table.add_column("Category", style="cyan")
        table.add_column("Time Spent", style="yellow")
        table.add_column("Percentage", style="green")
        
        total_time = sum(time_by_category.values())
        
        for category, seconds in sorted(time_by_category.items(), key=lambda x: x[1], reverse=True):
            time_str = self._format_time(seconds)
            percentage = (seconds / total_time) * 100
            table.add_row(category, time_str, f"{percentage:.1f}%")
        
        return table
    
    def _create_app_table(self, time_by_app):
        table = Table(show_header=True, header_style="bold magenta", title="Application Usage")
        table.add_column("Application", style="cyan")
        table.add_column("Time Spent", style="yellow")
        table.add_column("Percentage", style="green")
        
        total_time = sum(time_by_app.values())
        
        for app, seconds in sorted(time_by_app.items(), key=lambda x: x[1], reverse=True):
            time_str = self._format_time(seconds)
            percentage = (seconds / total_time) * 100
            table.add_row(app, time_str, f"{percentage:.1f}%")
        
        return table
    
    def generate_report(self, start_date=None, end_date=None):
        activities = self.logger.get_activities(start_date, end_date)
        
        # Initialize dictionaries for tracking
        time_by_category = defaultdict(float)
        time_by_app = defaultdict(float)
        productive_time = 0
        unproductive_time = 0
        neutral_time = 0
        
        for _, _, window, process, time_spent in activities:
            category, subcategory, is_productive = categorize_activity(window, process)
            
            # Update category totals
            time_by_category[category] += time_spent
            
            # Simplify app name and update app totals
            simplified_app = self._simplify_app_name(window, process)
            time_by_app[simplified_app] += time_spent
            
            # Update productivity totals
            if is_productive:
                productive_time += time_spent
            elif is_productive is False:
                unproductive_time += time_spent
            else:
                neutral_time += time_spent
        
        # Print all three tables with clear separation
        self.console.print("\n")
        self.console.print(self._create_productivity_table(productive_time, unproductive_time, neutral_time))
        self.console.print("\n")
        self.console.print(self._create_category_table(time_by_category))
        self.console.print("\n")
        self.console.print(self._create_app_table(time_by_app))
        self.console.print("\n")
    
    def generate_daily_report(self):
        start_date, end_date = self._get_time_range()
        self.generate_report(start_date, end_date)
    
    def generate_weekly_report(self):
        start_date, end_date = self._get_time_range(days=7)
        self.generate_report(start_date, end_date) 