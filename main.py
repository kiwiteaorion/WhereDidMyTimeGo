import argparse
from rich.console import Console
from rich.panel import Panel
from tracker import TimeTracker
from reporter import ReportGenerator
from visualizer import DataVisualizer
import sys
from logger import ActivityLogger
from rich.table import Table
import webbrowser
import os

console = Console()

def view_all_apps():
    logger = ActivityLogger()
    activities = logger.get_activities()
    
    if not activities:
        console.print("[yellow]No activity data found.[/yellow]")
        return
    
    # Create a table to display all activities
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Timestamp")
    table.add_column("Window")
    table.add_column("Process")
    table.add_column("Time Spent")
    
    for _, timestamp, window, process, time_spent in activities:
        hours = time_spent / 3600
        table.add_row(
            timestamp,
            window,
            process,
            f"{hours:.2f} hours"
        )
    
    console.print(Panel(table, title="All Tracked Activities"))

def open_report(report_path: str):
    """Open the generated report in the default web browser"""
    if os.path.exists(report_path):
        webbrowser.open(f'file://{os.path.abspath(report_path)}')
    else:
        console.print(f"[red]Report file not found: {report_path}[/red]")

def main():
    parser = argparse.ArgumentParser(description="Where Did My Time Go - Time Tracking Application")
    parser.add_argument("--start", action="store_true", help="Start tracking time")
    parser.add_argument("--report", action="store_true", help="Generate a report")
    parser.add_argument("--today", action="store_true", help="Generate report for today")
    parser.add_argument("--week", action="store_true", help="Generate report for this week")
    parser.add_argument("--view-all", action="store_true", help="View all tracked activities")
    parser.add_argument("--visualize", action="store_true", help="Generate and open visualization report")
    parser.add_argument("--visualize-today", action="store_true", help="Generate and open today's visualization")
    parser.add_argument("--visualize-week", action="store_true", help="Generate and open weekly visualization")
    
    args = parser.parse_args()
    
    if args.start:
        try:
            console.print(Panel.fit("Starting time tracking...", title="Time Tracker"))
            tracker = TimeTracker()
            tracker.start_tracking()
        except KeyboardInterrupt:
            console.print("\n[red]Stopping time tracking...[/red]")
            sys.exit(0)
    
    elif args.report or args.today or args.week:
        reporter = ReportGenerator()
        if args.today:
            reporter.generate_daily_report()
        elif args.week:
            reporter.generate_weekly_report()
        else:
            reporter.generate_report()
    
    elif args.visualize or args.visualize_today or args.visualize_week:
        visualizer = DataVisualizer()
        if args.visualize_today:
            report_path = visualizer.generate_daily_report()
            console.print(f"[green]Generated daily visualization report: {report_path}[/green]")
            open_report(report_path)
        elif args.visualize_week:
            report_path = visualizer.generate_weekly_report()
            console.print(f"[green]Generated weekly visualization report: {report_path}[/green]")
            open_report(report_path)
        else:
            report_path = visualizer.generate_report()
            console.print(f"[green]Generated visualization report: {report_path}[/green]")
            open_report(report_path)
    
    elif args.view_all:
        view_all_apps()
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 