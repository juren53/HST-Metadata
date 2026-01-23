## CRITIQUE_g2c-py_by_ChatGPT.md


Alright, let’s walk through **`g2c.py`** like we’re code-reviewing it together. I’ll go **top → bottom**, explain **what it’s trying to do**, **how each part works**, and I’ll also flag **important quirks / bugs / design smells** as we go (there are a few 👀).

---

## Big-picture: What this script is for

**Goal:**
Convert a **metadata Excel spreadsheet** into a **CSV formatted for IPTC fields**, using **row 3 of the spreadsheet as semantic labels**, not the column headers.

This is *not* a generic Excel→CSV converter. It assumes:

* Row 1–3 contain **metadata about the metadata**
* Real data starts at **row index 3**
* IPTC fields are inferred from **row 3 values**
* Some dates are split across `productionDateMonth/Day/Year`

---

## Script structure overview

```
g2c.py
├── read_excel_file()
├── print_dataframe_summary()
├── print_first_10_rows()
├── clean_encoding_artifacts()
├── clean_dataframe_encoding()
├── export_to_csv()
├── main()
```

---

## Imports & config

```python
import os
import sys
import argparse
import pandas as pd
from pathlib import Path
```

Pretty standard. No surprises.

```python
DEFAULT_EXCEL_PATH = "input/spreadsheet/metadata.xlsx"
```

This establishes a **convention-based project layout** (HPM projects).

---

## `read_excel_file()`

### Purpose

Load an Excel file into a Pandas DataFrame **as-is**.

### Key behavior

```python
engine = "openpyxl" if excel_path.suffix.lower() == ".xlsx" else "xlrd"
df = pd.read_excel(excel_path, engine=engine)
```

* `.xlsx` → `openpyxl`
* `.xls` → `xlrd`

✅ Correct
⚠️ `xlrd` **no longer supports xlsx** and must be installed separately.

### Validation

* File must exist
* DataFrame must not be empty

### ⚠️ MAJOR ISSUE: Dead / unreachable code

After this:

```python
return df
```

There is **hundreds of lines of unreachable code**:

```python
# Check for duplicate headers ...
# except HttpError as error:
```

This code:

* References undefined variables (`headers`, `data_rows`, `HttpError`)
* Will **never execute**
* Looks copy-pasted from a Google Sheets version

📌 **This is technical debt** and should be deleted or refactored.

---

## `print_dataframe_summary(df)`

Purely diagnostic.

It prints:

* Shape
* Column names
* First 5 rows
* dtypes

This is useful because **column headers don’t actually matter later** — row 3 does.

---

## `print_first_10_rows(df)`

Same idea, but:

* Forces Pandas to show **all columns**
* Useful for visually confirming row 3 mappings

Good debugging helper.

---

## Encoding cleanup

### `clean_encoding_artifacts(text)`

This fixes **classic mojibake**, e.g.:

| Broken | Fixed |
| ------ | ----- |
| `Ã±`   | `ñ`   |
| `â€™`  | `'`   |
| `â€”`  | `—`   |

This happens when:

* UTF-8 is interpreted as Windows-1252
* Common in Excel → CSV → Excel workflows

Also strips:

* Null bytes
* Control characters

👍 Solid defensive code.

---

### `clean_dataframe_encoding(df)`

* Applies the above function to **every object (string) column**
* Converts values to `str`
* Leaves `nan` untouched

⚠️ Minor note: converting everything to `str` can flatten mixed-type columns, but that’s probably intentional here.

---

## `export_to_csv()` — the heart of the script

This is where the real logic lives.

---

### Step 1: Define IPTC mapping

```python
row3_mapping = {
    "Title": "Headline",
    "Accession Number": "ObjectName",
    "Restrictions": "CopyrightNotice",
    "Scopenote": "Caption-Abstract",
    "Related Collection": "Source",
    "Source Photographer": "By-line",
    "Institutional Creator": "By-lineTitle",
}
```

**Important concept:**

> These strings are expected to appear in **row 3 of the spreadsheet**, not as column headers.

---

### Step 2: Scan row 3 to discover meaning

```python
row3_index = 2
```

Row index 2 = Excel row 3.

For every column:

* Look at `df.loc[2, col]`
* If the cell value matches one of the keys → map it

This is clever, but **very format-dependent**.

💡 The spreadsheet is acting like a **self-describing schema**.

---

### Step 3: Handle fuzzy matches

```python
elif "related collection" in cell_value.lower()
```

Allows variations like:

* "Related collections"
* "Related Collection (HPM)"

Nice pragmatic touch.

---

### Step 4: Clean the entire DataFrame

```python
df_cleaned = clean_dataframe_encoding(df)
```

This ensures the exported CSV doesn’t contain mojibake.

---

### Step 5: Build a new DataFrame

```python
new_df = pd.DataFrame()
```

Only mapped columns are copied:

```python
new_df[dst_col] = df_cleaned[src_col]
```

❗ This means:

* Unmapped columns are **discarded**
* Row 1–3 are still present unless filtered later

---

## DateCreated column logic

This part is careful but a little verbose.

### Requirements

Columns must exist:

```python
productionDateMonth
productionDateDay
productionDateYear
```

### Behavior

* Skips rows 0–2 (header rows)
* For rows ≥ 3:

  * Validates numeric date parts
  * Emits `YYYY-MM-DD`
  * Silently skips incomplete dates

Example output:

```
DateCreated = 1984-07-12
```

👍 Correct IPTC format
⚠️ No timezone handling (probably fine)

---

## Export

```python
new_df.to_csv(output_file, index=False, encoding="utf-8")
```

Clean UTF-8 CSV, no index column.

---

## `main()` — CLI glue

### Argument parsing

```python
--excel-file / -f
--export-csv / -e
```

⚠️ **BUG:** Arguments are defined **twice**.

This won’t crash, but it’s sloppy and confusing.

---

### Execution flow

1. Parse arguments
2. Read Excel
3. Print summaries
4. Export CSV (if requested)

---

## Summary: What this code does *well*

✅ Smart use of **row-based semantic metadata**
✅ Defensive Excel reading
✅ Solid encoding cleanup
✅ Clear logging and diagnostics
✅ IPTC-aware date formatting

---

## ⚠️ Issues you should absolutely fix

### 1. Dead code in `read_excel_file`

Remove everything after `return df`.

### 2. Duplicate argparse arguments

Delete the repeated `add_argument()` calls.

### 3. Undefined legacy Google Sheets logic

References to:

* `HttpError`
* `headers`
* `data_rows`

These are leftovers and misleading.

### 4. Hard dependency on row 3 layout

If someone inserts a row above → everything breaks.

(You may want to validate row 3 contents explicitly.)

---

## If you want next steps

I can:

* ✂️ **Refactor this into clean, minimal code**
* 🧪 Add **schema validation** for the spreadsheet
* 🧱 Make row index configurable
* 🧠 Convert this to a **unit-testable pipeline**
* 📦 Turn it into a reusable module

Just tell me how hard you want to go 😄
