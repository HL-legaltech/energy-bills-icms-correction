import os
import re
import pdfplumber
import pandas as pd

INPUT_FILES_DIR = "./input"
CORRECT_TAX_RATE = 0.1508

files = os.listdir(INPUT_FILES_DIR)

table_data = {
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
df = pd.DataFrame(table_data)


def extract_client_and_installation(text):
    client_match = re.search(r"Nº DO CLIENTE\n(\d+)", text)
    installation_match = re.search(r"Nº DA INSTALAÇÃO\n(\d+)", text)

    client_number = client_match.group(1) if client_match else None
    installation_number = installation_match.group(1) if installation_match else None

    return client_number, installation_number


def parse_float(string):
    clean_string = string.replace(".", "").replace(",", ".")

    try:
        return float(clean_string)
    except ValueError:
        return None


def extract_tables_and_text(file_path: str):
    with pdfplumber.open(file_path) as pdf:
        # Extract text from each page
        all_text = ""

        for page in pdf.pages:
            text = page.extract_text()
            if text:
                all_text += text + "\n"

        # Extract tables from each page
        all_tables = []
        for page in pdf.pages:
            tables = page.extract_tables()
            if tables:
                all_tables.extend(tables)

    return all_tables, all_text


def layout_1_processing(tables: list, text: str, page):
    print("------------------\nProcessing PAGE #", page, "---------------\n")

    lines = text.splitlines()

    current_month = ""
    client_number = ""
    installation_number = ""

    # The same file can have two layouts. This is how we detect one of them.
    if "INFORMAÇÕES DE TRIBUTOS" in text:
        for table in tables:
            if len(table) == 15:
                client_number, installation_number = extract_client_and_installation(
                    table[2][-1]
                )
                calculation_base = parse_float(table[-1][0])
                applied_tax_rate = parse_float(table[-1][1])
                paid_icms = parse_float(table[-1][2])

        for i in range(len(lines)):
            if "CONTA CONTRATO" in lines[i - 1]:
                if "/" in lines[i].split(" ")[1]:
                    current_month = lines[i].split(" ")[1]

                    df.loc[len(df)] = {
                        "client_number": client_number,
                        "period": current_month,
                        "calculation_base": calculation_base,
                        "applied_tax_rate": str(round(applied_tax_rate, 2)) + "%",
                        "fixed_tax_rate": str(round(CORRECT_TAX_RATE * 100, 2)) + "%",
                        "correct_icms": round(CORRECT_TAX_RATE * calculation_base, 2),
                        "client_number": client_number,
                        "installation_number": installation_number,
                        "paid_icms": paid_icms,
                        "credits": round(
                            paid_icms - (CORRECT_TAX_RATE * calculation_base), 2
                        ),
                    }

    else:
        for table in tables:
            if len(table) == 2 and "CÓDIGO DA INSTALAÇÃO" in table[0][0]:
                client_number = table[0][0].split("\n")[1]
                installation_number = table[1][0].split("\n")[1]

        for i in range(len(lines)):
            words = lines[i].split()

            if len(words) >= 4:
                last_four = words[-4:]

                if last_four[0] == "ICMS" and all(
                    any(c.isdigit() for c in item) for item in last_four[1:]
                ):
                    try:
                        invalid_number = False
                        # Check if the numbers match the expected format
                        for num in last_four[1:]:
                            # Verify numbers contain digits, comma and/or dot
                            if not all(c.isdigit() or c in ",." for c in num):
                                invalid_number = True
                                break

                        if not invalid_number:
                            calculation_base = parse_float(last_four[1])
                            applied_tax_rate = parse_float(last_four[2])
                            paid_icms = parse_float(last_four[3])

                            # Add row to the table if all values are defined
                            if (
                                calculation_base is not None
                                and applied_tax_rate is not None
                                and paid_icms is not None
                            ):
                                df.loc[len(df)] = {
                                    "client_number": None,
                                    "period": current_month,
                                    "calculation_base": calculation_base,
                                    "applied_tax_rate": str(round(applied_tax_rate, 2))
                                    + "%",
                                    "fixed_tax_rate": str(
                                        round(CORRECT_TAX_RATE * 100, 2)
                                    )
                                    + "%",
                                    "correct_icms": round(
                                        CORRECT_TAX_RATE * calculation_base, 2
                                    ),
                                    "client_number": client_number,
                                    "installation_number": installation_number,
                                    "paid_icms": paid_icms,
                                    "credits": round(
                                        paid_icms
                                        - (CORRECT_TAX_RATE * calculation_base),
                                        2,
                                    ),
                                }

                        else:
                            print("Invalid number found")
                            print(last_four[1:])
                    except:
                        continue

            if (
                i > 0
                and "TOTAL A PAGAR" in lines[i - 1]
                and "REF:MÊS/ANO" in lines[i - 1]
            ):
                current_month = lines[i].split(" ")[0]


if __name__ == "__main__":
    print("Files to process:", files)

    selected_layout = "1"

    for file in files:
        file_path = os.path.join(INPUT_FILES_DIR, file)

        if file.endswith(".pdf"):
            print("Processing file", file)

            # Open PDF and extract text and tables
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    tables = page.extract_tables()

                    # Process text and tables
                    if selected_layout == "1":
                        layout_1_processing(tables, text, page)

                    print(df)

    df["period"] = pd.to_datetime(df["period"], format="%m/%Y")
    df = df.sort_values(by="period")

    total_credits = df["credits"].sum()
    total_row = pd.DataFrame(
        [["Total", "", "", "", "", "", "", "", total_credits]],
        columns=df.columns,
    )
    df = pd.concat([df, total_row], ignore_index=True)

    print(df)

    df.to_csv("output.csv", index=False)
