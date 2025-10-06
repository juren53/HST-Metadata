# HSTL Photo Framework - Development Plan

## Project Overview
The HSTL Photo Framework is an umbrella application that orchestrates all components of the HSTL Photo Metadata Project. It manages the complete 8-step process from Google Spreadsheet preparation through final watermarked JPEG creation.

## Project Structure
```
C:\Users\jimur\Projects\HST-Metadata\Photo\Version-2\Framework\
├── hstl_framework.py          # Main CLI entry point
├── config/
│   ├── __init__.py
│   ├── config_manager.py      # Configuration management
│   └── settings.py            # Default settings
├── steps/
│   ├── __init__.py
│   ├── base_step.py           # Base class for all steps
│   ├── step1_google_sheet.py  # Google Spreadsheet preparation
│   ├── step2_csv_conversion.py # Google WS to CSV conversion
│   ├── step3_unicode_filter.py # Unicode text filtering
│   ├── step4_tiff_conversion.py # TIFF bit depth conversion
│   ├── step5_metadata_embed.py # Metadata embedding
│   ├── step6_jpeg_conversion.py # TIFF to JPEG conversion
│   ├── step7_jpeg_resize.py   # JPEG resizing
│   └── step8_watermark.py     # Watermark addition
├── utils/
│   ├── __init__.py
│   ├── logger.py              # Logging utilities
│   ├── validator.py           # Validation utilities
│   └── file_utils.py          # File operation utilities
├── gui/                       # Future PyQt6 GUI (Phase 2)
│   └── __init__.py
├── requirements.txt           # Python dependencies
├── DEVELOPMENT_PLAN.md        # This file
└── README.md                  # Usage documentation
```

## Process Steps Overview

| Step | Code Package/Process | Validation Required |
|------|---------------------|-------------------|
| 1 | Prepare Collaborative Google Spreadsheet | Confirm Title, Description, AN, Date, Rights, Photographer, & Organization are completed |
| 2 | Convert Google WS to CSV file (`g2c.py`, `gui_b2c.py`) | Number of rows in CSV should match number of Accession Numbers |
| 3 | Unicode filtering (`analyze.py`, `fix.py`) | Post-processing Summary Reports highlight problems |
| 4 | Test & convert 16-bit TIFFs to 8-bit | Bit depth validation |
| 5 | Embed metadata into TIFF images (`write_tags.py`) | Post-processing Summary Report, spot check with nomacs/tagwriter |
| 6 | Convert TIFFs to JPEGs | TIFF count should match JPEG count |
| 7 | Resize JPEGs to 800x800 box | Spot check dimensions |
| 8 | Add watermarks to restricted JPEGs | Spot check watermark application |

## Existing Applications to Integrate

### Available in Version-2:
- **Step 2**: `g2c.py` (multiple locations), `g2c_gui.py` 
- **Step 3**: `analyze_utf8.py`, `fix_special_characters.py`, `fix_unicode.py`, `fix_encoding.py`
- **Step 5**: `write-tags-from-csv.py`

### Version-1 Reference Code:
- JPEG conversion and resizing logic (Steps 6-7)
- Watermarking functionality (Step 8)
- General utilities for file operations

## Development Phases

### Phase 1: Core Framework & CLI (Current)
1. **Framework Architecture**
   - Main CLI entry point with argparse
   - Configuration management system
   - Project initialization and tracking
   - Data directory management
   - Logging and reporting system

2. **Step Integration** (Priority Order)
   - Step 2: CSV conversion (integrate existing `g2c.py`)
   - Step 3: Unicode filtering (integrate existing analyze/fix utilities)
   - Step 5: Metadata embedding (integrate existing `write_tags.py`)
   - Step 4: TIFF conversion (new implementation)
   - Step 6: TIFF to JPEG conversion (adapt from Version 1)
   - Step 7: JPEG resizing (adapt from Version 1)
   - Step 8: Watermarking (adapt from Version 1)
   - Step 1: Google Spreadsheet preparation (new implementation)

3. **Validation & Quality Assurance**
   - File count validation
   - Metadata verification utilities
   - Image dimension checking
   - Summary report generation

### Phase 2: GUI Implementation (Future)
- PyQt6 interface development
- Visual progress tracking
- Interactive configuration
- Integrated file browser
- Real-time validation feedback

## CLI Interface Design

### Core Commands
```bash
# Project Management
hstl_framework.py init --data-dir "C:\path\to\images" --project-name "MyProject"
hstl_framework.py config --list
hstl_framework.py config --set data_dir "C:\new\path"

# Step Execution
hstl_framework.py run --step 1              # Run single step
hstl_framework.py run --steps 1-3           # Run range of steps
hstl_framework.py run --steps 2,5,7         # Run specific steps
hstl_framework.py run --all                 # Run all steps
hstl_framework.py run --from 3              # Run from step 3 onwards
hstl_framework.py run --continue            # Continue from last completed step

# Status and Validation
hstl_framework.py status                    # Show project status
hstl_framework.py status --verbose          # Detailed status
hstl_framework.py validate --step 5         # Validate specific step
hstl_framework.py validate --all            # Validate all completed steps

# Reporting
hstl_framework.py report --step 3           # Generate step report
hstl_framework.py report --summary          # Overall project summary
hstl_framework.py report --export csv       # Export report to CSV
```

### Configuration Options
```bash
# Step-specific configurations
hstl_framework.py config --step 7 --set max_dimension 800
hstl_framework.py config --step 8 --set watermark_opacity 0.3

# Global settings
hstl_framework.py config --set log_level DEBUG
hstl_framework.py config --set parallel_processing true
```

## Data Directory Management

### Directory Structure
```
Project Data Directory/
├── input/
│   ├── tiff/                  # Original TIFF files
│   └── spreadsheet/           # Google Spreadsheet exports
├── output/
│   ├── csv/                   # Processed CSV files
│   ├── tiff_processed/        # Processed TIFF files
│   ├── jpeg/                  # Converted JPEG files
│   ├── jpeg_resized/          # Resized JPEG files
│   └── jpeg_watermarked/      # Watermarked JPEG files
├── reports/                   # Step reports and summaries
├── logs/                      # Processing logs
└── config/                    # Project-specific configuration
```

### Configuration File (project_config.yaml)
```yaml
project:
  name: "HSTL_Project_2024"
  created: "2024-10-06T14:00:00Z"
  data_directory: "C:\\Data\\HSTL_Photos\\Project_2024"
  
steps_completed:
  step1: false
  step2: true
  step3: true
  # ... etc

step_configurations:
  step7:
    max_dimension: 800
    quality: 85
  step8:
    watermark_opacity: 0.3
    watermark_position: "bottom_right"

validation:
  strict_mode: true
  auto_backup: true
```

## Implementation Strategy

### Development Order
1. **Core Framework Setup**
   - Project structure creation
   - Basic CLI interface
   - Configuration management
   - Logging system

2. **Step Modules (Incremental)**
   - Start with existing applications (Steps 2, 3, 5)
   - Create wrapper modules for integration
   - Add validation and reporting
   - Test each step independently

3. **Integration Testing**
   - End-to-end workflow testing
   - Data directory management
   - Error handling and recovery
   - Performance optimization

4. **Documentation & Polish**
   - User documentation
   - Developer documentation
   - Error message improvements
   - CLI help system enhancement

### Key Design Principles
- **Modularity**: Each step is independent and can be run separately
- **Configurability**: All settings can be customized per project
- **Reliability**: Comprehensive validation and error handling
- **Transparency**: Detailed logging and reporting at each step
- **Extensibility**: Easy to add new steps or modify existing ones
- **Data Safety**: Automatic backups and non-destructive operations where possible

## Dependencies
- Python 3.8+
- PyQt6 (Phase 2)
- Pillow (image processing)
- pandas (CSV/data handling)
- PyYAML (configuration)
- colorama (CLI colors)
- tqdm (progress bars)
- pathlib (path handling)

## Testing Strategy
- Unit tests for each step module
- Integration tests for workflow
- Sample data sets for validation
- Performance benchmarking
- Cross-platform compatibility (Windows focus)

## Risk Mitigation
- **Data Loss Prevention**: Automatic backups before destructive operations
- **Error Recovery**: Ability to resume from any step
- **Validation Failures**: Clear error messages and remediation guidance
- **Performance Issues**: Parallel processing options and progress tracking
- **Configuration Errors**: Validation of all configuration parameters

---

## Next Steps
1. Create basic project structure
2. Implement core CLI framework
3. Integrate Step 2 (CSV conversion) as proof of concept
4. Add configuration management
5. Implement logging and basic reporting
6. Continue with remaining steps in priority order

## Notes
- Version 1 code serves as reference only
- Focus on integration of existing working Version-2 applications
- CLI implementation first, GUI in Phase 2
- Windows PowerShell environment
- Data directories separate from framework code location