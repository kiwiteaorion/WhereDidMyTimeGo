from flask import Flask, render_template, jsonify, request
from datetime import datetime, timedelta
import os
import sys
import json
import pandas as pd
import logging
import sqlite3

# Add the parent directory to the path so we can import our modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from utils import cleanup_old_backups
from visualizer import DataVisualizer
from logger import ActivityLogger

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Set the correct database path
DB_PATH = os.path.join(parent_dir, 'activity.db')
logger.debug(f"Using database at: {DB_PATH}")

app = Flask(__name__)

def prepare_dataframe(activities):
    """Convert activities to a pandas DataFrame with proper column names"""
    try:
        logger.debug(f"Preparing dataframe from activities: {activities}")
        if not activities:
            logger.debug("No activities found, returning empty dataframe")
            return pd.DataFrame(columns=['id', 'timestamp', 'window', 'process', 'time_spent_seconds'])
        
        # Convert activities to DataFrame
        df = pd.DataFrame(activities, columns=['id', 'timestamp', 'window', 'process', 'time_spent_seconds'])
        
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Ensure time_spent_seconds is numeric
        df['time_spent_seconds'] = pd.to_numeric(df['time_spent_seconds'], errors='coerce')
        
        # Fill any NaN values with 0
        df['time_spent_seconds'] = df['time_spent_seconds'].fillna(0)
        
        logger.debug(f"DataFrame created with {len(df)} rows")
        logger.debug(f"DataFrame columns: {df.columns}")
        logger.debug(f"Sample data: {df.head()}")
        return df
    except Exception as e:
        logger.error(f"Error preparing dataframe: {e}")
        return pd.DataFrame(columns=['id', 'timestamp', 'window', 'process', 'time_spent_seconds'])

def categorize_activity(window_name):
    """Categorize activity based on window name"""
    window_name = str(window_name).lower()
    if any(keyword in window_name for keyword in ['code', 'dev', 'visual studio', 'intellij', 'pycharm', 'vscode']):
        return 'Productive'
    elif any(keyword in window_name for keyword in ['game', 'steam', 'epic', 'discord', 'youtube', 'netflix']):
        return 'Unproductive'
    else:
        return 'Other'

def simplify_process_name(process_name):
    """Simplify process names for display"""
    # Convert to lowercase for consistent processing
    name = process_name.lower()
    
    # Remove common file extensions
    name = name.replace('.exe', '')
    name = name.replace('.app', '')
    name = name.replace('.dmg', '')
    
    # Remove common browser suffixes
    name = name.replace(' - google chrome', '')
    name = name.replace(' - chrome', '')
    name = name.replace(' - firefox', '')
    name = name.replace(' - microsoft edge', '')
    name = name.replace(' - brave', '')
    name = name.replace(' - opera', '')
    
    # Remove common prefixes
    name = name.replace('microsoft ', '')
    name = name.replace('google ', '')
    name = name.replace('mozilla ', '')
    
    # Remove other common suffixes
    name = name.replace(' premium', '')
    name = name.replace(' pro', '')
    name = name.replace(' - cursor', '')
    name = name.replace(' dashboard', '')
    name = name.replace(' web', '')
    name = name.replace(' app', '')
    
    # Special cases for common applications
    if 'chrome' in name:
        name = 'Chrome'
    elif 'firefox' in name:
        name = 'Firefox'
    elif 'edge' in name:
        name = 'Edge'
    elif 'spotify' in name:
        name = 'Spotify'
    elif 'discord' in name:
        name = 'Discord'
    elif 'vscode' in name or 'visual studio code' in name:
        name = 'VS Code'
    elif 'explorer' in name:
        name = 'File Explorer'
    elif 'powershell' in name:
        name = 'PowerShell'
    elif 'cmd' in name or 'command' in name:
        name = 'Command Prompt'
    else:
        # For other apps, just capitalize each word
        name = ' '.join(word.capitalize() for word in name.split())
        
        # Remove any remaining parentheses and their contents
        name = ' '.join(part.split('(')[0].strip() for part in name.split(')')).strip()
    
    return name

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/activities/today')
def get_today_activities():
    try:
        logger.debug("Fetching today's activities")
        # Check if database exists
        if not os.path.exists(DB_PATH):
            logger.error(f"Database file not found at {DB_PATH}")
            return jsonify({
                'error': 'Database not found',
                'productivity': {'labels': ['No Data'], 'values': [1]},
                'categories': {'categories': ['No Data'], 'values': [1]},
                'timeSeries': {'timestamps': ['No Data'], 'values': [1]}
            })
        
        # Check database contents
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM activity')
        total_records = cursor.fetchone()[0]
        logger.debug(f"Total records in database: {total_records}")
        
        cursor.execute('SELECT * FROM activity ORDER BY timestamp DESC LIMIT 5')
        recent_records = cursor.fetchall()
        logger.debug(f"Recent records: {recent_records}")
        conn.close()
        
        # Create ActivityLogger with the correct database path
        activity_logger = ActivityLogger(db_path=DB_PATH)
        
        # Get today's data
        today = datetime.now().date()
        start_date = datetime.combine(today, datetime.min.time())
        end_date = datetime.combine(today, datetime.max.time())
        
        logger.debug(f"Fetching activities between {start_date} and {end_date}")
        activities = activity_logger.get_activities(start_date, end_date)
        logger.debug(f"Retrieved {len(activities)} activities")
        logger.debug(f"Activities data: {activities}")
        
        df = prepare_dataframe(activities)
        
        if df.empty:
            logger.debug("No data found for today")
            return jsonify({
                'productivity': {'labels': ['No Data'], 'values': [1]},
                'categories': {'categories': ['No Data'], 'values': [1]},
                'timeSeries': {'timestamps': ['No Data'], 'values': [1]}
            })
        
        # Add category column
        df['category'] = df['window'].apply(categorize_activity)
        
        # Generate productivity data
        logger.debug("Generating productivity data")
        productivity_data = {
            'labels': ['Productive', 'Unproductive', 'Other'],
            'values': [
                df[df['category'] == 'Productive']['time_spent_seconds'].sum() / 3600,
                df[df['category'] == 'Unproductive']['time_spent_seconds'].sum() / 3600,
                df[df['category'] == 'Other']['time_spent_seconds'].sum() / 3600
            ]
        }
        logger.debug(f"Productivity data: {productivity_data}")
        
        # Generate category data
        logger.debug("Generating category data")
        process_groups = df.groupby('process')['time_spent_seconds'].sum()
        top_processes = process_groups.nlargest(10)
        category_data = {
            'categories': top_processes.index.tolist(),
            'values': (top_processes / 3600).tolist()
        }
        logger.debug(f"Category data: {category_data}")
        
        # Generate time series data
        logger.debug("Generating time series data")
        df['hour'] = df['timestamp'].dt.strftime('%H:%M')
        hourly_data = df.groupby('hour')['time_spent_seconds'].sum()
        time_series_data = {
            'timestamps': hourly_data.index.tolist(),
            'values': (hourly_data / 3600).tolist()
        }
        logger.debug(f"Time series data: {time_series_data}")
        
        return jsonify({
            'productivity': productivity_data,
            'categories': category_data,
            'timeSeries': time_series_data
        })
    except Exception as e:
        logger.error(f"Error in get_today_activities: {e}")
        return jsonify({
            'error': str(e),
            'productivity': {'labels': ['Error'], 'values': [1]},
            'categories': {'categories': ['Error'], 'values': [1]},
            'timeSeries': {'timestamps': ['Error'], 'values': [1]}
        })

@app.route('/api/activities/week')
def get_week_activities():
    try:
        logger.debug("Fetching week's activities")
        if not os.path.exists(DB_PATH):
            logger.error(f"Database file not found at {DB_PATH}")
            return jsonify({
                'error': 'Database not found',
                'productivity': {'labels': ['No Data'], 'values': [1]},
                'categories': {'categories': ['No Data'], 'values': [1]},
                'timeSeries': {'timestamps': ['No Data'], 'values': [1]}
            })
        
        # Create ActivityLogger with the correct database path
        activity_logger = ActivityLogger(db_path=DB_PATH)
        
        # Get this week's data
        today = datetime.now()
        start_date = today - timedelta(days=today.weekday())
        start_date = datetime.combine(start_date.date(), datetime.min.time())
        end_date = datetime.combine(today.date(), datetime.max.time())
        
        logger.debug(f"Fetching activities between {start_date} and {end_date}")
        activities = activity_logger.get_activities(start_date, end_date)
        logger.debug(f"Retrieved {len(activities)} activities")
        
        df = prepare_dataframe(activities)
        
        if df.empty:
            logger.debug("No data found for this week")
            return jsonify({
                'productivity': {'labels': ['No Data'], 'values': [1]},
                'categories': {'categories': ['No Data'], 'values': [1]},
                'timeSeries': {'timestamps': ['No Data'], 'values': [1]}
            })
        
        # Add category column
        df['category'] = df['window'].apply(categorize_activity)
        
        # Generate productivity data
        logger.debug("Generating productivity data")
        productivity_data = {
            'labels': ['Productive', 'Unproductive', 'Other'],
            'values': [
                df[df['category'] == 'Productive']['time_spent_seconds'].sum() / 3600,
                df[df['category'] == 'Unproductive']['time_spent_seconds'].sum() / 3600,
                df[df['category'] == 'Other']['time_spent_seconds'].sum() / 3600
            ]
        }
        logger.debug(f"Productivity data: {productivity_data}")
        
        # Generate category data
        logger.debug("Generating category data")
        process_groups = df.groupby('process')['time_spent_seconds'].sum()
        top_processes = process_groups.nlargest(10)
        category_data = {
            'categories': top_processes.index.tolist(),
            'values': (top_processes / 3600).tolist()
        }
        logger.debug(f"Category data: {category_data}")
        
        # Generate time series data
        logger.debug("Generating time series data")
        df['day'] = df['timestamp'].dt.strftime('%Y-%m-%d')
        daily_data = df.groupby('day')['time_spent_seconds'].sum()
        time_series_data = {
            'timestamps': daily_data.index.tolist(),
            'values': (daily_data / 3600).tolist()
        }
        logger.debug(f"Time series data: {time_series_data}")
        
        return jsonify({
            'productivity': productivity_data,
            'categories': category_data,
            'timeSeries': time_series_data
        })
    except Exception as e:
        logger.error(f"Error in get_week_activities: {e}")
        return jsonify({
            'error': str(e),
            'productivity': {'labels': ['Error'], 'values': [1]},
            'categories': {'categories': ['Error'], 'values': [1]},
            'timeSeries': {'timestamps': ['Error'], 'values': [1]}
        })

@app.route('/api/activities/range', methods=['POST'])
def get_activities_range():
    try:
        data = request.get_json()
        start_date = data.get('startDate')
        end_date = data.get('endDate')
        
        if not start_date or not end_date:
            return jsonify({'error': 'Missing start or end date'}), 400
        
        logger.debug(f"Fetching activities between {start_date} and {end_date}")
        
        # Create ActivityLogger with the correct database path
        activity_logger = ActivityLogger(db_path=DB_PATH)
        
        # Convert string dates to datetime objects
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Set time to start/end of day
        start_date = datetime.combine(start_date, datetime.min.time())
        end_date = datetime.combine(end_date, datetime.max.time())
        
        activities = activity_logger.get_activities(start_date, end_date)
        logger.debug(f"Retrieved {len(activities)} activities")

        df = prepare_dataframe(activities)
        
        if df.empty:
            return jsonify({
                'totalTime': 0,
                'productiveTime': 0,
                'unproductiveTime': 0,
                'productivity': {'labels': ['No Data'], 'values': [1]},
                'categories': {'categories': ['No Data'], 'values': [1]},
                'timeSeries': {'timestamps': ['No Data'], 'values': [1]}
            })

        # Add category column
        df['category'] = df['window'].apply(categorize_activity)
        
        # Simplify process names for the category chart
        df['simplified_process'] = df['process'].apply(simplify_process_name)
        
        # Calculate total times
        total_time = df['time_spent_seconds'].sum() / 3600
        productive_time = df[df['category'] == 'Productive']['time_spent_seconds'].sum() / 3600
        unproductive_time = df[df['category'] == 'Unproductive']['time_spent_seconds'].sum() / 3600
        other_time = df[df['category'] == 'Other']['time_spent_seconds'].sum() / 3600
        
        # Generate productivity data
        productivity_data = {
            'labels': ['Productive', 'Unproductive', 'Other'],
            'values': [productive_time, unproductive_time, other_time]
        }
        
        # Generate category data using simplified process names
        process_groups = df.groupby('simplified_process')['time_spent_seconds'].sum()
        top_processes = process_groups.nlargest(10)
        category_data = {
            'categories': top_processes.index.tolist(),
            'values': (top_processes / 3600).tolist()
        }
        
        # Generate time series data (daily totals)
        time_series_data = df.groupby(df['timestamp'].dt.date)['time_spent_seconds'].sum().reset_index()

        return jsonify({
            'totalTime': round(total_time, 2),
            'productiveTime': round(productive_time, 2),
            'unproductiveTime': round(unproductive_time, 2),
            'productivity': {
                'labels': productivity_data['labels'],
                'values': [round(v, 2) for v in productivity_data['values']]
            },
            'categories': {
                'categories': category_data['categories'],
                'values': [round(v, 2) for v in category_data['values']]
            },
            'timeSeries': {
                'timestamps': time_series_data['timestamp'].astype(str).tolist(),
                'values': [round(v/3600, 2) for v in time_series_data['time_spent_seconds'].tolist()]
            }
        })
    except Exception as e:
        logger.error(f"Error processing activities: {e}")
        return jsonify({
            'error': str(e),
            'totalTime': 0,
            'productiveTime': 0,
            'unproductiveTime': 0
        }), 500

@app.route('/api/cleanup-backups', methods=['POST'])
def cleanup_backups():
    try:
        # Get the number of days to keep from the request
        data = request.get_json()
        keep_days = data.get('keep_days', 7)
        
        # Get the backup directory path
        backup_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backups')
        
        # Clean up old backups
        cleanup_old_backups(backup_dir, keep_days)
        
        return jsonify({
            'success': True,
            'message': f'Successfully cleaned up backups older than {keep_days} days'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error cleaning up backups: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(debug=True) 