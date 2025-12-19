# HSTL Photo Framework

A comprehensive Python framework for managing the complete HSTL Photo Metadata Project workflow.

## Quick Start

```bash
# Initialize a new project (ultra-simple - just provide the name!)
python hstl_framework.py init "January 2025 Batch"

# Or with custom base directory
python hstl_framework.py init "January 2025" --base-dir "D:\MyBatches"

# Or with full custom path
python hstl_framework.py init "January 2025" --data-dir "C:\Custom\Path"

# View current configuration
python hstl_framework.py --config "C:\path\to\images\config\project_config.yaml" config --list

# Update configuration
python hstl_framework.py --config "C:\path\to\images\config\project_config.yaml" config --set project.data_directory "C:\new\path"

# Run the complete workflow
python hstl_framework.py --config "C:\path\to\images\config\project_config.yaml" run --all

# Run specific steps
python hstl_framework.py --config "C:\path\to\images\config\project_config.yaml" run --step 2
python hstl_framework.py --config "C:\path\to\images\config\project_config.yaml" run --steps 2-5

# Check project status
python hstl_framework.py --config "C:\path\to\images\config\project_config.yaml" status
```

## Processing Steps

This framework orchestrates 8 steps of photo metadata processing:

1. **Google Spreadsheet Preparation** - Collaborative spreadsheet setup
2. **CSV Conversion** - Google Worksheet to CSV conversion  
3. **Unicode Filtering** - Text encoding cleanup and validation
4. **TIFF Conversion** - 16-bit to 8-bit TIFF conversion
5. **Metadata Embedding** - Embed metadata into TIFF images
6. **JPEG Conversion** - Convert TIFFs to JPEGs
7. **JPEG Resizing** - Resize JPEGs to 800x800 pixel constraint
8. **Watermarking** - Add watermarks to restricted images

## Project Directory Structure

When you initialize a project with `hstl_framework.py init`, the following directory structure is automatically created:

```
Project Data Directory/
├── input/
│   ├── tiff/              # Original TIFF files (your source images)
│   └── spreadsheet/       # Google Spreadsheet exports
├── output/
│   ├── csv/               # Processed CSV files (Step 2)
│   ├── tiff_processed/    # Processed TIFF files (Step 4)
│   ├── jpeg/              # Converted JPEG files (Step 6)
│   ├── jpeg_resized/      # Resized JPEG files (Step 7)
│   └── jpeg_watermarked/  # Watermarked JPEG files (Step 8)
├── reports/               # Validation and summary reports
├── logs/                  # Processing logs
└── config/
    └── project_config.yaml  # Project configuration file
```

### Usage Notes

- Place your original TIFF images in `input/tiff/`
- Place Google Spreadsheet exports in `input/spreadsheet/`
- Processed outputs will be placed in their respective `output/` subdirectories
- All configuration is managed through `config/project_config.yaml`

## Configuration Management

The framework uses a YAML configuration file to manage project settings. This allows you to:

- Track which steps have been completed
- Configure step-specific parameters (quality, dimensions, etc.)
- Manage paths and validation settings
- Store processing history and metadata

### Viewing Configuration

```bash
python hstl_framework.py --config "path/to/project_config.yaml" config --list
```

### Updating Configuration

You can update any configuration value using dot notation:

```bash
# Update data directory path
python hstl_framework.py --config "path/to/project_config.yaml" config --set project.data_directory "C:\new\path"

# Update step-specific settings
python hstl_framework.py --config "path/to/project_config.yaml" config --set step_configurations.step7.max_dimension 1024

# Update validation settings
python hstl_framework.py --config "path/to/project_config.yaml" config --set validation.strict_mode false
```

### Important Configuration Keys

- `project.name` - Name of your batch/project
- `project.data_directory` - Root path to your data directory
- `steps_completed.stepN` - Boolean flag for each step (1-8)
- `step_configurations.stepN.*` - Step-specific parameters
- `validation.strict_mode` - Enable/disable strict validation

## Multi-Batch Management

The framework supports managing multiple batch projects simultaneously. This is essential for production environments where multiple photo collections are processed in parallel.

### List All Batches

```bash
# Show active batches
python hstl_framework.py batches

# Show all batches (including completed/archived)
python hstl_framework.py batches --all
```

### Batch Lifecycle Commands

```bash
# Get detailed information about a batch
python hstl_framework.py batch info <batch_id>

# Mark batch as completed (removes from active list)
python hstl_framework.py batch complete <batch_id>

# Archive a batch for long-term storage
python hstl_framework.py batch archive <batch_id>

# Reactivate a completed or archived batch
python hstl_framework.py batch reactivate <batch_id>

# Remove batch from registry (preserves all files)
python hstl_framework.py batch remove <batch_id> --confirm
```

### Batch Status States

- **active** - Currently being processed (shown in `batches` list)
- **completed** - All processing finished (shown only in `batches --all`)
- **archived** - Long-term storage (shown only in `batches --all`)

### Retirement Workflow

When you finish processing a batch:

1. Mark as completed: `python hstl_framework.py batch complete january2024`
2. Later, archive: `python hstl_framework.py batch archive january2024`
3. Eventually, remove from tracking: `python hstl_framework.py batch remove january2024 --confirm`
4. Manually delete files if no longer needed

**Note**: Status changes never delete files. Your data is always preserved until you manually delete the directory.

## Development Status

🚧 **Currently in Development** - CLI Phase

### Completed
- ✅ Development plan created
- ✅ Project structure creation
- ✅ Basic CLI interface
- ✅ Configuration management (`init`, `config --list`, `config --set`)
- ✅ Multi-batch registry and tracking
- ✅ Batch lifecycle management (complete, archive, reactivate, remove)
- ✅ Logging system

### In Progress
- ⏳ Step module integration
- ⏳ Validation framework
- ⏳ Pipeline orchestration

### Planned
- 📋 Step implementations (Steps 1-8)
- 📋 Report generation
- 📋 GUI implementation (Phase 2)

## Documentation

- [`docs/DEVELOPMENT_PLAN.md`](docs/DEVELOPMENT_PLAN.md) - Comprehensive development roadmap
- [`docs/GLOSSARY.md`](docs/GLOSSARY.md) - Complete glossary of framework terminology and concepts
- [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) - Step-by-step user guide for the GUI application
- [`docs/GLOSSARY_PLAN.md`](docs/GLOSSARY_PLAN.md) - Development plan for the glossary
- Requirements and dependencies listed in development plan
- Integration strategy for existing Version-2 applications

## Environment

- **Platform**: Windows (PowerShell)
- **Python**: 3.8+
- **Framework Location**: `C:\Users\jimur\Projects\HST-Metadata\Photo\Version-2\Framework\`
- **Data Directories**: Configurable, separate from framework location

---

*This project integrates and orchestrates existing HSTL photo processing applications into a unified workflow management system.*