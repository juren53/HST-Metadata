## CRITIQUE_g2c-py_by_gemini.md


This script, `g2c.py`, is a specialized utility designed to bridge the gap between human-managed Excel spreadsheets and automated metadata systems (specifically for IPTC/HPM projects). It converts `.xlsx` or `.xls` files into a standardized CSV format with very specific column mapping and data cleaning.

Here is a walkthrough of how the code functions, step-by-step:

---

## 1. File Ingestion (`read_excel_file`)

The script starts by looking for an Excel file (defaulting to `input/spreadsheet/metadata.xlsx`).

* **Engine Selection:** It intelligently switches between `openpyxl` (for newer `.xlsx` files) and `xlrd` (for older `.xls` files).
* **Validation:** It checks if the file exists and if it actually contains data before proceeding to load it into a pandas DataFrame.

## 2. Text "De-Garbling" (`clean_encoding_artifacts`)

One of the more unique features of this script is its ability to fix "mojibake"—those strange character sequences that happen when text is saved in the wrong encoding.

* **Artifact Mapping:** It searches for sequences like `Ã±` and converts them back to the correct characters (e.g., `ñ`).
* **Typography Correction:** It fixes "smart quotes" and dashes (`â€œ` becomes `"`) that often break downstream systems.
* **Sanitization:** It strips out non-printable null bytes while preserving standard tabs and newlines.

## 3. Metadata Mapping (`export_to_csv`)

The heart of the script is the transformation logic. It doesn't just copy columns; it translates them based on the **content of the 3rd row** of your spreadsheet.

| Original Label (Row 3) | IPTC Target Header |
| --- | --- |
| Title | Headline |
| Accession Number | ObjectName |
| Restrictions | CopyrightNotice |
| Scopenote | Caption-Abstract |
| Related Collection | Source |
| Source Photographer | By-line |
| Institutional Creator | By-lineTitle |

## 4. Date Standardization

The script looks for three specific columns: `productionDateMonth`, `productionDateDay`, and `productionDateYear`.

* It skips the header rows (first 3 rows).
* It validates that the values are numbers and fall within logical ranges (e.g., months 1–12).
* It combines them into a new **ISO 8601** column named `DateCreated` (formatted as `YYYY-MM-DD`).

## 5. Execution Flow (`main`)

When you run the script from the command line:

1. **Arguments:** It parses your flags (like `--excel-file` or `--export-csv`).
2. **Summary:** It prints a summary of the loaded data to your console (shape, columns, and the first 10 rows) so you can verify it looks right before exporting.
3. **Export:** It writes the cleaned, mapped data to a CSV using `utf-8` encoding to ensure the characters remain "clean" for the next tool in your pipeline.

---

### How to use it

If you have your file in the default location, just run:

```bash
python g2c.py --export-csv

```

**Would you like me to help you modify the IPTC mapping table or add support for additional metadata fields?**