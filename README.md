## Log Analysis Web App

This project is a simple **Flask** web application that analyzes log files and generates a **PDF report** with useful statistics.

You upload a log file (e.g. `.log`, `.txt`, `.csv`, `.json`), the app parses it, extracts metrics (errors, warnings, IPs, URLs, HTTP status codes, timelines, etc.) using `LogAnalyzer`, and then `PDFGenerator` creates a formatted PDF report for download.

### Features

- **Web UI (Flask)** to upload log files.
- **Large-file friendly** line‑by‑line analysis.
- Counts of **errors / warnings / info** lines.
- Detection of **error types**, **top IPs**, **status codes**, **URLs**, and **timestamps**.
- **PDF report** summarizing all findings.

### Project Structure (key files)

- `log_analysis/app.py` – Flask app entrypoint and upload endpoint.
- `log_analysis/log_analyzer.py` – Core log analysis logic.
- `log_analysis/pdf_generator.py` – Generates the PDF report from analysis results.
- `log_analysis/requirements.txt` – Python dependencies for the app.

### Prerequisites

- **Python 3.10+** installed and available on your PATH.
- `pip` working (so that dependencies can be installed).

### Setup

From a terminal (PowerShell or cmd):

```bash
python -m venv .venv

.\.venv\Scripts\activate

pip install -r log_analysis\requirements.txt
```

### Run the App

With the virtual environment activated:

```bash

python app.py

```

Then open your browser and go to:

- `http://127.0.0.1:5000`

Upload a supported log file to receive a generated PDF report.


