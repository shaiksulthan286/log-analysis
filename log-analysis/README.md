# Log Analysis Tool

A web-based tool for analyzing log files and generating comprehensive PDF reports.

## Features

- 📁 **File Upload**: Drag & drop or click to upload log files
- 📊 **Comprehensive Analysis**: Analyzes errors, warnings, IP addresses, URLs, and more
- 📄 **PDF Reports**: Generates detailed PDF reports with visual tables and statistics
- 🎨 **Modern UI**: Beautiful, responsive web interface

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the Flask server:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. Upload a log file (.txt, .log, .csv, or .json)

4. The PDF report will be automatically downloaded

## Supported File Types

- `.txt` - Text log files
- `.log` - Log files
- `.csv` - CSV files
- `.json` - JSON files

## Analysis Features

The tool analyzes:
- Total lines and file size
- Error, warning, and info counts
- Error types and patterns
- IP addresses and their frequency
- HTTP status codes
- URLs found in logs
- Timeline of events

## Project Structure

```
crypto-toolkit/
├── app.py              # Flask application
├── log_analyzer.py     # Log analysis logic
├── pdf_generator.py    # PDF report generation
├── templates/
│   └── index.html      # Web frontend
├── requirements.txt    # Python dependencies
└── uploads/           # Temporary upload directory (auto-created)
```

