# HSTL Photo Framework - Development Plan

## Project Overview

The HSTL Photo Framework is an umbrella application that orchestrates all components of the HSTL Photo Metadata Project. It manages the complete 8-step process from Google Spreadsheet preparation through final watermarked JPEG creation.

## Repository Information

- **GitHub Repository**: https://github.com/juren53/HST-Metadata
- **Framework Branch**: `master` (main branch)
- **Development Branch**: `framework-setup` (development work)
- **Local Repository**: `C:\Users\jimur\Projects\HST-Metadata`
- **Framework Path**: `Photos/Version-2/Framework/`
- **GitHub URL**: https://github.com/juren53/HST-Metadata/tree/master/Photos/Version-2/Framework
- **Current Status**: Core framework implemented and deployed to master branch

## Project Structure

```
C:\Users\jimur\Projects\HST-Metadata\Photos\Version-2\Framework\
├── hstl_framework.py              # Main CLI entry point
├── config/
│   ├── __init__.py
│   ├── config_manager.py          # Configuration management
│   └── settings.py                # Default settings
├── steps/
│   ├── __init__.py
│   ├── base_step.py               # Base class for all steps
│   ├── step1_google_sheet.py      # Google Spreadsheet preparation
│   ├── step2_csv_conversion.py    # Google WS to CSV conversion
│   ├── step3_unicode_filter.py    # Unicode text filtering
│   ├── step4_tiff_conversion.py   # TIFF bit depth conversion
│   ├── step5_metadata_embed.py    # Metadata embedding
│   ├── step6_jpeg_conversion.py   # TIFF to JPEG conversion
│   ├── step7_jpeg_resize.py       # JPEG resizing
│   └── step8_watermark.py         # Watermark addition
├── utils/
│   ├── __init__.py
│   ├── logger.py                  # Logging utilities
│   ├── validator.py               # Validation utilities
│   ├── file_utils.py              # File operation utilities
│   ├── path_manager.py            # Path management utilities
│   └── batch_registry.py          # Multi-batch registry management
├── core/
│   ├── __init__.py
│   └── pipeline.py                # Pipeline orchestration system
├── gui/                           # Future PyQt6 GUI (Phase 2)
│   └── __init__.py
├── requirements.txt               # Python dependencies
├── docs/DEVELOPMENT_PLAN.md            # This file
└── README.md                      # Usage documentation
```

## Architecture & Best Practices

### Core Architecture Patterns

#### Plugin/Extension Architecture

- **Modular Design**: Each step (1-8) is a separate, self-contained module
- **Common Interface**: All step implementations inherit from a base `StepProcessor` class
- **Extensibility**: Easy to add, remove, or replace individual steps without affecting others
- **Isolation**: Each step operates independently with clear input/output contracts

#### Pipeline/Workflow Pattern

- **Data Flow**: Model the 8-step process as a pipeline where data flows through stages
- **Stage Validation**: Each stage validates its inputs before execution
- **Checkpoints**: Validation points between stages (matching "Checking and Validation" requirements)
- **State Tracking**: Maintain processing state throughout the pipeline

#### Configuration-Driven Design

- **External Configuration**: Store all settings in YAML/TOML config files
- **Path Management**: Keep data directory paths separate from code
- **Step Parameters**: Configurable validation rules and processing parameters
- **Environment Flexibility**: Easy deployment across different environments

#### Multi-Batch Registry Pattern

- **Centralized Tracking**: Single registry tracks all batch projects across the framework
- **Batch Isolation**: Each batch has independent configuration and data directories
- **Progress Visibility**: View status and progress of all batches from any location
- **Automatic Registration**: Batches auto-register on creation, no manual tracking needed
- **Status Management**: Track batch lifecycle (active, completed, archived)

### Key Technical Practices

#### State Management

- **Progress Tracking**: Track completion status of each step for each photo collection
- **Resume Capability**: Store processing state to resume interrupted workflows
- **History Logging**: Maintain detailed logs of processing history, timestamps, and errors
- **Rollback Support**: Ability to revert to previous states when needed

#### Path Management System

```python
class PathManager:
    - framework_root: Framework installation directory
    - input_tiff_dir: Source TIFF image directory
    - output_jpeg_dir: Processed JPEG output directory
    - working_dir: Temporary processing directory
    - logs_dir: Log file storage location
    - config_dir: Configuration file directory
    - reports_dir: Validation and summary reports
```

#### Batch Registry System

```python
class BatchRegistry:
    """Centralized registry for tracking multiple batch projects"""
    - registry_path: Path to central batch_registry.yaml
    - batches: Dictionary of all registered batches
    
    # Core Operations
    def register_batch(name, data_dir, config_path) -> bool
    def unregister_batch(batch_id) -> bool
    def get_batch_summary(batch_id) -> Dict  # Includes step completion status
    def list_batches_summary() -> List[Dict]  # All batches with progress
    
    # Query Operations
    def get_active_batches() -> Dict
    def find_batch_by_name(name) -> Tuple[batch_id, info]
    def find_batch_by_config(config_path) -> Tuple[batch_id, info]
    
    # Lifecycle Management
    def update_batch_status(batch_id, status) -> bool  # status: active/completed/archived
    def update_last_accessed(batch_id) -> bool
```

**Batch Status Values:**
- `active` - Currently being processed (default)
- `completed` - All processing finished
- `archived` - Long-term storage

**Registry Storage**: `Framework/config/batch_registry.yaml`
- Persists across framework sessions
- Stores batch metadata (name, paths, creation time, status)
- Automatically updated on batch operations

#### Context Object Pattern

- **Pipeline Context**: Pass a context object through all processing stages
- **Shared Resources**: Contains paths, configuration, and shared utilities
- **Error Handling**: Centralized error collection and reporting
- **Progress Reporting**: Real-time status updates throughout the pipeline

#### Validation & Error Handling

- **Pre-flight Checks**: Validate inputs and environment before each step
- **Clear Error Messages**: Actionable guidance for error resolution
- **Summary Reports**: Detailed reports after each step completion
- **Dry-run Mode**: Validation without making changes (--dry-run flag)
- **Graceful Degradation**: Continue processing when non-critical errors occur

#### Quality Assurance

- **File Count Validation**: Ensure expected number of files at each stage
- **Metadata Verification**: Validate embedded metadata against source data
- **Image Quality Checks**: Verify dimensions, bit depth, and format correctness
- **Automated Testing**: Unit tests for each step module
- **Integration Testing**: End-to-end workflow validation

## Process Steps Overview

| Step | Code Package/Process                                   | Validation Required                                                                      |
| ---- | ------------------------------------------------------ | ---------------------------------------------------------------------------------------- |
| 1    | Prepare Collaborative Google Spreadsheet               | Confirm Title, Description, AN, Date, Rights, Photographer, & Organization are completed |
| 2    | Convert Google WS to CSV file (`g2c.py`, `gui_b2c.py`) | Number of rows in CSV should match number of Accession Numbers                           |
| 3    | Unicode filtering (`analyze.py`, `fix.py`)             | Post-processing Summary Reports highlight problems                                       |
| 4    | Test & convert 16-bit TIFFs to 8-bit                   | Bit depth validation                                                                     |
| 5    | Embed metadata into TIFF images (`write_tags.py`)      | Post-processing Summary Report, spot check with nomacs/tagwriter                         |
| 6    | Convert TIFFs to JPEGs                                 | TIFF count should match JPEG count                                                       |
| 7    | Resize JPEGs to 800x800 box                            | Spot check dimensions                                                                    |
| 8    | Add watermarks to restricted JPEGs                     | Spot check watermark application                                                         |

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

## Framework Implementation Architecture

### Core Classes Structure

```python
class StepProcessor(ABC):
    """Base class for all step implementations"""
    @abstractmethod
    def validate_inputs(self, context: ProcessingContext) -> ValidationResult
    @abstractmethod
    def execute(self, context: ProcessingContext) -> StepResult
    @abstractmethod
    def validate_outputs(self, context: ProcessingContext) -> ValidationResult

class ProcessingContext:
    """Shared context passed through the pipeline"""
    paths: PathManager
    config: ConfigManager
    logger: Logger
    state: StateManager
    current_step: int

class Pipeline:
    """Main pipeline orchestrator"""
    def __init__(self, steps: List[StepProcessor], context: ProcessingContext)
    def run(self, start_step: int = 1, end_step: int = 8) -> PipelineResult
    def validate_all(self) -> ValidationReport
    def resume_from_checkpoint(self) -> PipelineResult
```

### Step Implementation Pattern

```python
class Step2_CSVConversion(StepProcessor):
    """CSV conversion step integrating existing g2c.py"""

    def validate_inputs(self, context):
        # Check for Google Spreadsheet files
        # Validate spreadsheet format and accessibility
        return ValidationResult()

    def execute(self, context):
        # Integrate existing g2c.py functionality
        # Convert spreadsheet to CSV
        # Generate processing report
        return StepResult()

    def validate_outputs(self, context):
        # Verify CSV file creation
        # Check row count matches expectations
        return ValidationResult()
```

## CLI Interface Design

### Core Commands

```bash
# Project Management
hstl_framework.py init --data-dir "C:\path\to\images" --project-name "MyProject"
hstl_framework.py config --list
hstl_framework.py config --set data_dir "C:\new\path"

# Multi-Batch Management
hstl_framework.py batches                  # List all active batches
hstl_framework.py batches --all            # List all batches (including archived)

# Batch Lifecycle Management
hstl_framework.py batch info <batch_id>              # Show detailed batch information
hstl_framework.py batch complete <batch_id>          # Mark batch as completed
hstl_framework.py batch archive <batch_id>           # Archive a batch
hstl_framework.py batch reactivate <batch_id>        # Reactivate archived/completed batch
hstl_framework.py batch remove <batch_id> --confirm  # Remove from registry (preserves files)

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

# Pipeline Management (Best Practices)
hstl_framework.py pipeline --dry-run        # Validate entire pipeline without execution
hstl_framework.py pipeline --resume         # Resume from last checkpoint
hstl_framework.py pipeline --rollback 5     # Rollback to state before step 5
hstl_framework.py state --checkpoint         # Create manual checkpoint
hstl_framework.py state --history           # Show processing history

# Advanced Validation
hstl_framework.py validate --pre-flight     # Check all requirements before starting
hstl_framework.py validate --paths          # Validate all directory paths
hstl_framework.py validate --dependencies   # Check external tool dependencies
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
Project Data Directory/ (Per Batch)
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
    └── project_config.yaml    # Batch configuration file

Framework Directory/ (Shared)
└── config/
    └── batch_registry.yaml    # Central registry of all batches
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

## Multi-Batch Workflow

### Use Case: Managing Multiple Concurrent Batches

The framework is designed to handle multiple batch projects simultaneously. This is essential for production environments where:
- Multiple photo collections are processed in parallel
- Batches are at different stages of completion
- Users need to track progress across all active work

### Workflow Example

```bash
# Initialize multiple batches (directories created automatically)
python hstl_framework.py init --data-dir "C:\Data\Batch_2024_January" --project-name "January2024"

python hstl_framework.py init --data-dir "C:\Data\Batch_2024_February" --project-name "February2024"

python hstl_framework.py init --data-dir "C:\Data\Batch_2024_March" --project-name "March2024"

# View all batches at a glance
python hstl_framework.py batches
# Output shows:
# - Batch names and IDs
# - Progress: X/8 steps (percentage)
# - Status: active/completed/archived
# - Data directory locations

# Work on specific batch
python hstl_framework.py --config "C:\Data\Batch_2024_January\config\project_config.yaml" run --step 2

# Check status of specific batch
python hstl_framework.py --config "C:\Data\Batch_2024_January\config\project_config.yaml" status

# Return to overview of all batches
python hstl_framework.py batches
```

### Batch Registry Features

1. **Automatic Registration**: Batches are automatically registered when created with `init`
2. **Progress Tracking**: Shows completion status (0/8, 3/8, 8/8) for each batch
3. **Visual Indicators**:
   - ⭕ Not started (0%)
   - 🔄 In progress (1-99%)
   - ✅ Completed (100%)
4. **Sorting**: Batches sorted by last accessed (most recent first)
5. **Filtering**: View only active batches or all batches including archived
6. **Lifecycle Management**: Mark batches as completed, archived, or reactivate them
7. **Safe Removal**: Unregister batches from tracking without deleting files
8. **Detailed Information**: View complete batch details including all step statuses

### Batch Lifecycle States

- **active**: Currently being processed (default state)
- **completed**: All 8 steps finished, ready for delivery
- **archived**: Long-term storage, not actively worked on

### Batch Retirement Workflow

When processing is complete, retire batches using lifecycle commands:

```bash
# 1. Verify batch is complete
hstl_framework.py batch info january2024

# 2. Mark as completed (removes from active list)
hstl_framework.py batch complete january2024

# 3. Later, archive for long-term storage
hstl_framework.py batch archive january2024

# 4. Eventually, remove from registry (files preserved)
hstl_framework.py batch remove january2024 --confirm

# 5. Manually delete files if no longer needed
Remove-Item "C:\Data\Batch_Jan" -Recurse -Force
```

**Key Points:**
- `complete` and `archive` remove batch from active list but keep in registry
- `remove` unregisters batch but preserves all files
- Files are never automatically deleted
- `reactivate` can restore any completed/archived batch to active status
- View completed/archived batches with `batches --all`

## Implementation Strategy

### Development Order

1. **Core Framework Setup** ✅ COMPLETED
   
   - ✅ Project structure creation
   - ✅ Basic CLI interface (argparse with subcommands)
   - ✅ Configuration management (YAML-based with dot notation)
   - ✅ Logging system
   - ✅ Multi-batch registry system
   - ✅ Path management utilities

2. **Step Modules (Incremental)** 🔄 IN PROGRESS
   
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

- **Modularity**: Each step is independent and can be run separately (Plugin Architecture)
- **Configurability**: All settings can be customized per project (Configuration-Driven Design)
- **Multi-Batch Support**: Concurrent management of multiple photo batches with centralized tracking
- **Reliability**: Comprehensive validation and error handling (Quality Assurance)
- **Transparency**: Detailed logging and reporting at each step (State Management)
- **Extensibility**: Easy to add new steps or modify existing ones (Plugin Architecture)
- **Data Safety**: Automatic backups and non-destructive operations where possible
- **Lifecycle Safety**: Batch status changes never delete files; manual deletion required
- **Pipeline Flow**: Sequential data processing with validation checkpoints
- **Context-Aware**: Centralized resource and state management throughout processing
- **Resume-able**: Ability to restart from any step without losing progress
- **Batch Isolation**: Each batch maintains independent configuration and data directories

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
- ## Risk Mitigation

- **Data Loss Prevention**: Automatic backups before destructive operations
- **Error Recovery**: Ability to resume from any step
- **Validation Failures**: Clear error messages and remediation guidance
- **Performance Issues**: Parallel processing options and progress tracking
- **Configuration Errors**: Validation of all configuration parameters

---

## Next Steps

### Completed (Phase 1 - Core Framework)
1. ✅ Create basic project structure
2. ✅ Implement core CLI framework
3. ✅ Add configuration management (YAML with dot notation)
4. ✅ Implement logging system
5. ✅ Build multi-batch registry system
6. ✅ Create path management utilities

### Current Focus
1. 🔄 Integrate Step 2 (CSV conversion) as proof of concept
2. 🔄 Implement base step processor interface
3. 🔄 Create validation framework

### Upcoming
1. Integrate remaining steps (3, 4, 5, 6, 7, 8)
2. Build pipeline orchestration
3. Add comprehensive error handling and reporting
4. Performance optimization and testing
5. Complete documentation

## Notes

- Version 1 code serves as reference only
- Focus on integration of existing working Version-2 applications
- CLI implementation first, GUI in Phase 2
- Windows PowerShell environment
- Data directories separate from framework code location
- **Multi-batch capability**: Framework designed to handle multiple concurrent batch projects
- **Centralized tracking**: All batches registered in single `batch_registry.yaml` file
- **Batch isolation**: Each batch maintains independent configuration and data
- **Lifecycle management**: Complete workflow for retiring batches (complete → archive → remove)
- **Non-destructive**: Status changes and registry removal never delete files

Updated: 2025-11-30 14:35
