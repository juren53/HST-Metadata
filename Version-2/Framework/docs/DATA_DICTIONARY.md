### Project Data Dictionary

This document outlines the key data structures used in the HSTL Photo Framework. The architecture is centered around a "batch," which represents a single processing job.

---

### 1. Batch Registry (`batch_registry.yaml`)

This file acts as a central inventory of all known processing batches. It is a YAML file containing a dictionary where each key is a unique batch name.

| Field | Data Type | Description |
| :--- | :--- | :--- |
| `name` | string | The unique identifier for the batch. This is the key in the top-level dictionary. |
| `data_directory` | string | The absolute path to the root directory where the batch's data is stored. |
| `config_path` | string | The absolute path to the batch's specific configuration file (`project.yaml`). |
| `status` | string | The current high-level status of the batch (e.g., "New", "In Progress", "Completed"). |

---

### 2. Batch Configuration (`project.yaml`)

Each batch has its own `project.yaml` file, which stores all its parameters and step-specific settings. This file is the "single source of truth" for a batch's configuration.

| Section | Field | Data Type | Description |
| :--- | :--- | :--- | :--- |
| **Project Info**| `project_name`| string | The display name of the project or batch. |
| | `project_description`| string | A short description of the batch. |
| | `creation_date`| string | The date and time when the batch was created. |
| | `version`| string | The framework version used to create the batch. |
| **Directory Paths**| `data_dir` | string | Root directory for all data associated with this batch. |
| | `input_dir` | string | Subdirectory for input files. |
| | `output_dir` | string | Subdirectory for output files. |
| | `log_dir` | string | Subdirectory for log files. |
| | `config_dir` | string | Subdirectory for configuration files. |
| **Step Status** | `step_1_completed`| boolean | `true` if Step 1 has been successfully completed. |
| | `step_2_completed`| boolean | `true` if Step 2 has been successfully completed. |
| | ... (and so on for all 8 steps) | | |
| **Step 1 Config**| `worksheet_url`| string | The URL of the Google Sheet to be processed. |
| **(Other Steps)**| ... | ... | Each step can have its own section with specific parameters. |

---

### 3. In-Memory Processing Context (`ProcessingContext`)

This is a Python object that acts as a live "data bus" during a pipeline run. It is created when a pipeline is started and is passed sequentially to each step, allowing them to share data.

| Attribute | Data Type | Description |
| :--- | :--- | :--- |
| `config` | `ConfigManager` | An object that holds the entire loaded `project.yaml` for the current batch. |
| `paths` | `PathManager` | An object that provides easy access to the various directory paths for the batch. |
| `shared_data` | `dict` | A dictionary used to pass data between pipeline steps. For example, Step 1 might place a pandas DataFrame here, and Step 2 would then access and process it. |
| `logger` | `Logger` | The logger instance for the current pipeline run. |

---

### 4. Photo Metadata (from CSV / `g2c.py` processing)

This section describes the structure of the photo metadata processed by the framework, typically originating from a CSV file (often derived from a Google Sheet). The `g2c.py` script maps raw spreadsheet column headers (identified from a specific row, often row 3) to standard IPTC (International Press Telecommunications Council) metadata fields.

| Spreadsheet Column (Row 3 Value) | Mapped IPTC Field | Data Type | Description |
| :------------------------------- | :---------------- | :-------- | :---------- |
| `Title` | `Headline` | string | A brief heading or title for the image. |
| `Accession Number` | `ObjectName` | string | A unique identifier for the object or image. |
| `Restrictions` | `CopyrightNotice` | string | Any copyright or usage restrictions. |
| `Scopenote` | `Caption-Abstract` | string | A textual description of the image content. |
| `Related Collection` | `Source` | string | The original owner or provider of the image. |
| `Source Photographer` | `By-line` | string | The name of the photographer or creator. |
| `Institutional Creator` | `By-lineTitle` | string | The title or role of the institutional creator. |
| `productionDateMonth` | (internal, for `DateCreated`) | string (numeric) | The month component of the creation date. |
| `productionDateDay` | (internal, for `DateCreated`) | string (numeric) | The day component of the creation date. |
| `productionDateYear` | (internal, for `DateCreated`) | string (numeric) | The year component of the creation date. |
| *(Composite)* | `DateCreated` | string (ISO YYYY-MM-DD) | The full date the image was created, derived from `productionDateMonth`, `productionDateDay`, and `productionDateYear`. |