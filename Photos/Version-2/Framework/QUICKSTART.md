# HSTL Framework Quick Start Guide

## Prerequisites

- Python 3.8 or higher
- All dependencies installed: `pip install -r requirements.txt`

## Setting Up a New Batch Project

### Step 1: Initialize the Project

Initialize the framework with just the project name! The directory will be created automatically:

```powershell
# Simple - just provide the batch name
python hstl_framework.py init "December 2024 Batch"

# This creates: C:\Data\HSTL_Batches\December_2024_Batch
```

Optional: Specify a different location:
```powershell
# Use a different base directory
python hstl_framework.py init "December 2024" --base-dir "D:\MyBatches"

# Or specify the full path
python hstl_framework.py init "December 2024" --data-dir "C:\Custom\Dec2024"
```

This will:
- Create the data directory if it doesn't exist
- Create all necessary subdirectories (input/, output/, logs/, reports/, config/)
- Generate a project configuration file at `config/project_config.yaml`
- Register the batch in the framework registry

### Step 2: Add Your Source Files
- A project configuration file at `config/project_config.yaml`

### Step 3: Add Your Source Files

Place your files in the appropriate input directories:

```powershell
# Copy your TIFF images
Copy-Item "C:\path\to\your\*.tif" "C:\Data\HSTL_Batches\Batch_2024_December\input\tiff\"

# Copy your Google Spreadsheet export (when ready)
Copy-Item "C:\path\to\metadata.csv" "C:\Data\HSTL_Batches\Batch_2024_December\input\spreadsheet\"
```

### Step 3: Review Configuration

View your current project configuration:

```powershell
python hstl_framework.py --config "C:\Data\HSTL_Batches\Batch_2024_December\config\project_config.yaml" config --list
```

### Step 4: Customize Settings (Optional)

Adjust configuration values as needed:

```powershell
# Change JPEG quality for Step 6
python hstl_framework.py --config "C:\Data\HSTL_Batches\Batch_2024_December\config\project_config.yaml" config --set step_configurations.step6.quality 90

# Change resize dimension for Step 7
python hstl_framework.py --config "C:\Data\HSTL_Batches\Batch_2024_December\config\project_config.yaml" config --set step_configurations.step7.max_dimension 1024

# Adjust watermark opacity for Step 8
python hstl_framework.py --config "C:\Data\HSTL_Batches\Batch_2024_December\config\project_config.yaml" config --set step_configurations.step8.watermark_opacity 0.25
```

### Step 5: Check Project Status

View the current processing status:

```powershell
python hstl_framework.py --config "C:\Data\HSTL_Batches\Batch_2024_December\config\project_config.yaml" status
```

### Step 6: Run Processing Steps

Execute the processing workflow:

```powershell
# Run all steps in sequence
python hstl_framework.py --config "C:\Data\HSTL_Batches\Batch_2024_December\config\project_config.yaml" run --all

# Or run steps individually
python hstl_framework.py --config "C:\Data\HSTL_Batches\Batch_2024_December\config\project_config.yaml" run --step 2

# Or run a range of steps
python hstl_framework.py --config "C:\Data\HSTL_Batches\Batch_2024_December\config\project_config.yaml" run --steps 2-5

# Dry run to validate without execution
python hstl_framework.py --config "C:\Data\HSTL_Batches\Batch_2024_December\config\project_config.yaml" run --all --dry-run
```

## Typical Workflow

1. **Initialize batch** - Set up directory structure and configuration
2. **Add source files** - Place TIFF images and spreadsheet data in input directories
3. **Review configuration** - Verify settings are appropriate for this batch
4. **Run Steps 1-3** - Prepare spreadsheet, convert to CSV, filter Unicode
5. **Run Step 4** - Convert TIFF bit depth if needed
6. **Run Step 5** - Embed metadata into TIFFs
7. **Run Steps 6-7** - Convert to JPEG and resize
8. **Run Step 8** - Add watermarks to restricted images
9. **Review reports** - Check validation reports in the `reports/` directory
10. **Deliver outputs** - Retrieve processed files from `output/` subdirectories
11. **Disposition of batch data**  - Archive or Delete workflow artifacts

## Directory Reference

After initialization, your project directory will look like:

```
Batch_2024_December/
├── input/
│   ├── tiff/              ← Place your source TIFF images here
│   └── spreadsheet/       ← Save Google Worksheet URL here
├── output/
│   ├── csv/               → export.csv saved here  (Step 2)
│   ├── tiff_processed/    → Processed TIFFs (Step 4)
│   ├── jpeg/              → JPEG conversions (Step 6)
│   ├── jpeg_resized/      → Resized JPEGs (Step 7)
│   └── jpeg_watermarked/  → Watermarked JPEGs (Step 8)
├── reports/               → Validation and processing reports
├── logs/                  → Processing logs
└── config/
    └── project_config.yaml → Project configuration
```

## Managing Multiple Batches

### Viewing All Batches

See all your active batches at a glance:

```powershell
# List active batches
python hstl_framework.py batches

# List all batches (including completed and archived)
python hstl_framework.py batches --all
```

### Viewing Batch Details

Get detailed information about a specific batch:

```powershell
python hstl_framework.py batch info december2024batch
```

This shows:
- Batch name, ID, and status
- Creation and last accessed dates
- Data directory and config file locations
- Progress (X/8 steps completed)
- Individual step status

## Retiring Batches

When you've finished processing a batch, you should retire it to keep your active batch list clean.

### Step 1: Mark as Completed

Once all 8 steps are done, mark the batch as completed:

```powershell
# Get the batch ID from the batches list
python hstl_framework.py batches

# Mark as completed (removes from active list)
python hstl_framework.py batch complete december2024batch
```

### Step 2: Archive (Optional)

For long-term storage, archive the batch:

```powershell
python hstl_framework.py batch archive december2024batch
```

### Step 3: Remove from Registry (Optional)

When you no longer need to track the batch:

```powershell
# Shows confirmation prompt with details
python hstl_framework.py batch remove december2024batch

# Actually remove after confirming
python hstl_framework.py batch remove december2024batch --confirm
```

**Important:** This only removes the batch from tracking. All files remain on disk.

### Step 4: Delete Files (Manual)

If you want to delete the actual files:

```powershell
# Manually delete the directory
Remove-Item "C:\Data\HSTL_Batches\December_2024_Batch" -Recurse -Force
```

### Batch Lifecycle Summary

1. **active** → Working on the batch (default state)
2. **completed** → All processing finished
3. **archived** → Long-term storage, not actively working
4. **removed** → Untracked by framework (files still exist)
5. **deleted** → Files permanently removed (manual action)

### Reactivating a Batch

If you need to work on a completed or archived batch again:

```powershell
python hstl_framework.py batch reactivate december2024batch
```

## Common Configuration Changes

### JPEG Processing

### Resize Dimensions

Default is 800×800 maximum dimension:

```powershell
python hstl_framework.py --config "path\to\project_config.yaml" config --set step_configurations.step7.max_dimension 1024
```

### Watermark Settings

Apply if the image is `Restricted`:

```powershell
python hstl_framework.py --config "path\to\project_config.yaml" config --set step_configurations.step8.watermark_opacity 0.5
python hstl_framework.py --config "path\to\project_config.yaml" config --set step_configurations.step8.watermark_position "bottom_left"
```

### Validation Mode

Toggle strict validation:

```powershell
python hstl_framework.py --config "path\to\project_config.yaml" config --set validation.strict_mode false
```

## Tips

- Always use absolute paths for directories and configuration files
- Run `status` frequently to track progress
- Check the `logs/` directory if you encounter errors
- Use `--dry-run` to validate your setup before processing
- Each step generates a report in the `reports/` directory

## Need Help?

- Review [`README.md`](README.md) for detailed documentation
- See [`DEVELOPMENT_PLAN.md`](DEVELOPMENT_PLAN.md) for architecture details
- Check processing logs in your project's `logs/` directory

Last updated: 2025-11-30  15:16
