import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from main_window import MainWindow
from qt_material import apply_stylesheet
import darkdetect

def main():
    # Create application
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Use Fusion style as base
    
    # Apply theme based on system preference
    is_dark = darkdetect.isDark()
    theme = "dark_blue.xml" if is_dark else "light_blue.xml"
    apply_stylesheet(app, theme=theme)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Start the event loop
    return app.exec()

if __name__ == "__main__":
    sys.exit(main()) 