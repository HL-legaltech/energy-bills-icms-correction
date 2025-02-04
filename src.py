import os
import re
import pdfplumber
import pandas as pd

# Configuration constants
INPUT_FILES_DIR = "./input"
CORRECT_TAX_RATE = 0.1508

# Get list of files to process
input_files = os.listdir(INPUT_FILES_DIR)

# Define the structure for our tax data
tax_data_columns = {
    "installation_number": [],
    "client_number": [],
    "period": [],
    "calculation_base": [],
    "applied_tax_rate": [],
    "paid_icms": [],
    "fixed_tax_rate": [],
    "correct_icms": [],
    "credits": [],
}

# Initialize DataFrame with our column structure
tax_data_df = pd.DataFrame(tax_data_columns)


def extract_client_and_installation(text: str) -> tuple[str | None, str | None]:
    """
    Extract client and installation numbers from the PDF text using regex.

    Args:
        text: The text content to search in

    Returns:
        Tuple containing client number and installation number (both optional)
    """
    client_match = re.search(r"Nº DO CLIENTE\n(\d+)", text)
    installation_match = re.search(r"Nº DA INSTALAÇÃO\n(\d+)", text)

    client_number = client_match.group(1) if client_match else None
    installation_number = installation_match.group(1) if installation_match else None

    return client_number, installation_number


def parse_brazilian_float(value_str: str) -> float | None:
    """
    Convert Brazilian number format (using comma as decimal separator) to float.

    Args:
        value_str: String representing a number in Brazilian format (e.g., "1.234,56")

    Returns:
        Converted float value or None if conversion fails
    """
    clean_string = value_str.replace(".", "").replace(",", ".")

    try:
        return float(clean_string)
    except ValueError:
        return None


def extract_pdf_content(file_path: str) -> tuple[list, str]:
    """
    Extract both tables and text content from a PDF file.

    Args:
        file_path: Path to the PDF file

    Returns:
        Tuple containing (tables, text_content)
    """
    with pdfplumber.open(file_path) as pdf:
        # Extract all text from PDF
        full_text = ""
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"

        # Extract all tables from PDF
        all_tables = []
        for page in pdf.pages:
            tables = page.extract_tables()
            if tables:
                all_tables.extend(tables)

    return all_tables, full_text


def process_tax_page(tables: list, text: str, page_num: int) -> None:
    """
    Process a single page of tax information from the PDF.
    Handles two different layouts: tax information layout and standard layout.

    Args:
        tables: List of tables extracted from the page
        text: Text content of the page
        page_num: Page number for logging purposes
    """
    print(f"------------------\nProcessing PAGE #{page_num}---------------\n")

    text_lines = text.splitlines()
    current_month = ""
    client_number = ""
    installation_number = ""

    # Process special tax information layout
    if "INFORMAÇÕES DE TRIBUTOS" in text:
        _process_tax_info_layout(tables, text_lines)
    else:
        _process_standard_layout(tables, text_lines)


def _process_tax_info_layout(tables: list, text_lines: list) -> None:
    """
    Process pages with "INFORMAÇÕES DE TRIBUTOS" layout.
    This layout has tax information in a specific table format.
    """
    for table in tables:
        if len(table) == 15:
            client_number, installation_number = extract_client_and_installation(
                table[2][-1]
            )
            calculation_base = parse_brazilian_float(table[-1][0])
            applied_tax_rate = parse_brazilian_float(table[-1][1])
            paid_icms = parse_brazilian_float(table[-1][2])

            _extract_and_add_tax_record(
                text_lines,
                client_number,
                installation_number,
                calculation_base,
                applied_tax_rate,
                paid_icms,
            )


def _process_standard_layout(tables: list, text_lines: list) -> None:
    """
    Process pages with standard layout.
    This layout has tax information spread across the document in a different format.
    """
    client_number = installation_number = current_month = None

    # Extract client and installation info from tables
    for table in tables:
        if len(table) == 2 and "CÓDIGO DA INSTALAÇÃO" in table[0][0]:
            client_number = table[0][0].split("\n")[1]
            installation_number = table[1][0].split("\n")[1]

    # Process each line for tax information
    for i, line in enumerate(text_lines):
        words = line.split()

        # Extract month information
        if (
            i > 0
            and "TOTAL A PAGAR" in text_lines[i - 1]
            and "REF:MÊS/ANO" in text_lines[i - 1]
        ):
            current_month = words[0]

        # Process tax values if line contains ICMS information
        if len(words) >= 4:
            _process_icms_line(
                words[-4:], client_number, installation_number, current_month
            )


def _process_icms_line(
    values: list, client_number: str, installation_number: str, current_month: str
) -> None:
    """Process a line containing ICMS tax information."""
    if values[0] != "ICMS":
        return

    try:
        # Validate number format
        if not all(all(c.isdigit() or c in ",." for c in num) for num in values[1:]):
            print("Invalid number format found:", values[1:])
            return

        # Parse tax values
        calculation_base = parse_brazilian_float(values[1])
        applied_tax_rate = parse_brazilian_float(values[2])
        paid_icms = parse_brazilian_float(values[3])

        # Add tax record if all values are valid
        if all(v is not None for v in [calculation_base, applied_tax_rate, paid_icms]):
            _add_tax_record(
                client_number,
                installation_number,
                current_month,
                calculation_base,
                applied_tax_rate,
                paid_icms,
            )
    except Exception as e:
        print(f"Error processing ICMS line: {e}")


def _add_tax_record(
    client_number: str,
    installation_number: str,
    period: str,
    calculation_base: float,
    applied_tax_rate: float,
    paid_icms: float,
) -> None:
    """Add a new tax record to the DataFrame."""
    correct_icms = round(CORRECT_TAX_RATE * calculation_base, 2)
    tax_credits = round(paid_icms - correct_icms, 2)

    tax_data_df.loc[len(tax_data_df)] = {
        "client_number": client_number,
        "installation_number": installation_number,
        "period": period,
        "calculation_base": calculation_base,
        "applied_tax_rate": f"{round(applied_tax_rate, 2)}%",
        "fixed_tax_rate": f"{round(CORRECT_TAX_RATE * 100, 2)}%",
        "correct_icms": correct_icms,
        "paid_icms": paid_icms,
        "credits": tax_credits,
    }


def _extract_and_add_tax_record(
    text_lines: list,
    client_number: str,
    installation_number: str,
    calculation_base: float,
    applied_tax_rate: float,
    paid_icms: float,
) -> None:
    """Extract period information and add tax record for tax info layout."""
    for i, line in enumerate(text_lines):
        if "CONTA CONTRATO" in text_lines[i - 1]:
            words = line.split()
            if len(words) > 1 and "/" in words[1]:
                _add_tax_record(
                    client_number,
                    installation_number,
                    words[1],
                    calculation_base,
                    applied_tax_rate,
                    paid_icms,
                )


if __name__ == "__main__":
    print("Files to process:", input_files)

    # Process each PDF file
    for file in input_files:
        if not file.endswith(".pdf"):
            continue

        file_path = os.path.join(INPUT_FILES_DIR, file)
        print("Processing file:", file)

        # Process each page in the PDF
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                tables = page.extract_tables()
                process_tax_page(tables, text, page_num)

    # Prepare final report
    tax_data_df["period"] = pd.to_datetime(tax_data_df["period"], format="%m/%Y")
    tax_data_df = tax_data_df.sort_values(by="period")

    # Add total row
    total_credits = tax_data_df["credits"].sum()
    total_row = pd.DataFrame(
        [["Total", "", "", "", "", "", "", "", total_credits]],
        columns=tax_data_df.columns,
    )
    tax_data_df = pd.concat([tax_data_df, total_row], ignore_index=True)

    # Save results
    print(tax_data_df)
    tax_data_df.to_csv("output.csv", index=False)
