# ICMS Tax Analysis Tool

## Overview
This tool processes electricity bills in PDF format to analyze ICMS tax calculations and identify potential tax credits. It generates detailed reports in both Excel and PDF formats.

## Prerequisites
- Python 3.8+ ([Download Python](https://www.python.org/downloads/))
- wkhtmltopdf ([Download wkhtmltopdf](https://wkhtmltopdf.org/downloads.html))

## Setup
1. Clone the repository
```bash
git clone https://github.com/HL-legaltech/energy-bills-icms-correction
cd energy-bills-icms-correction
```

2. Create virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/MacOS
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

## Project Structure
```
.
├── input/          # Place client PDF files here
├── output/         # Generated reports will appear here
├── src.py          # Main processing script
└── requirements.txt
```

## Usage
1. Create `input` and `output` folders if they don't exist
2. Place all PDF files from ONE client in the `input` folder
   - ⚠️ Important: Do not mix files from different clients
3. Run the script:
```bash
python src.py
```
4. Check the `output` folder for generated reports:
   - `relatorio_icms.xlsx`: Detailed Excel report
   - `relatorio_icms.pdf`: Formatted PDF report

## Requirements
```
pdfplumber==0.10.3
pandas==2.1.4
openpyxl==3.1.2
pdfkit==1.0.0
```