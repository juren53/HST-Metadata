# HPM - HSTL Photo Metadata Framework

A Python/PyQt6 GUI application for managing the complete HSTL Photo Metadata Project workflow. HPM orchestrates an 8-step pipeline that transforms raw TIFF images and Excel metadata spreadsheets into watermarked, metadata-embedded JPEG deliverables.

**Current version: 1.9.0**

## Getting HPM

### Option 1: Download HPM.exe (Recommended)

Download the latest pre-built Windows executable from the GitHub Releases page:

```
https://github.com/juren53/HST-Metadata/releases
```

Download `HPM.exe` from the latest release, place it where you want to run it from, and double-click to launch. No Python installation required.

### Option 2: Run from Source (Python)

For developers or users who prefer to run the Python source code directly. See [`INSTALLATION.md`](INSTALLATION.md) for full instructions.

## Using the Application

Launch `HPM.exe` from anywhere on your C: drive. It is recommended you move it to a directory that is in your PATH.

The main window has four areas:

- **Batches Tab** - Lists all batch projects with status and progress
- **Current Batch Tab** - Shows the 8 processing steps for the selected batch
- **Configuration Tab** - Displays the current batch configuration
- **Log Viewer** - Real-time log messages and processing output

See [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) for a complete walkthrough.

## Processing Steps

HPM orchestrates 8 steps of photo metadata processing:

| Step | Name | Description |
|------|------|-------------|
| 1 | Excel Spreadsheet Preparation | Select and validate an Excel (.xlsx) metadata spreadsheet |
| 2 | CSV Conversion | Convert Excel spreadsheet to CSV format |
| 3 | Unicode Filtering | Text encoding cleanup and mojibake repair |
| 4 | TIFF Conversion | Select TIFF source images; convert 16-bit to 8-bit if needed |
| 5 | Metadata Embedding | Embed IPTC/EXIF metadata into TIFF images using ExifTool |
| 6 | JPEG Conversion | Convert processed TIFFs to JPEG |
| 7 | JPEG Resizing | Resize JPEGs to 800x800 pixel maximum dimension |
| 8 | Watermarking | Add watermarks to images flagged as restricted |

## Project Directory Structure

When you create a new batch, HPM generates this directory structure automatically:

```
[BatchName]/
├── input/
│   ├── tiff/              <- Source TIFF images (selected in Step 4)
│   └── spreadsheet/       <- Excel metadata file (selected in Step 1)
├── output/
│   ├── csv/               -> Exported CSV (Step 2)
│   ├── tiff_processed/    -> Processed TIFFs (Step 4)
│   ├── jpeg/              -> JPEG conversions (Step 6)
│   ├── jpeg_resized/      -> Resized JPEGs (Step 7)
│   └── jpeg_watermarked/  -> Watermarked JPEGs (Step 8)
├── reports/               -> Validation and processing reports
├── logs/                  -> Processing logs
└── config/
    └── project_config.yaml  <- Batch configuration file
```

## Environment

- **Platform**: Windows 11 (the target envirnoment) 

## Documentation

- [`INSTALLATION.md`](INSTALLATION.md) - Complete installation guide
- [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) - Step-by-step user guide for the GUI
- [`docs/QUICKSTART.md`](docs/QUICKSTART.md) - Quick start reference
- [`docs/CLI_REFERENCE.md`](docs/CLI_REFERENCE.md) - Command-line interface reference
- [`docs/GLOSSARY.md`](docs/GLOSSARY.md) - Glossary of framework terminology
- [`docs/DATA_DICTIONARY.md`](docs/DATA_DICTIONARY.md) - Data dictionary for metadata fields
- [`docs/PROCEDURE_HPM-download-specific-version.md`](docs/PROCEDURE_HPM-download-specific-version.md) - How to download a specific version
- [`launcher/LAUNCHER_README.md`](launcher/LAUNCHER_README.md) - HPM Launcher documentation (WinPython)

---

*HPM integrates and orchestrates the HSTL photo processing pipeline into a unified workflow management application.*
