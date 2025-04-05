import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Tuple, Optional
import os
from logger import ActivityLogger
from categories import categorize_activity

class DataVisualizer:
    def __init__(self):
        self.logger = ActivityLogger()
        self.output_dir = "reports"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def _prepare_data(self, activities: List[Tuple]) -> pd.DataFrame:
        """Convert activities to a pandas DataFrame for easier analysis"""
        data = []
        for _, timestamp, window, process, time_spent in activities:
            category, subcategory, is_productive = categorize_activity(window, process)
            data.append({
                'timestamp': datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S"),
                'window': window,
                'process': process,
                'time_spent': time_spent,
                'category': category,
                'subcategory': subcategory,
                'is_productive': is_productive
            })
        return pd.DataFrame(data)
    
    def _create_productivity_pie(self, df: pd.DataFrame, title: str) -> go.Figure:
        """Create a pie chart showing productivity distribution"""
        productive_time = df[df['is_productive'] == True]['time_spent'].sum()
        unproductive_time = df[df['is_productive'] == False]['time_spent'].sum()
        neutral_time = df[df['is_productive'].isna()]['time_spent'].sum()
        
        fig = go.Figure(data=[go.Pie(
            labels=['Productive', 'Unproductive', 'Neutral'],
            values=[productive_time, unproductive_time, neutral_time],
            hole=.3
        )])
        
        fig.update_layout(
            title=title,
            annotations=[dict(text='Productivity', x=0.5, y=0.5, font_size=20, showarrow=False)]
        )
        
        return fig
    
    def _create_category_bar(self, df: pd.DataFrame, title: str) -> go.Figure:
        """Create a bar chart showing time by category"""
        category_time = df.groupby('category')['time_spent'].sum().reset_index()
        category_time['hours'] = category_time['time_spent'] / 3600
        
        fig = go.Figure(data=[go.Bar(
            x=category_time['category'],
            y=category_time['hours'],
            text=category_time['hours'].round(1),
            textposition='auto',
        )])
        
        fig.update_layout(
            title=title,
            xaxis_title="Category",
            yaxis_title="Hours",
            showlegend=False
        )
        
        return fig
    
    def _create_time_series(self, df: pd.DataFrame, title: str) -> go.Figure:
        """Create a time series plot showing activity over time"""
        # Resample to hourly data
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        hourly_data = df.set_index('timestamp').resample('H')['time_spent'].sum().reset_index()
        hourly_data['hours'] = hourly_data['time_spent'] / 3600
        
        fig = go.Figure(data=[go.Scatter(
            x=hourly_data['timestamp'],
            y=hourly_data['hours'],
            mode='lines+markers'
        )])
        
        fig.update_layout(
            title=title,
            xaxis_title="Time",
            yaxis_title="Hours",
            showlegend=False
        )
        
        return fig
    
    def generate_report(self, start_date: Optional[datetime] = None, 
                       end_date: Optional[datetime] = None,
                       report_name: Optional[str] = None) -> str:
        """Generate a complete HTML report with multiple visualizations"""
        activities = self.logger.get_activities(start_date, end_date)
        if not activities:
            return "No data available for the selected time period"
        
        df = self._prepare_data(activities)
        
        # Create figures
        productivity_fig = self._create_productivity_pie(df, "Productivity Distribution")
        category_fig = self._create_category_bar(df, "Time by Category")
        time_series_fig = self._create_time_series(df, "Activity Over Time")
        
        # Generate HTML report
        if not report_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_name = f"report_{timestamp}.html"
        
        report_path = os.path.join(self.output_dir, report_name)
        
        with open(report_path, 'w') as f:
            f.write('<html><head><title>Time Tracking Report</title></head><body>')
            f.write('<h1>Time Tracking Report</h1>')
            
            if start_date and end_date:
                f.write(f'<p>Period: {start_date.date()} to {end_date.date()}</p>')
            
            # Add productivity pie chart
            f.write('<h2>Productivity Distribution</h2>')
            f.write(productivity_fig.to_html(full_html=False, include_plotlyjs='cdn'))
            
            # Add category bar chart
            f.write('<h2>Time by Category</h2>')
            f.write(category_fig.to_html(full_html=False, include_plotlyjs='cdn'))
            
            # Add time series
            f.write('<h2>Activity Over Time</h2>')
            f.write(time_series_fig.to_html(full_html=False, include_plotlyjs='cdn'))
            
            f.write('</body></html>')
        
        return report_path
    
    def generate_daily_report(self) -> str:
        """Generate a report for today"""
        start_date, end_date = self._get_time_range()
        return self.generate_report(start_date, end_date, "daily_report.html")
    
    def generate_weekly_report(self) -> str:
        """Generate a report for the past week"""
        start_date, end_date = self._get_time_range(days=7)
        return self.generate_report(start_date, end_date, "weekly_report.html")
    
    def _get_time_range(self, days: int = 0) -> Tuple[datetime, datetime]:
        """Get start and end dates for a time range"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        return start_date, end_date 