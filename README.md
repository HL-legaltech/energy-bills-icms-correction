# ICMS Tax Analysis Tool

## Overview
This tool processes electricity bills in PDF format to analyze ICMS tax calculations and identify potential tax credits. It generates detailed reports in both Excel and PDF formats.

## Prerequisites
- Python 3.8+ ([Download Python](https://www.python.org/downloads/))
- wkhtmltopdf ([Download wkhtmltopdf](https://wkhtmltopdf.org/downloads.html))

### Installing wkhtmltopdf
1. **Download the Installer**:
   - Visit the [wkhtmltopdf downloads page](https://wkhtmltopdf.org/downloads.html) and download the installer for your operating system.

2. **Install wkhtmltopdf**:
   - **Windows**:
     - Run the installer and follow the installation steps.
     - By default, wkhtmltopdf is installed in `C:\Program Files\wkhtmltopdf\bin`.
   - **Linux**:
     - Use your package manager to install wkhtmltopdf. For example:
       ```bash
       sudo apt-get install wkhtmltopdf
       ```
   - **MacOS**:
     - Use Homebrew to install wkhtmltopdf:
       ```bash
       brew install --cask wkhtmltopdf
       ```

3. **Add wkhtmltopdf to System PATH**:
   - **Windows**:
     1. Open the Start Menu and search for "Environment Variables".
     2. Click on "Edit the system environment variables".
     3. In the System Properties window, click on the "Environment Variables" button.
     4. Under "System variables", find the `Path` variable and click "Edit".
     5. Add the wkhtmltopdf installation directory (e.g., `C:\Program Files\wkhtmltopdf\bin`) to the list of paths.
     6. Click "OK" to save the changes.
   - **Linux/MacOS**:
     - If wkhtmltopdf is not automatically added to your PATH, add it manually by editing your shell configuration file (e.g., `.bashrc`, `.zshrc`):
       ```bash
       export PATH=$PATH:/usr/local/bin/wkhtmltopdf
       ```
     - Reload the shell configuration:
       ```bash
       source ~/.bashrc  # or source ~/.zshrc
       ```

4. **Verify Installation**:
   - Open a terminal or command prompt and run:
     ```bash
     wkhtmltopdf --version
     ```
   - If the command returns the version number, wkhtmltopdf is installed and configured correctly.

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
