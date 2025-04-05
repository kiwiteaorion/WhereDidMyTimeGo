# Where Did My Time Go? 🕒

A powerful and intuitive time tracking application that helps you understand how you spend your time on your computer.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Features ✨

- **Automatic Time Tracking**: Silently tracks your active windows and applications
- **Smart Categorization**: Automatically categorizes your activities
- **Productivity Insights**: Understand your productive vs unproductive time
- **Beautiful Visualizations**: View your time usage through intuitive charts
- **Privacy First**: All data stays local on your machine
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Installation 🚀

1. Clone the repository:

```bash
git clone https://github.com/yourusername/where-did-my-time-go.git
cd where-did-my-time-go
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the application:

```bash
python main.py
```

## Usage 📖

1. **Starting the Application**

   - Run the application using the command above or the executable
   - The app will minimize to system tray and start tracking automatically

2. **Viewing Statistics**

   - Click the system tray icon to open the main window
   - View your time distribution across different applications
   - Switch between different time periods (daily, weekly, monthly)

3. **Settings**
   - Customize application categories
   - Set productivity rules
   - Configure theme and appearance
   - Manage data backup and export

## Screenshots 📸

[Screenshots will be added in future updates]

## Development 🛠️

### Prerequisites

- Python 3.8 or higher
- PyQt6
- Other dependencies listed in requirements.txt

### Project Structure

```
where-did-my-time-go/
├── gui/                    # GUI-related code
│   ├── main_window.py     # Main window implementation
│   └── style.qss         # QSS styles
├── web/                   # Web interface files
├── logger.py             # Activity logging
├── tracker.py            # Time tracking core
├── reporter.py           # Report generation
└── main.py              # Application entry point
```

### Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Versioning 📌

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/yourusername/where-did-my-time-go/tags).

Current version: 1.0.0

## Authors 👥

- **Your Name** - _Initial work_

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments 🙏

- Thanks to all contributors
- PyQt6 for the GUI framework
- All other open source libraries used in this project
