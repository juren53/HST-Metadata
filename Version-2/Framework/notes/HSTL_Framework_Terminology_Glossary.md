# HSTL Photo Framework - Comprehensive Terminology Glossary

This glossary contains all significant technical terminology extracted from the HSTL Photo Framework Python codebase, organized by category for reference.

## Table of Contents
- [Core Classes](#core-classes)
- [Methods/Functions](#methodsfunctions)
- [Variables/Data Structures](#variablesdata-structures)
- [Module/Package Names](#modulepackage-names)
- [Configuration Keys](#configuration-keys)
- [Technical Terms](#technical-terms)

---

## Core Classes

### Framework Classes
- **HSLTFramework** (hstl_framework.py:44)
  - Main framework controller class managing the complete photo processing workflow
  
- **Pipeline** (core/pipeline.py:33)
  - Orchestrates execution of processing steps in sequence
  
- **PipelineResult** (core/pipeline.py:13)
  - Container for pipeline execution results and step completion status

### Configuration Classes
- **ConfigManager** (config/config_manager.py:16)
  - Manages YAML configuration files with hierarchical key access
  
- **BatchRegistry** (utils/batch_registry.py:14)
  - Manages registry of all batch projects with status tracking

### Processing Classes
- **StepProcessor** (steps/base_step.py:56)
  - Abstract base class for all processing steps
  
- **ProcessingContext** (steps/base_step.py:33)
  - Shared context object passed through pipeline for data exchange
  
- **StepResult** (steps/base_step.py:18)
  - Result container for individual step execution

### Validation Classes
- **Validator** (utils/validator.py:32)
  - Utility class for validating files, directories, and configurations
  
- **ValidationResult** (utils/validator.py:11)
  - Container for validation results with errors and warnings

### GUI Classes
- **MainWindow** (gui/main_window.py:31)
  - Primary interface window with tabbed layout
  
- **BatchListWidget** (gui/widgets/batch_list_widget.py:21)
  - Widget for displaying and managing batch projects
  
- **StepWidget** (gui/widgets/step_widget.py:27)
  - Interface for executing and monitoring processing steps
  
- **ConfigWidget** (gui/widgets/config_widget.py)
  - Configuration editor widget
  
- **LogWidget** (gui/widgets/log_widget.py)
  - Log viewer widget
  
- **NewBatchDialog** (gui/dialogs/new_batch_dialog.py:12)
  - Dialog for creating new batch projects

### Utility Classes
- **PathManager** (utils/path_manager.py:11)
  - Centralized management of directory paths
  
- **FileUtils** (utils/file_utils.py:14)
  - Utility functions for file operations
  
- **ColoredFormatter** (utils/logger.py:22)
  - Custom log formatter with colorized output
  
- **StepLogger** (utils/logger.py:124)
  - Context manager for step-specific logging

### Specialized Classes
- **RecordViewerFrame** (csv_record_viewer.py:7)
  - wxPython frame for viewing CSV records with navigation
  
- **SheetsTypeDetector** (referenced in g2c.py:166)
  - Detects Google Sheets vs Excel file types

---

## Methods/Functions

### Framework Methods
- **initialize()** (hstl_framework.py:53)
  - Initialize framework with configuration and logging
  
- **init_project()** (hstl_framework.py:78)
  - Create new project with directory structure and configuration
  
- **run_steps()** (hstl_framework.py:194)
  - Execute specified processing steps
  
- **show_status()** (hstl_framework.py:150)
  - Display current project status and step completion
  
- **validate()** (hstl_framework.py:216)
  - Validate project or specific step

### Configuration Methods
- **load_config()** (config/config_manager.py:32)
  - Load configuration from YAML file
  
- **save_config()** (config/config_manager.py:57)
  - Save configuration to YAML file
  
- **get()** (config/config_manager.py:92)
  - Get configuration value using dot notation
  
- **set()** (config/config_manager.py:114)
  - Set configuration value using dot notation
  
- **update_step_status()** (config/config_manager.py:148)
  - Update completion status for specific step

### Pipeline Methods
- **register_step()** (core/pipeline.py:41)
  - Register a step processor with the pipeline
  
- **run()** (core/pipeline.py:46)
  - Execute pipeline from start to end step

### Step Processing Methods
- **validate_inputs()** (steps/base_step.py:69)
  - Validate inputs before step execution
  
- **execute()** (steps/base_step.py:74)
  - Execute the main step processing logic
  
- **validate_outputs()** (steps/base_step.py:79)
  - Validate outputs after step execution
  
- **run()** (steps/base_step.py:84)
  - Complete step workflow: validate inputs, execute, validate outputs

### Batch Registry Methods
- **register_batch()** (utils/batch_registry.py:60)
  - Register new batch project in registry
  
- **get_batch()** (utils/batch_registry.py:128)
  - Retrieve batch information by ID
  
- **list_batches_summary()** (utils/batch_registry.py:223)
  - Get summary of all batches with completion status

### Utility Methods
- **ensure_directory()** (utils/file_utils.py:17)
  - Create directory if it doesn't exist
  
- **backup_file()** (utils/file_utils.py:26)
  - Create backup copy of file
  
- **count_csv_records()** (utils/file_utils.py:44)
  - Count records in CSV file by Accession Numbers/ObjectNames

### Google Sheets Integration Methods
- **get_credentials()** (g2c.py:57)
  - Obtain OAuth2 credentials for Google APIs
  
- **extract_spreadsheet_id_from_url()** (g2c.py:116)
  - Extract spreadsheet ID from Google Sheets/Drive URLs
  
- **fetch_sheet_data()** (g2c.py:224)
  - Fetch data from Google Sheet into pandas DataFrame
  
- **export_to_csv()** (g2c.py:445)
  - Export DataFrame to CSV with IPTC metadata mapping

---

## Variables/Data Structures

### Core Data Structures
- **FRAMEWORK_VERSION** (hstl_framework.py:41)
  - Version string for framework (currently "1.0.0")
  
- **SUPPORTED_STEPS** (hstl_framework.py:42)
  - List of supported processing step numbers (1-8)
  
- **DEFAULT_SETTINGS** (config/settings.py:9)
  - Default configuration dictionary with all framework settings

### Step Configuration
- **STEP_NAMES** (config/settings.py:142)
  - Mapping of step numbers to human-readable names
  
- **STEP_VALIDATION_RULES** (config/settings.py:154)
  - Validation rules for each processing step

### GUI State Variables
- **current_batch_id** (gui/main_window.py:41)
  - Currently selected batch identifier
  
- **batch_info_cache** (gui/widgets/batch_list_widget.py:35)
  - Cache for batch information to improve performance

### Processing Context
- **shared_data** (steps/base_step.py:45)
  - Dictionary for passing data between processing steps

### File Patterns
- **file_patterns** (config/settings.py:126)
  - Dictionary of file extension patterns by type

---

## Module/Package Names

### Core Modules
- **core.pipeline** - Pipeline orchestration module
- **core.__init__** - Core package initialization

### Configuration Modules
- **config.config_manager** - Configuration management
- **config.settings** - Default settings and constants
- **config.__init__** - Configuration package initialization

### Step Processing Modules
- **steps.base_step** - Base step processor and utilities
- **steps.__init__** - Steps package initialization

### Utility Modules
- **utils.batch_registry** - Batch project registry management
- **utils.file_utils** - File operation utilities
- **utils.validator** - Validation utilities
- **utils.path_manager** - Path management utilities
- **utils.logger** - Logging utilities
- **utils.__init__** - Utilities package initialization

### GUI Modules
- **gui.hstl_gui** - GUI application entry point
- **gui.main_window** - Main application window
- **gui.widgets.step_widget** - Step execution widget
- **gui.widgets.batch_list_widget** - Batch list display widget
- **gui.widgets.config_widget** - Configuration editor widget
- **gui.widgets.log_widget** - Log viewer widget
- **gui.widgets.__init__** - Widgets package initialization
- **gui.dialogs.new_batch_dialog** - New batch creation dialog
- **gui.dialogs.settings_dialog** - Settings configuration dialog
- **gui.dialogs.*_dialog** - Various step-specific dialogs
- **gui.dialogs.__init__** - Dialogs package initialization
- **gui.__init__** - GUI package initialization

### External Tool Modules
- **csv_record_viewer** - Standalone CSV record viewer application
- **g2c** - Google Drive to CSV converter with IPTC mapping

---

## Configuration Keys

### Project Configuration
- **project.name** - Project/batch name
- **project.data_directory** - Base directory for project files
- **project.created** - Project creation timestamp

### Step Status
- **steps_completed.step[1-8]** - Boolean completion status for each step

### Step-Specific Configuration
- **step_configurations.step[1-8]** - Configuration for each processing step
  - step1.required_fields - Required metadata fields
  - step2.output_filename - Output CSV filename
  - step3.generate_reports - Generate Unicode reports flag
  - step4.target_bit_depth - Target TIFF bit depth
  - step5.validate_embedding - Metadata embedding validation
  - step6.quality - JPEG conversion quality
  - step7.max_dimension - Maximum resized dimension
  - step8.watermark_opacity - Watermark transparency

### Logging Configuration
- **logging.level** - Logging level (DEBUG, INFO, WARNING, ERROR)
- **logging.file** - Log file path
- **logging.format** - Log message format string
- **logging.max_file_size** - Maximum log file size
- **logging.backup_count** - Number of log backups to keep

### Validation Configuration
- **validation.strict_mode** - Enable strict validation mode
- **validation.auto_backup** - Automatic backup on validation errors
- **validation.validate_paths** - Validate file paths
- **validation.pre_flight_checks** - Run pre-flight validation

### Pipeline Configuration
- **pipeline.stop_on_error** - Stop pipeline on step failure
- **pipeline.create_checkpoints** - Create recovery checkpoints
- **pipeline.parallel_processing** - Enable parallel step execution
- **pipeline.max_workers** - Maximum parallel worker threads

### Directory Structure
- **directories.input.tiff** - Input TIFF directory path
- **directories.input.spreadsheet** - Input spreadsheet directory path
- **directories.output.csv** - Output CSV directory path
- **directories.output.tiff_processed** - Processed TIFF output directory
- **directories.output.jpeg** - JPEG output directory
- **directories.output.jpeg_resized** - Resized JPEG output directory
- **directories.output.jpeg_watermarked** - Watermarked JPEG output directory
- **directories.reports** - Reports directory path
- **directories.logs** - Logs directory path
- **directories.config** - Configuration directory path
- **directories.temp** - Temporary files directory path

### External Tools Configuration
- **tools.nomacs** - Path to Nomacs image viewer
- **tools.tagwriter** - Path to TagWriter metadata tool
- **tools.exiftool** - Path to ExifTool metadata utility

### Performance Configuration
- **performance.chunk_size** - Processing chunk size for large datasets
- **performance.memory_limit** - Memory usage limit
- **performance.temp_cleanup** - Clean temporary files flag

---

## Technical Terms

### Processing Workflow Terms
- **Batch Project** - Independent collection of photos processed together
- **Processing Step** - One of 8 defined workflow stages
- **Pipeline** - Sequential execution of processing steps
- **Checkpoint** - Recovery point during pipeline execution
- **Pre-flight Validation** - Validation performed before processing starts

### File Format Terms
- **TIFF** - Tagged Image File Format (input format)
- **JPEG** - Joint Photographic Experts Group format (output format)
- **CSV** - Comma-Separated Values (metadata format)
- **YAML** - YAML Ain't Markup Language (configuration format)

### Metadata Terms
- **IPTC** - International Press Telecommunications Council metadata standard
- **EXIF** - Exchangeable Image File Format metadata
- **Accession Number** - Unique identifier for museum/collection objects
- **ObjectName** - IPTC field for object identification
- **Headline** - IPTC field for title/headline
- **Caption-Abstract** - IPTC field for description
- **CopyrightNotice** - IPTC field for copyright information
- **By-line** - IPTC field for photographer credit
- **Source** - IPTC field for source/origin

### Image Processing Terms
- **Bit Depth Conversion** - Converting 16-bit to 8-bit TIFF images
- **Metadata Embedding** - Writing IPTC metadata into image files
- **JPEG Conversion** - Converting TIFF to JPEG format
- **Image Resizing** - Scaling images to maximum dimensions
- **Watermarking** - Adding watermark to restricted images

### Data Quality Terms
- **Unicode Filtering** - Cleaning encoding artifacts and character issues
- **Validation** - Checking data integrity and completeness
- **Encoding Artifacts** - Character encoding misinterpretation patterns

### Google Integration Terms
- **Google Sheets API** - Google's spreadsheet data access interface
- **OAuth2** - Authentication protocol for Google API access
- **Spreadsheet ID** - Unique identifier for Google Sheets
- **Client Secret** - Authentication credentials file

### GUI Terms
- **PyQt6** - Python GUI framework (version 6)
- **Widget** - UI component (button, table, dialog, etc.)
- **Signal/Slot** - Qt event communication mechanism
- **Tab Widget** - Container for multiple interface panels
- **Context Menu** - Right-click popup menu

### Development Terms
- **Abstract Base Class** - Class designed to be inherited from
- **Dataclass** - Python class primarily for storing data
- **Context Manager** - Resource management using 'with' statement
- **Logging** - Recording application events and errors
- **Configuration Management** - Managing application settings

### File System Terms
- **Path Manager** - Centralized path resolution system
- **Registry** - Persistent storage for batch metadata
- **Cache** - Temporary storage for performance optimization
- **Backup** - Duplicate copy for data protection

### Error Handling Terms
- **Exception Handling** - Managing runtime errors gracefully
- **Validation Result** - Container for validation outcomes
- **Error Recovery** - Processes for handling and recovering from errors
- **Warning System** - Non-critical issue notification

---

## File Locations and References

This glossary was compiled from the following Python files in the HSTL Photo Framework:

- **hstl_framework.py** - Main CLI framework controller
- **core/pipeline.py** - Pipeline orchestration
- **config/config_manager.py** - Configuration management
- **config/settings.py** - Default settings and constants
- **steps/base_step.py** - Step processing base classes
- **utils/batch_registry.py** - Batch project registry
- **utils/file_utils.py** - File operation utilities
- **utils/validator.py** - Validation utilities
- **utils/path_manager.py** - Path management
- **utils/logger.py** - Logging system
- **gui/hstl_gui.py** - GUI application entry point
- **gui/main_window.py** - Main GUI window
- **gui/widgets/step_widget.py** - Step execution interface
- **gui/widgets/batch_list_widget.py** - Batch management interface
- **gui/dialogs/new_batch_dialog.py** - New batch creation dialog
- **csv_record_viewer.py** - Standalone CSV viewer
- **g2c.py** - Google Drive to CSV converter

## Last Updated

This glossary was generated on December 19, 2025, and reflects the terminology used in the HSTL Photo Framework codebase as of that date.