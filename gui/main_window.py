from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QPushButton, QSystemTrayIcon, QMenu, QTabWidget,
                               QApplication, QStyle, QComboBox)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QSize
from PyQt6.QtGui import QIcon, QAction, QPainter
from PyQt6.QtCharts import QChart, QChartView
import sys
import os
from datetime import datetime
from qt_material import apply_stylesheet, list_themes
import darkdetect

# Add parent directory to path so we can import our existing modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logger import ActivityLogger
from tracker import TimeTracker

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Time Tracker")
        self.setMinimumSize(1000, 600)
        
        # Initialize logger and tracker
        self.activity_logger = ActivityLogger()
        self.tracker = TimeTracker()
        
        # Cache for stats to prevent unnecessary updates
        self._stats_cache = {}
        self._last_update = None
        
        # Setup UI
        self._setup_ui()
        self._setup_tray()
        
        # Setup update timer with optimized interval
        self._update_timer = QTimer(self)
        self._update_timer.timeout.connect(self._update_stats)
        self._update_timer.start(30000)  # Update every 30 seconds instead of 60
        
        # Initial stats update
        self._update_stats()
        
        # Start with fade-in animation
        self._fade_in()
    
    def _fade_in(self):
        self.setWindowOpacity(0)
        self.show()
        
        self._fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self._fade_animation.setDuration(300)
        self._fade_animation.setStartValue(0.0)
        self._fade_animation.setEndValue(1.0)
        self._fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._fade_animation.start()
    
    def _setup_ui(self):
        # Create central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setSpacing(20)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        
        self._setup_header()
        self._setup_tabs()
        
        # Ensure the central widget has a minimum size
        self.central_widget.setMinimumSize(800, 500)
    
    def _setup_header(self):
        # Create header with time stats
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setSpacing(20)
        
        # Create stat widgets with hover effects
        self._total_time = self._create_stat_widget("Total Time", "0h 0m")
        self._productive_time = self._create_stat_widget("Productive", "0h 0m")
        self._unproductive_time = self._create_stat_widget("Unproductive", "0h 0m")
        
        header_layout.addWidget(self._total_time)
        header_layout.addWidget(self._productive_time)
        header_layout.addWidget(self._unproductive_time)
        
        self.main_layout.addWidget(header)
    
    def _setup_tabs(self):
        # Create tab widget
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        
        self._setup_overview_tab()
        self._setup_settings_tab()
        
        # Add tabs to main layout
        self.main_layout.addWidget(self.tabs)
    
    def _setup_overview_tab(self):
        overview_tab = QWidget()
        overview_layout = QVBoxLayout(overview_tab)
        overview_layout.setSpacing(20)
        
        # Create chart views with optimized settings
        self._productivity_chart = QChartView()
        self._category_chart = QChartView()
        self._timeline_chart = QChartView()
        
        # Optimize chart rendering
        for chart in [self._productivity_chart, self._category_chart, self._timeline_chart]:
            chart.setMinimumSize(300, 200)
            chart.setRenderHint(QPainter.RenderHint.Antialiasing)
            chart.setViewportUpdateMode(QChartView.ViewportUpdateMode.SmartViewportUpdate)
        
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(20)
        charts_layout.addWidget(self._productivity_chart)
        charts_layout.addWidget(self._category_chart)
        overview_layout.addLayout(charts_layout)
        overview_layout.addWidget(self._timeline_chart)
        
        self.tabs.addTab(overview_tab, "Overview")
    
    def _setup_settings_tab(self):
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)
        settings_layout.setSpacing(20)
        
        # Theme settings
        theme_group = QWidget()
        theme_layout = QVBoxLayout(theme_group)
        theme_layout.setSpacing(10)
        
        theme_label = QLabel("Theme Settings")
        theme_label.setProperty("class", "settings-header")
        theme_layout.addWidget(theme_label)
        
        # Create optimized theme dropdown
        self.theme_combo = QComboBox()
        self.theme_combo.setProperty("class", "theme-combo")
        self.theme_combo.setMinimumWidth(200)
        
        # Add themes
        themes = [
            ("Light Blue", "light_blue.xml"),
            ("Light Amber", "light_amber.xml"),
            ("Light Cyan", "light_cyan.xml"),
            ("Light Teal", "light_teal.xml"),
            (None, None),  # Separator
            ("Dark Blue", "dark_blue.xml"),
            ("Dark Amber", "dark_amber.xml"),
            ("Dark Cyan", "dark_cyan.xml"),
            ("Dark Teal", "dark_teal.xml")
        ]
        
        for name, value in themes:
            if name is None:
                self.theme_combo.insertSeparator(self.theme_combo.count())
            else:
                self.theme_combo.addItem(name, value)
        
        # Set initial theme based on system preference
        is_dark = darkdetect.isDark()
        initial_theme = "dark_blue.xml" if is_dark else "light_blue.xml"
        index = self.theme_combo.findData(initial_theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        
        self.theme_combo.currentIndexChanged.connect(self._change_theme)
        theme_layout.addWidget(self.theme_combo)
        
        settings_layout.addWidget(theme_group)
        settings_layout.addStretch()
        
        self.tabs.addTab(settings_tab, "Settings")
    
    def _create_stat_widget(self, title, value):
        widget = QWidget()
        widget.setProperty("class", "stat-widget")
        widget.setMinimumHeight(100)
        widget.setMinimumWidth(200)
        
        layout = QVBoxLayout(widget)
        layout.setSpacing(5)
        
        title_label = QLabel(title)
        title_label.setProperty("class", "stat-title")
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setProperty("class", "stat-value")
        layout.addWidget(value_label)
        
        return widget
    
    def _setup_tray(self):
        self._tray_icon = QSystemTrayIcon(self)
        self._tray_icon.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        
        tray_menu = QMenu()
        for action_text, slot in [
            ("Show", self.show),
            ("Hide", self.hide),
            ("Quit", QApplication.quit)
        ]:
            action = QAction(action_text, self)
            action.triggered.connect(slot)
            tray_menu.addAction(action)
        
        self._tray_icon.setContextMenu(tray_menu)
        self._tray_icon.show()
    
    def _update_stats(self):
        try:
            today = datetime.now().date()
            start_date = datetime.combine(today, datetime.min.time())
            end_date = datetime.combine(today, datetime.max.time())
            
            # Only update if necessary
            if (not self._last_update or 
                (datetime.now() - self._last_update).seconds > 30):
                activities = self.activity_logger.get_activities(start_date, end_date)
                self._stats_cache = self._process_activities(activities)
                self._last_update = datetime.now()
            
            self._update_display()
            
        except Exception as e:
            print(f"Error updating stats: {e}")
    
    def _process_activities(self, activities):
        # Process activities and return cached stats
        # TODO: Implement activity processing
        return {}
    
    def _update_display(self):
        # Update UI with cached stats
        # TODO: Implement display update
        pass
    
    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self._tray_icon.showMessage(
            "Time Tracker",
            "Application minimized to tray. Double-click to restore.",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )
    
    def _change_theme(self, index):
        app = QApplication.instance()
        theme = self.theme_combo.currentData()
        
        try:
            # Apply theme directly without animation
            apply_stylesheet(app, theme=theme)
            
            # Force an immediate refresh of the window and all widgets
            app.processEvents()
            self.repaint()
            
            # Ensure window stays in front
            self.raise_()
            self.activateWindow()
            
        except Exception as e:
            print(f"Error applying theme: {e}") 