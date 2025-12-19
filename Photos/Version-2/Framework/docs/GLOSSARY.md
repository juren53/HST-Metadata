# HSTL Photo Framework Glossary

This glossary provides definitions for key terms, concepts, and technical vocabulary used throughout the HSTL Photo Framework. It is organized by category for easy reference.

---

## 1. Core Framework Concepts

### **Batch**
**Definition:** A single photo collection being processed with its own directories, configuration file, and processing status.

**Context:** Batches are the fundamental unit of work in the HSTL Framework. Each batch represents one complete photo processing job from start to finish.

**Related Terms:** Pipeline, StepProcessor, ConfigManager, BatchRegistry

**Example:**
```python
# Creating a new batch
python hstl_framework.py init "January 2025 Batch"
```

### **Pipeline**
**Definition:** The sequence of 8 processing steps that transform source TIFF images and metadata into final web-ready JPEG images.

**Context:** The Pipeline orchestrates the execution of all steps in order, managing data flow between steps and handling errors.

**Related Terms:** StepProcessor, ProcessingContext, Batch

### **Framework**
**Definition:** The umbrella application that manages the complete HSTL photo metadata workflow, providing both CLI and GUI interfaces.

**Context:** The Framework integrates all the individual processing tools into a unified, manageable system.

**Related Terms:** Pipeline, Batch, GUI, CLI

### **ProcessingContext**
**Definition:** A shared data structure that passes information between pipeline steps, including configuration, paths, and shared data.

**Context:** ProcessingContext acts as a "data bus" during pipeline execution, allowing steps to communicate and share state.

**Related Terms:** Pipeline, StepProcessor, ConfigManager, PathManager

---

## 2. Processing Pipeline Terminology

### **Step 1: Google Spreadsheet Preparation**
**Definition:** Manual setup of the collaborative Google Spreadsheet containing metadata for all photos in the batch.

**Context:** This is currently a manual step where users ensure all required metadata fields (Title, Description, Date, etc.) are completed.

**Related Terms:** Google Sheets API, CSV Conversion, Metadata

### **Step 2: CSV Conversion**
**Definition:** Automated conversion of Google Worksheet data into a local CSV file for processing.

**Context:** Uses `g2c.py` to fetch spreadsheet data via the Google Sheets API and convert it to CSV format.

**Related Terms:** Google Sheets API, g2c.py, CSV, Accession Number

### **Step 3: Unicode Filtering**
**Definition:** Automated detection and correction of text encoding issues in the CSV metadata.

**Context:** Identifies problematic characters (like special quotes) that could cause downstream processing issues.

**Related Terms:** CSV, Encoding, Validation

### **Step 4: TIFF Conversion**
**Definition:** Automated conversion of 16-bit TIFF images to 8-bit format for processing compatibility.

**Context:** 8-bit images are copied unchanged; only 16-bit images are converted to maintain quality standards.

**Related Terms:** TIFF, Bit Depth, Image Processing

### **Step 5: Metadata Embedding**
**Definition:** Automated injection of IPTC metadata from the CSV file into corresponding TIFF images.

**Context:** Uses `write_tags.py` to embed metadata directly into image files for permanent association.

**Related Terms:** IPTC, Metadata, TIFF, write_tags.py

### **Step 6: JPEG Conversion**
**Definition:** Automated conversion of processed TIFF files into JPEG format for web delivery.

**Context:** Reuses Version 1 code to create web-friendly compressed images from archival TIFF files.

**Related Terms:** TIFF, JPEG, Image Processing

### **Step 7: JPEG Resizing**
**Definition:** Automated resizing of JPEG images to fit within an 800x800 pixel constraint.

**Context:** Ensures all images meet web display standards while maintaining aspect ratio.

**Related Terms:** JPEG, Image Processing, Web Optimization

### **Step 8: Watermarking**
**Definition:** Automated addition of HSTL copyright watermarks to restricted images.

**Context:** Only applies watermarks to images marked as restricted in their metadata; unrestricted images are copied unchanged.

**Related Terms:** JPEG, Copyright, Metadata

---

## 3. Data & File Formats

### **TIFF (Tagged Image File Format)**
**Definition:** High-quality, lossless image format used for archival source images.

**Context:** TIFF files are the input format for all processing and are preserved as archival masters.

**Related Terms:** 16-bit TIFF, 8-bit TIFF, Archival Format

### **JPEG (Joint Photographic Experts Group)**
**Definition:** Compressed image format optimized for web delivery and digital access.

**Context:** JPEG files are the final output format, created from processed TIFF files.

**Related Terms:** Image Processing, Web Optimization

### **CSV (Comma-Separated Values)**
**Definition:** Plain text file format for tabular data, used to store metadata exported from Google Sheets.

**Context:** CSV files serve as the primary metadata source for the processing pipeline.

**Related Terms:** Google Sheets API, Metadata, g2c.py

### **YAML (YAML Ain't Markup Language)**
**Definition:** Human-readable configuration file format used for project settings.

**Context:** YAML files store batch configuration, step settings, and framework preferences.

**Related Terms:** ConfigManager, Configuration

### **Accession Number**
**Definition:** Unique identifier for each photo object, mapped to the IPTC ObjectName field.

**Context:** Used to match metadata records with corresponding image files throughout processing.

**Related Terms:** IPTC, ObjectName, Metadata

---

## 4. Technical Architecture

### **StepProcessor**
**Definition:** Abstract base class that defines the interface for all processing steps.

**Context:** Each of the 8 pipeline steps inherits from StepProcessor, implementing validate_inputs(), execute(), and validate_outputs() methods.

**Related Terms:** Pipeline, ProcessingContext, Abstract Base Class

**Example:**
```python
class Step1Processor(StepProcessor):
    def __init__(self):
        super().__init__(1, "Google Spreadsheet Preparation")
    
    def validate_inputs(self, context):
        # Validate step inputs
        pass
    
    def execute(self, context):
        # Execute step logic
        pass
```

### **ConfigManager**
**Definition:** Class responsible for loading, saving, and managing YAML configuration files.

**Context:** Handles project configuration, step settings, and batch metadata using dot notation for key access.

**Related Terms:** YAML, Configuration, ProcessingContext

**Example:**
```python
# Get configuration value
project_name = config.get('project.name')

# Set configuration value
config.set('steps_completed.step1', True)
```

### **BatchRegistry**
**Definition:** Central inventory system that tracks all batch projects and their statuses.

**Context:** Manages batch lifecycle (active, completed, archived) and provides quick access to batch information.

**Related Terms:** Batch, Configuration, Project Management

### **PathManager**
**Definition:** Utility class for managing directory paths and file locations within a batch.

**Context:** Provides consistent access to input, output, and configuration directories for processing steps.

**Related Terms:** ProcessingContext, Directory Structure, Batch

### **ValidationResult**
**Definition:** Data structure containing the results of validation operations.

**Context:** Used throughout the pipeline to validate inputs and outputs, containing success status, errors, and warnings.

**Related Terms:** Validation, StepProcessor, Error Handling

---

## 5. User Interface Terms

### **GUI (Graphical User Interface)**
**Definition:** Visual interface built with PyQt6 for interactive batch management and processing.

**Context:** Provides an alternative to the CLI interface with windows, buttons, and visual feedback.

**Related Terms:** CLI, PyQt6, MainWindow

### **CLI (Command Line Interface)**
**Definition:** Text-based interface for batch management and processing commands.

**Context:** Allows scripting, automation, and remote operation of the framework.

**Related Terms:** GUI, Command Line, Batch Operations

### **MainWindow**
**Definition:** Primary application window containing tabbed interface for batch and step management.

**Context:** Central hub for user interaction with tabs for Batches, Current Batch, Configuration, and Logs.

**Related Terms:** GUI, PyQt6, Tab Interface

---

## 6. Configuration & Management

### **Configuration**
**Definition:** Settings and parameters that control framework behavior and processing options.

**Context:** Stored in YAML files with hierarchical structure using dot notation for access.

**Related Terms:** YAML, ConfigManager, Settings

### **Batch Status**
**Definition:** Current state of a batch in the processing lifecycle.

**Context:** Possible statuses include active, completed, and archived, affecting visibility and operations.

**Related Terms:** Batch, BatchRegistry, Project Management

### **Directory Structure**
**Definition:** Standardized folder layout for batch data organization.

**Context:** Includes input/, output/, config/, reports/, and logs/ subdirectories for organized file management.

**Related Terms:** Batch, PathManager, File Organization

---

## 7. Metadata & IPTC Terms

### **IPTC (International Press Telecommunications Council)**
**Definition:** Metadata standard for describing images, used throughout the framework.

**Context:** IPTC fields provide standardized metadata structure for photo description and rights management.

**Related Terms:** Metadata, EXIF, Accession Number

### **Metadata**
**Definition:** Information about photos including title, description, date, photographer, and usage rights.

**Context:** Stored in CSV files and embedded into image files for permanent association.

**Related Terms:** IPTC, CSV, Metadata Embedding

### **Headline**
**Definition:** IPTC field containing the title or brief heading for an image.

**Context:** Mapped from the "Title" column in the Google Spreadsheet.

**Related Terms:** IPTC, Title, Spreadsheet Column

### **Caption-Abstract**
**Definition:** IPTC field containing detailed description of image content.

**Context:** Mapped from the "Scopenote" column in the Google Spreadsheet.

**Related Terms:** IPTC, Description, Scopenote

### **CopyrightNotice**
**Definition:** IPTC field containing copyright and usage restriction information.

**Context:** Mapped from the "Restrictions" column in the Google Spreadsheet.

**Related Terms:** IPTC, Copyright, Restrictions

---

## 8. Acronyms & Abbreviations

### **HSTL**
**Definition:** Harry S. Truman Library - the project name and organization.

**Context:** The framework was developed specifically for HSTL photo metadata processing needs.

**Related Terms:** Truman Library, Photo Collection

### **EXIF**
**Definition:** Exchangeable Image File Format - metadata standard for technical image information.

**Context:** Contains camera settings, capture date, and technical parameters alongside IPTC metadata.

**Related Terms:** IPTC, Metadata, Technical Data

### **Bit Depth**
**Definition:** Number of bits used to represent color information in each pixel.

**Context:** Framework converts 16-bit images to 8-bit for processing compatibility.

**Related Terms:** TIFF, Image Processing, Color Depth

---

## 9. Tools & External Dependencies

### **Google Sheets API**
**Definition:** Google's programming interface for accessing spreadsheet data.

**Context:** Used in Step 2 to fetch metadata from collaborative Google Worksheets.

**Related Terms:** g2c.py, OAuth2, CSV Conversion

### **g2c.py**
**Definition:** Google Drive to CSV converter script that maps spreadsheet columns to IPTC fields.

**Context:** Core utility for Step 2, handling authentication and data conversion.

**Related Terms:** Google Sheets API, CSV, IPTC

### **Nomacs**
**Definition:** Free image viewer used for spot-checking processed images.

**Context:** Recommended tool for validating metadata embedding and image processing results.

**Related Terms:** Image Viewing, Validation, Quality Control

### **TagWriter**
**Definition:** Tool for viewing and editing image metadata tags.

**Context:** Used for manual verification of embedded metadata in processed images.

**Related Terms:** Metadata, IPTC, Validation

---

## 11. Error Handling & Validation

### **Pre-flight Validation**
**Definition:** Comprehensive validation performed before processing begins to ensure all requirements are met.

**Context:** Checks input files, configuration validity, directory structure, and system readiness before starting pipeline execution.

**Related Terms:** Validation, ProcessingContext, Pipeline

### **Checkpoint**
**Definition:** Recovery point during pipeline execution that allows resuming from failed steps.

**Context:** Enables robust error recovery by saving progress after successful step completion.

**Related Terms:** Pipeline, Error Handling, StepProcessor

### **Mojibake**
**Definition:** Text that appears garbled due to incorrect character encoding interpretation.

**Context:** Common issue in Step 3 when processing text with mixed encoding sources.

**Related Terms:** Unicode Filtering, Character Encoding, CSV

---

## 12. Authentication & Security

### **OAuth2**
**Definition:** Authentication protocol used by Google Sheets API for secure access authorization.

**Context:** Required for Step 2 to access private Google Worksheets containing metadata.

**Related Terms:** Google Sheets API, Client Secret, Token

### **Client Secret**
**Definition:** Authentication credentials file provided by Google API for application authorization.

**Context:** Must be placed in application directory and kept secure for Google Sheets access.

**Related Terms:** OAuth2, Google Sheets API, Authentication

### **Token**
**Definition:** Serialized authentication session data stored after successful OAuth2 authorization.

**Context:** Stored in `token_sheets.pickle` file to avoid repeated authentication prompts.

**Related Terms:** OAuth2, Client Secret, Authentication

---

## 13. GUI Components & Dialogs

### **NewBatchDialog**
**Definition:** Dialog window for creating new batch projects with name and directory selection.

**Context:** Provides user interface for batch initialization with validation and directory creation.

**Related Terms:** Batch, GUI, PyQt6

### **BatchListWidget**
**Definition:** Widget displaying list of all known batches with status and quick access controls.

**Context:** Main interface for batch management, showing active, completed, and archived batches.

**Related Terms:** Batch, BatchRegistry, GUI

### **StepWidget**
**Definition:** Individual widget for each processing step showing status, configuration, and execution controls.

**Context:** Allows users to run individual steps, view results, and monitor progress.

**Related Terms:** StepProcessor, GUI, ProcessingContext

### **ConfigWidget**
**Definition:** Widget for viewing and editing project configuration settings.

**Context:** Provides interface for modifying YAML configuration through GUI controls.

**Related Terms:** ConfigManager, YAML, Configuration

### **LogWidget**
**Definition:** Widget displaying real-time log messages and processing output.

**Context:** Shows detailed information about pipeline execution, errors, and warnings.

**Related Terms:** Logging, ProcessingContext, Error Handling

---

## 14. Data Structures & Internal Components

### **PipelineResult**
**Definition:** Data structure containing results of pipeline execution including success status and step results.

**Context:** Returned by Pipeline.run() method with details about completed steps and any errors.

**Related Terms:** Pipeline, StepResult, ProcessingContext

### **StepResult**
**Definition:** Data structure containing results of individual step execution.

**Context:** Includes success status, message, processed files, and step-specific data.

**Related Terms:** StepProcessor, PipelineResult, Validation

### **Shared Data**
**Definition:** Dictionary for passing data between processing steps during pipeline execution.

**Context:** Allows Step 2 to pass CSV data to Step 3, or Step 4 to pass file lists to Step 5.

**Related Terms:** ProcessingContext, Pipeline, StepProcessor

---

## 15. File System Operations

### **FileUtils**
**Definition:** Utility class providing common file system operations and path management functions.

**Context:** Handles file copying, directory creation, path validation, and other file operations.

**Related Terms:** PathManager, File Operations, Utilities

### **File Validation**
**Definition:** Process of checking file existence, permissions, and format compatibility.

**Context:** Performed before each step to ensure required input files are present and valid.

**Related Terms:** Validation, Pre-flight Validation, FileUtils

---

## 16. Encoding & Character Handling

### **Character Encoding**
**Definition:** Method of converting characters between bytes and text representations.

**Context:** Critical for processing metadata from Google Sheets which may contain special characters.

**Related Terms:** Unicode Filtering, UTF-8, Mojibake

### **UTF-8**
**Definition:** Unicode character encoding standard supporting international characters.

**Context:** Preferred encoding for CSV files and framework configuration files.

**Related Terms:** Character Encoding, Unicode Filtering, CSV

### **cp1252**
**Definition:** Windows code page character encoding commonly used on Windows systems.

**Context:** Alternative encoding that may be encountered when processing older text files.

**Related Terms:** Character Encoding, UTF-8, Windows

---

## 17. Quality Control & Testing

### **Spot Check**
**Definition:** Manual verification process of sample outputs to ensure processing quality.

**Context:** Recommended for Steps 5, 7, and 8 using Nomacs or TagWriter to verify results.

**Related Terms:** Quality Control, Validation, Nomacs

### **Regression Testing**
**Definition:** Automated testing process to ensure new changes don't break existing functionality.

**Context:** Comprehensive test suite covering pipeline steps, configuration, and GUI operations.

**Related Terms:** Testing, Quality Assurance, Development

---

## 18. Development Patterns & Concepts

### **Abstract Base Class**
**Definition:** Class designed to be inherited from, providing interface definition without implementation.

**Context:** StepProcessor is an ABC requiring subclasses to implement validate_inputs(), execute(), and validate_outputs().

**Related Terms:** StepProcessor, Object-Oriented Programming, Interface

### **Context Manager**
**Definition:** Python construct for resource management using 'with' statement syntax.

**Context:** Used for logging, file operations, and resource cleanup throughout the framework.

**Related Terms:** Resource Management, Python, StepLogger

### **Dataclass**
**Definition:** Python class primarily for storing data with automatic method generation.

**Context:** Used for StepResult, ValidationResult, and other simple data structures.

**Related Terms:** Python, Data Structure, Object-Oriented Programming

### **Signal/Slot**
**Definition:** Qt event communication mechanism for connecting UI events to handler functions.

**Context:** Used throughout GUI for button clicks, menu actions, and widget updates.

**Related Terms:** PyQt6, GUI, Event Handling

---

## 10. Development & Architecture Patterns

### **Plugin Architecture**
**Definition:** Modular design where each processing step is implemented as a separate, interchangeable module.

**Context:** Allows easy addition, modification, or replacement of individual processing steps.

**Related Terms:** StepProcessor, Modularity, Extensibility

### **Configuration-Driven Design**
**Definition:** Architecture where behavior is controlled through external configuration files rather than hardcoded values.

**Context:** Framework behavior, paths, and processing options are all configurable via YAML files.

**Related Terms:** YAML, ConfigManager, Settings

### **Multi-Batch Registry Pattern**
**Definition:** Centralized tracking system for managing multiple concurrent batch projects.

**Context:** Enables production environments to process multiple photo collections simultaneously.

**Related Terms:** BatchRegistry, Project Management, Batch Lifecycle

---

## Cross-Reference Index

### A
- **Accession Number** - See: Metadata & IPTC Terms
- **Active Batch** - See: Configuration & Management
- **Abstract Base Class** - See: StepProcessor
- **Archived Batch** - See: Configuration & Management

### B
- **Batch** - See: Core Framework Concepts
- **Batch Registry** - See: Technical Architecture
- **Batch Status** - See: Configuration & Management
- **Bit Depth** - See: Acronyms & Abbreviations

### C
- **Caption-Abstract** - See: Metadata & IPTC Terms
- **CLI** - See: User Interface Terms
- **ConfigManager** - See: Technical Architecture
- **Configuration** - See: Configuration & Management
- **CopyrightNotice** - See: Metadata & IPTC Terms
- **CSV** - See: Data & File Formats

### D
- **Directory Structure** - See: Configuration & Management

### E
- **EXIF** - See: Acronyms & Abbreviations

### F
- **Framework** - See: Core Framework Concepts

### G
- **g2c.py** - See: Tools & External Dependencies
- **GUI** - See: User Interface Terms
- **Google Sheets API** - See: Tools & External Dependencies

### H
- **Headline** - See: Metadata & IPTC Terms
- **HSTL** - See: Acronyms & Abbreviations

### I
- **IPTC** - See: Metadata & IPTC Terms

### J
- **JPEG** - See: Data & File Formats

### M
- **MainWindow** - See: User Interface Terms
- **Metadata** - See: Metadata & IPTC Terms
- **Metadata Embedding** - See: Processing Pipeline Terminology (Step 5)

### N
- **Nomacs** - See: Tools & External Dependencies

### P
- **PathManager** - See: Technical Architecture
- **Pipeline** - See: Core Framework Concepts
- **ProcessingContext** - See: Core Framework Concepts
- **Plugin Architecture** - See: Development & Architecture Patterns

### S
- **StepProcessor** - See: Technical Architecture
- **Spreadsheet Column** - See: Metadata & IPTC Terms

### T
- **TagWriter** - See: Tools & External Dependencies
- **TIFF** - See: Data & File Formats

### V
- **ValidationResult** - See: Technical Architecture

### Y
- **YAML** - See: Data & File Formats

---

*This glossary is a living document. Please suggest additions or corrections by reviewing the framework documentation and codebase.*