# Software Architecture Document (SAD)

## HSTL Photo Metadata Framework (HPM)

**Version:** 0.1.7l
**Date:** 2026-01-23
**Author:** HSTL Photo Metadata Project

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Architectural Goals and Constraints](#2-architectural-goals-and-constraints)
3. [System Overview](#3-system-overview)
4. [Architectural Views](#4-architectural-views)
   - 4.1 [Logical View](#41-logical-view)
   - 4.2 [Process View](#42-process-view)
   - 4.3 [Development View](#43-development-view)
   - 4.4 [Physical View](#44-physical-view)
5. [Component Descriptions](#5-component-descriptions)
6. [Data Architecture](#6-data-architecture)
7. [Interface Specifications](#7-interface-specifications)
8. [Design Patterns](#8-design-patterns)
9. [External Dependencies](#9-external-dependencies)
10. [Quality Attributes](#10-quality-attributes)
11. [Appendices](#11-appendices)

---

## 1. Introduction

### 1.1 Purpose

This Software Architecture Document (SAD) provides a comprehensive architectural overview of the HSTL Photo Metadata Framework (HPM). It describes the system's structure, components, interfaces, and design decisions to guide development, maintenance, and future enhancements.

### 1.2 Scope

HPM is a desktop application for managing photo metadata processing workflows. It orchestrates an 8-step pipeline from Excel spreadsheet preparation through final watermarked JPEG creation, supporting both command-line and graphical user interfaces.

### 1.3 Definitions and Acronyms

| Term | Definition                                     |
| ---- | ---------------------------------------------- |
| HPM  | HSTL Photo Metadata Framework                  |
| HSTL | Harry S. Truman Library                        |
| SAD  | Software Architecture Document                 |
| CLI  | Command Line Interface                         |
| GUI  | Graphical User Interface                       |
| EXIF | Exchangeable Image File Format                 |
| IPTC | International Press Telecommunications Council |
| TIFF | Tagged Image File Format                       |

### 1.4 References

- [CHANGELOG.md](../CHANGELOG.md) - Version history
- [USER_GUIDE.md](USER_GUIDE.md) - User documentation
- [GUI_QUICKSTART.md](GUI_QUICKSTART.md) - GUI quick start guide
- [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md) - Development roadmap

---

## 2. Architectural Goals and Constraints

### 2.1 Architectural Goals

| Goal                | Description                                                |
| ------------------- | ---------------------------------------------------------- |
| **Modularity**      | Independent, replaceable components with clear interfaces  |
| **Extensibility**   | Easy addition of new processing steps without core changes |
| **Usability**       | Both CLI and GUI interfaces for different user preferences |
| **Reliability**     | Robust error handling and recovery mechanisms              |
| **Traceability**    | Comprehensive logging for debugging and auditing           |
| **Maintainability** | Clear code structure with separation of concerns           |

### 2.2 Architectural Constraints

| Constraint         | Rationale                                                |
| ------------------ | -------------------------------------------------------- |
| Python 3.9+        | Language requirement for type hints and modern features  |
| PyQt6              | GUI framework for cross-platform desktop application     |
| Windows Primary    | Target platform (Windows 10/11) with ExifTool dependency |
| Local Processing   | All image processing occurs locally for data security    |
| YAML Configuration | Human-readable configuration format                      |

### 2.3 Design Principles

1. **Single Responsibility**: Each module handles one concern
2. **Open/Closed**: Extensible without modification (step system)
3. **Dependency Inversion**: High-level modules independent of low-level details
4. **Interface Segregation**: Specific interfaces over general-purpose ones
5. **Don't Repeat Yourself**: Centralized utilities and shared components

---

## 3. System Overview

### 3.1 System Context

```
┌─────────────────────────────────────────────────────────────────┐
│                        External Systems                          │
├─────────────────┬─────────────────┬─────────────────────────────┤
│  Excel Files    │   TIFF Images   │   ExifTool (Binary)         │
│  (.xlsx/.xls)   │   (16/8-bit)    │   (Metadata R/W)            │
└────────┬────────┴────────┬────────┴──────────────┬──────────────┘
         │                 │                        │
         ▼                 ▼                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                  HPM Framework Application                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    User Interfaces                        │   │
│  │  ┌─────────────────┐    ┌─────────────────────────────┐  │   │
│  │  │   CLI (hstl_    │    │   GUI (PyQt6 MainWindow)    │  │   │
│  │  │   framework.py) │    │   - Batches Tab             │  │   │
│  │  │                 │    │   - Current Batch Tab       │  │   │
│  │  │                 │    │   - Configuration Tab       │  │   │
│  │  │                 │    │   - Logs Tab                │  │   │
│  │  └─────────────────┘    └─────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                   Core Processing                         │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │   │
│  │  │   Pipeline   │  │    Steps     │  │   Batch      │    │   │
│  │  │ Orchestrator │  │   (1-8)      │  │  Registry    │    │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘    │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                   Infrastructure                          │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────────┐  │   │
│  │  │  Config  │ │   Log    │ │   Path   │ │  Validator  │  │   │
│  │  │ Manager  │ │ Manager  │ │ Manager  │ │             │  │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └─────────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
         │                 │                        │
         ▼                 ▼                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Output Files                             │
├─────────────────┬─────────────────┬─────────────────────────────┤
│  CSV Exports    │  Processed      │   JPEG Images               │
│                 │  TIFFs          │   (Full/Resized/Watermarked)│
└─────────────────┴─────────────────┴─────────────────────────────┘
```

### 3.2 High-Level Architecture

The system follows a **layered architecture** with clear separation between:

1. **Presentation Layer** - CLI and GUI interfaces
2. **Application Layer** - Pipeline orchestration and step execution
3. **Domain Layer** - Business logic for image processing
4. **Infrastructure Layer** - Configuration, logging, file management

---

## 4. Architectural Views

### 4.1 Logical View

The logical view describes the system's functional decomposition.

```
┌─────────────────────────────────────────────────────────────────┐
│                      Presentation Layer                          │
│  ┌─────────────────────────┐  ┌─────────────────────────────┐   │
│  │     CLI Interface       │  │      GUI Application        │   │
│  │   (hstl_framework.py)   │  │    (gui/main_window.py)     │   │
│  └───────────┬─────────────┘  └──────────────┬──────────────┘   │
└──────────────┼───────────────────────────────┼──────────────────┘
               │                               │
               ▼                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Application Layer                           │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                  Pipeline Orchestrator                   │    │
│  │                   (core/pipeline.py)                     │    │
│  └──────────────────────────┬──────────────────────────────┘    │
│                             │                                    │
│  ┌──────────────────────────┴──────────────────────────────┐    │
│  │                   Step Processors                        │    │
│  │  ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐│    │
│  │  │ S1 │ │ S2 │ │ S3 │ │ S4 │ │ S5 │ │ S6 │ │ S7 │ │ S8 ││    │
│  │  └────┘ └────┘ └────┘ └────┘ └────┘ └────┘ └────┘ └────┘│    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Domain Layer                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │ ProcessingCo │  │  StepResult  │  │  ValidationResult    │   │
│  │   ntext      │  │              │  │                      │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Infrastructure Layer                           │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐    │
│  │  Config    │ │    Log     │ │    Path    │ │   Batch    │    │
│  │  Manager   │ │  Manager   │ │  Manager   │ │  Registry  │    │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘    │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐                   │
│  │ Validator  │ │ FileUtils  │ │ Console    │                   │
│  │            │ │            │ │ Capture    │                   │
│  └────────────┘ └────────────┘ └────────────┘                   │
└─────────────────────────────────────────────────────────────────┘
```

#### 4.1.1 Key Logical Components

| Component                 | Responsibility                                  |
| ------------------------- | ----------------------------------------------- |
| **CLI Interface**         | Command-line access to all framework operations |
| **GUI Application**       | Visual interface for batch and step management  |
| **Pipeline Orchestrator** | Coordinates sequential step execution           |
| **Step Processors**       | Individual processing logic for each step       |
| **ProcessingContext**     | Shared state carrier through pipeline           |
| **ConfigManager**         | Hierarchical configuration management           |
| **LogManager**            | Centralized logging with GUI integration        |
| **BatchRegistry**         | Multi-project batch tracking                    |

### 4.2 Process View

The process view describes runtime behavior and concurrency.

#### 4.2.1 Main Process Flow

```
Application Start
      │
      ▼
┌─────────────────┐
│  Initialize     │
│  - LogManager   │
│  - ThemeManager │
│  - ZoomManager  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│   Load Batch    │────▶│  Load Config    │
│   Registry      │     │  (YAML)         │
└────────┬────────┘     └────────┬────────┘
         │                       │
         ▼                       ▼
┌─────────────────────────────────────────┐
│            Main Event Loop               │
│  ┌─────────────────────────────────┐    │
│  │  User Action                     │    │
│  │    │                             │    │
│  │    ▼                             │    │
│  │  ┌───────────────────────────┐  │    │
│  │  │  Execute Step             │  │    │
│  │  │  - validate_inputs()      │  │    │
│  │  │  - execute()              │  │    │
│  │  │  - validate_outputs()     │  │    │
│  │  │  - update_step_status()   │  │    │
│  │  └───────────────────────────┘  │    │
│  │    │                             │    │
│  │    ▼                             │    │
│  │  Update UI / Log Results         │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

#### 4.2.2 Step Execution Sequence

```
StepWidget._run_step(step_num)
         │
         ▼
┌────────────────────┐
│  Open Step Dialog  │
│  (StepXDialog)     │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│  User Configures   │
│  Step Parameters   │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│  Execute Button    │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐     ┌────────────────────┐
│  StepProcessor.run │────▶│  validate_inputs() │
└─────────┬──────────┘     └─────────┬──────────┘
          │                          │
          │◀─────────────────────────┘
          ▼
┌────────────────────┐
│     execute()      │
│  (Main Processing) │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ validate_outputs() │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│  Update Config     │
│  (step completed)  │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│  Emit step_executed│
│  Signal            │
└────────────────────┘
```

#### 4.2.3 Logging Process Flow

```
Application Component
         │
         │ log_manager.info("message", batch_id, step)
         ▼
┌────────────────────────────────────────────────────────────┐
│                      LogManager                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                   Route Log Entry                     │  │
│  └──────────────────────────────────────────────────────┘  │
│         │                    │                    │        │
│         ▼                    ▼                    ▼        │
│  ┌────────────┐     ┌────────────────┐    ┌────────────┐  │
│  │  Session   │     │  Batch File    │    │    GUI     │  │
│  │  Logger    │     │  Handler       │    │  Handler   │  │
│  │            │     │  (Rotating)    │    │  (Signal)  │  │
│  └─────┬──────┘     └───────┬────────┘    └─────┬──────┘  │
└────────┼────────────────────┼───────────────────┼─────────┘
         │                    │                   │
         ▼                    ▼                   ▼
   session.log         batch_XXX.log      EnhancedLogWidget
```

### 4.3 Development View

The development view describes the static organization of the software.

#### 4.3.1 Package Structure

```
Framework/
├── __init__.py              # Package metadata (__version__, __commit_date__)
├── hstl_framework.py        # CLI entry point
│
├── config/                  # Configuration Management
│   ├── __init__.py
│   ├── config_manager.py    # ConfigManager class
│   └── settings.py          # DEFAULT_SETTINGS dictionary
│
├── core/                    # Core Processing
│   ├── __init__.py
│   └── pipeline.py          # Pipeline, PipelineResult classes
│
├── steps/                   # Step Implementations
│   ├── __init__.py
│   └── base_step.py         # StepProcessor (ABC), ProcessingContext, StepResult
│
├── gui/                     # GUI Application
│   ├── __init__.py
│   ├── hstl_gui.py          # GUI entry point, main()
│   ├── main_window.py       # MainWindow class
│   ├── theme_manager.py     # ThemeManager (Singleton)
│   ├── zoom_manager.py      # ZoomManager (Singleton)
│   │
│   ├── widgets/             # Reusable Widgets
│   │   ├── __init__.py
│   │   ├── batch_list_widget.py
│   │   ├── step_widget.py
│   │   ├── config_widget.py
│   │   ├── enhanced_log_widget.py
│   │   └── log_widget.py
│   │
│   └── dialogs/             # Modal Dialogs
│       ├── __init__.py
│       ├── step1_dialog.py through step8_dialog.py
│       ├── new_batch_dialog.py
│       ├── batch_info_dialog.py
│       ├── settings_dialog.py
│       ├── log_viewer_dialog.py
│       ├── set_data_location_dialog.py
│       └── theme_dialog.py
│
├── utils/                   # Utilities
│   ├── __init__.py
│   ├── config_manager.py    # (Legacy, redirects to config/)
│   ├── logger.py            # ColoredFormatter, setup_logger()
│   ├── log_manager.py       # LogManager (Singleton)
│   ├── path_manager.py      # PathManager class
│   ├── batch_registry.py    # BatchRegistry class
│   ├── validator.py         # Validator, ValidationResult
│   ├── file_utils.py        # FileUtils class
│   ├── console_capture.py   # ConsoleCaptureHandler
│   ├── github_version_checker.py
│   └── git_updater.py
│
├── tests/                   # Test Suite
│   ├── conftest.py          # Pytest fixtures
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   └── gui/                 # GUI tests
│
├── docs/                    # Documentation
│   ├── USER_GUIDE.md
│   ├── GUI_QUICKSTART.md
│   ├── DEVELOPMENT_PLAN.md
│   ├── GLOSSARY.md
│   └── SOFTWARE_ARCHITECTURE.md (this document)
│
├── launcher/                # Application launchers
├── scripts/                 # Utility scripts
├── requirements.txt         # Python dependencies
├── pyproject.toml           # Project configuration
├── CHANGELOG.md             # Version history
└── README.md                # Project overview
```

#### 4.3.2 Module Dependencies

```
                    ┌─────────────────┐
                    │   __init__.py   │
                    │ (__version__)   │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│hstl_framework │   │  gui/hstl_gui │   │ Utility Scripts│
│    (CLI)      │   │    (GUI)      │   │  (g2c.py etc) │
└───────┬───────┘   └───────┬───────┘   └───────────────┘
        │                   │
        │                   ▼
        │           ┌───────────────┐
        │           │  main_window  │
        │           └───────┬───────┘
        │                   │
        │    ┌──────────────┼──────────────┐
        │    │              │              │
        │    ▼              ▼              ▼
        │ ┌────────┐  ┌──────────┐  ┌───────────┐
        │ │widgets/│  │ dialogs/ │  │theme/zoom │
        │ └────┬───┘  └────┬─────┘  │ managers  │
        │      │           │        └───────────┘
        │      └─────┬─────┘
        │            │
        ▼            ▼
┌─────────────────────────────────────────────────────┐
│                    core/pipeline                     │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│                   steps/base_step                    │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│                      utils/                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐    │
│  │config_mgr   │ │ log_manager │ │ path_manager│    │
│  └─────────────┘ └─────────────┘ └─────────────┘    │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐    │
│  │batch_registry│ │ validator  │ │ file_utils  │    │
│  └─────────────┘ └─────────────┘ └─────────────┘    │
└─────────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│                   config/settings                    │
│              (DEFAULT_SETTINGS dict)                 │
└─────────────────────────────────────────────────────┘
```

### 4.4 Physical View

The physical view describes the mapping of software to hardware.

#### 4.4.1 Deployment Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Windows Workstation                           │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                   HPM Application                        │    │
│  │  ┌─────────────────┐    ┌─────────────────────────────┐ │    │
│  │  │  Python 3.9+    │    │      PyQt6 Runtime          │ │    │
│  │  │  Interpreter    │    │                             │ │    │
│  │  └─────────────────┘    └─────────────────────────────┘ │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                   External Tools                         │    │
│  │  ┌─────────────────┐    ┌─────────────────────────────┐ │    │
│  │  │   ExifTool.exe  │    │  TagWriter (Optional Viewer)  │ │    │
│  │  │   (Metadata)    │    │                             │ │    │
│  │  └─────────────────┘    └─────────────────────────────┘ │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    File System                           │    │
│  │                                                          │    │
│  │  C:\Users\{user}\                                        │    │
│  │  └── .hstl_photo_framework\     (App data)               │    │
│  │      ├── logs\                  (Session logs)           │    │
│  │      └── settings.ini           (User preferences)       │    │
│  │                                                          │    │
│  │  {Framework Directory}\                                  │    │
│  │  └── config\                                             │    │
│  │      └── batch_registry.yaml    (Batch registry)         │    │
│  │                                                          │    │
│  │  {Project Data Directory}\      (Per batch)              │    │
│  │  ├── input\                                              │    │
│  │  │   ├── tiff\                  (Source TIFFs)           │    │
│  │  │   └── spreadsheet\           (Excel files)            │    │
│  │  ├── output\                                             │    │
│  │  │   ├── csv\                   (Exported CSVs)          │    │
│  │  │   ├── tiff_processed\        (Processed TIFFs)        │    │
│  │  │   ├── jpeg\                  (Converted JPEGs)        │    │
│  │  │   ├── jpeg_resized\          (Resized JPEGs)          │    │
│  │  │   └── jpeg_watermarked\      (Watermarked JPEGs)      │    │
│  │  ├── config\                                             │    │
│  │  │   └── project_config.yaml    (Batch configuration)    │    │
│  │  ├── logs\                      (Batch logs)             │    │
│  │  └── reports\                   (Processing reports)     │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                   Network (Optional)                     │    │
│  │  ┌─────────────────────────────────────────────────────┐│    │
│  │  │  GitHub API (api.github.com)                        ││    │
│  │  │  - Version checking                                 ││    │
│  │  │  - Update downloads                                 ││    │
│  │  └─────────────────────────────────────────────────────┘│    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

#### 4.4.2 Directory Structure Per Batch

```
{Data Directory}/
├── input/
│   ├── tiff/                    # Source TIFF images (Step 4 input)
│   │   ├── image001.tif
│   │   ├── image002.tif
│   │   └── ...
│   └── spreadsheet/             # Excel metadata (Step 1 input)
│       └── metadata.xlsx
│
├── output/
│   ├── csv/                     # Step 2 output
│   │   └── export.csv
│   ├── tiff_processed/          # Steps 4-5 output
│   │   ├── image001.tif         # 8-bit with metadata
│   │   └── ...
│   ├── jpeg/                    # Step 6 output
│   │   ├── image001.jpg
│   │   └── ...
│   ├── jpeg_resized/            # Step 7 output
│   │   ├── image001.jpg         # 800x800 max
│   │   └── ...
│   └── jpeg_watermarked/        # Step 8 output
│       ├── image001.jpg         # With watermark (restricted only)
│       └── ...
│
├── config/
│   └── project_config.yaml      # Batch configuration
│
├── logs/
│   └── batch_{id}.log           # Batch-specific logs
│
└── reports/
    ├── unicode_report.txt       # Step 3 report
    └── embedding_report.txt     # Step 5 report
```

---

## 5. Component Descriptions

### 5.1 Configuration Management

#### 5.1.1 ConfigManager (`config/config_manager.py`)

**Purpose**: Centralized configuration handling with hierarchical key access.

**Key Features**:

- YAML file loading and saving
- Dot-notation key access (e.g., `project.name`)
- Default value merging
- Step status tracking
- Configuration validation

**Interface**:

```python
class ConfigManager:
    def load_config(path: Path) -> Dict
    def save_config(data: Dict, path: Path) -> None
    def get(key: str, default: Any = None) -> Any
    def set(key: str, value: Any) -> None
    def update_step_status(step_num: int, completed: bool) -> None
    def get_next_step() -> Optional[int]
    def validate_config() -> ValidationResult
    def to_dict() -> Dict
```

#### 5.1.2 BatchRegistry (`utils/batch_registry.py`)

**Purpose**: Track and manage multiple batch projects.

**Key Features**:

- Register/unregister batches
- Status lifecycle (active → completed → archived)
- Persistence to YAML file
- Quick batch lookup

**Interface**:

```python
class BatchRegistry:
    def register_batch(name: str, data_dir: Path, config_path: Path) -> str
    def get_batch(batch_id: str) -> Optional[Dict]
    def update_batch_status(batch_id: str, status: str) -> bool
    def get_active_batches() -> List[Dict]
    def unregister_batch(batch_id: str) -> bool
```

### 5.2 Step Processing

#### 5.2.1 StepProcessor (`steps/base_step.py`)

**Purpose**: Abstract base class for all processing steps.

**Template Method Pattern**:

```python
class StepProcessor(ABC):
    step_num: int
    step_name: str

    def run(context: ProcessingContext) -> StepResult:
        """Template method - orchestrates step execution"""
        self.setup(context)

        validation = self.validate_inputs(context)
        if not validation.is_valid:
            return StepResult(success=False, message=validation.errors[0])

        result = self.execute(context)
        if not result.success:
            return result

        validation = self.validate_outputs(context)
        if not validation.is_valid:
            return StepResult(success=False, message=validation.errors[0])

        context.config.update_step_status(self.step_num, True)
        return result

    @abstractmethod
    def validate_inputs(context) -> ValidationResult: ...

    @abstractmethod
    def execute(context) -> StepResult: ...

    @abstractmethod
    def validate_outputs(context) -> ValidationResult: ...
```

#### 5.2.2 ProcessingContext (`steps/base_step.py`)

**Purpose**: Shared state container passed through pipeline.

**Attributes**:

```python
@dataclass
class ProcessingContext:
    paths: PathManager          # Path resolution
    config: ConfigManager       # Configuration access
    logger: logging.Logger      # Logging instance
    current_step: int           # Current step number
    batch_id: Optional[str]     # Batch identifier
    shared_data: Dict           # Inter-step data exchange

    def set_data(key: str, value: Any) -> None
    def get_data(key: str, default: Any = None) -> Any
```

### 5.3 GUI Components

#### 5.3.1 MainWindow (`gui/main_window.py`)

**Purpose**: Primary application window with tabbed interface.

**Structure**:

```python
class MainWindow(QMainWindow):
    # Tabs
    batches_tab: QWidget          # BatchListWidget
    current_batch_tab: QWidget    # StepWidget
    config_tab: QWidget           # ConfigWidget
    logs_tab: QWidget             # EnhancedLogWidget

    # State
    current_batch_id: Optional[str]
    framework: HSLTFramework

    # Signals
    batch_selected = pyqtSignal(str, dict)
```

#### 5.3.2 StepWidget (`gui/widgets/step_widget.py`)

**Purpose**: Step execution interface with status tracking.

**Features**:

- 8 step buttons in 2-column grid
- Individual step controls (Run, Revert)
- Status indicators (Pending, Running, Completed, Error)
- Batch-level actions (Run All, Run Next, Validate)
- Output log display

**Signals**:

```python
step_executed = pyqtSignal(int, bool)  # step_num, success
```

#### 5.3.3 ThemeManager (`gui/theme_manager.py`)

**Purpose**: Application-wide theme management (Singleton).

**Features**:

- Light/Dark/System themes
- Semantic color definitions
- Settings persistence via QSettings
- Signal-based theme change notifications

**Interface**:

```python
class ThemeManager:
    @classmethod
    def instance(cls) -> ThemeManager

    def get_current_theme() -> str
    def set_theme(theme_name: str) -> None
    def get_color(color_name: str) -> QColor

    # Signal
    theme_changed = pyqtSignal(object)
```

### 5.4 Logging Infrastructure

#### 5.4.1 LogManager (`utils/log_manager.py`)

**Purpose**: Centralized logging with GUI integration (Singleton).

**Features**:

- Session-level logging (application lifetime)
- Per-batch logging (separate files)
- GUI signal emission for real-time display
- Console capture (stdout/stderr)
- Verbosity control (minimal/normal/detailed)

**Interface**:

```python
class LogManager:
    @staticmethod
    def instance() -> LogManager

    def setup_session_logging(log_dir: Path, verbosity: str) -> None
    def setup_batch_logging(batch_dir: Path, batch_id: str) -> None
    def get_gui_handler() -> GUILogHandler

    # Convenience methods
    def debug(message, batch_id=None, step=None) -> None
    def info(message, batch_id=None, step=None) -> None
    def success(message, batch_id=None, step=None) -> None
    def warning(message, batch_id=None, step=None) -> None
    def error(message, batch_id=None, step=None) -> None

    def step_start(step_num, step_name, batch_id=None) -> None
    def step_complete(step_num, step_name, batch_id=None) -> None
```

---

## 6. Data Architecture

### 6.1 Configuration Schema

#### 6.1.1 Project Configuration (project_config.yaml)

```yaml
project:
  name: "Batch Name"
  data_directory: "C:\\path\\to\\data"
  created: "2026-01-23T10:30:00"

steps_completed:
  step1: true
  step2: true
  step3: false
  step4: false
  step5: false
  step6: false
  step7: false
  step8: false

step_configurations:
  step1:
    required_fields: ["Accession Number", "Title", "Date"]
    validation_strict: true
  step2:
    output_filename: "export.csv"
    validate_row_count: true
  step3:
    generate_reports: true
    encoding: "utf-8"
  step4:
    target_bit_depth: 8
    backup_original: false
  step5:
    generate_reports: true
    validate_embedding: true
  step6:
    quality: 85
    preserve_metadata: true
  step7:
    max_dimension: 800
    maintain_aspect_ratio: true
    quality: 85
  step8:
    watermark_opacity: 0.3
    watermark_position: "center"
    only_restricted: true

logging:
  level: "INFO"
  verbosity: "normal"

validation:
  strict_mode: false
  auto_backup: true
```

#### 6.1.2 Batch Registry (batch_registry.yaml)

```yaml
batches:
  abc123def456:
    name: "January 2026 Batch"
    data_directory: "C:\\Data\\January2026"
    config_path: "C:\\Data\\January2026\\config\\project_config.yaml"
    created: "2026-01-15T09:00:00"
    last_accessed: "2026-01-23T19:45:00"
    status: "active"

  xyz789ghi012:
    name: "December 2025 Archive"
    data_directory: "C:\\Data\\December2025"
    config_path: "C:\\Data\\December2025\\config\\project_config.yaml"
    created: "2025-12-01T10:00:00"
    last_accessed: "2025-12-20T16:30:00"
    status: "archived"
```

### 6.2 Data Flow Through Steps

```
┌─────────────────────────────────────────────────────────────────┐
│ Step 1: Excel Spreadsheet Preparation                           │
│   Input:  User selection                                        │
│   Output: input/spreadsheet/metadata.xlsx                       │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 2: CSV Conversion                                          │
│   Input:  input/spreadsheet/metadata.xlsx                       │
│   Output: output/csv/export.csv                                 │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 3: Unicode Filtering                                       │
│   Input:  output/csv/export.csv                                 │
│   Output: output/csv/export.csv (cleaned)                       │
│           reports/unicode_report.txt                            │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 4: TIFF Bit Depth Conversion                               │
│   Input:  input/tiff/*.tif (16-bit)                             │
│   Output: input/tiff/*.tif (8-bit, in-place conversion)         │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 5: Metadata Embedding                                      │
│   Input:  input/tiff/*.tif + output/csv/export.csv              │
│   Output: output/tiff_processed/*.tif (with EXIF/IPTC)          │
│           reports/embedding_report.txt                          │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 6: JPEG Conversion                                         │
│   Input:  output/tiff_processed/*.tif                           │
│   Output: output/jpeg/*.jpg                                     │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 7: JPEG Resizing                                           │
│   Input:  output/jpeg/*.jpg                                     │
│   Output: output/jpeg_resized/*.jpg (800x800 max)               │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 8: Watermark Addition                                      │
│   Input:  output/jpeg_resized/*.jpg + restriction data          │
│   Output: output/jpeg_watermarked/*.jpg (restricted items only) │
└─────────────────────────────────────────────────────────────────┘
```

---

## 7. Interface Specifications

### 7.1 Command Line Interface

```
hstl_framework.py <command> [options]

Commands:
  init <name>          Initialize new project
    --data-dir PATH    Data directory (required)

  run                  Execute processing steps
    --step N           Run specific step (1-8)
    --start N          Start from step N
    --end N            End at step N
    --dry-run          Preview without executing

  status               Show current project status

  validate             Validate project configuration

  config               Configuration operations
    --get KEY          Get configuration value
    --set KEY VALUE    Set configuration value
    --show             Display full configuration

  gui                  Launch GUI application

  batches              List registered batches
    --active           Show only active batches

  batch <id>           Select batch for operations
    --info             Show batch details
```

### 7.2 GUI Signal Interface

```python
# MainWindow Signals
batch_selected = pyqtSignal(str, dict)    # batch_id, batch_info

# BatchListWidget Signals
batch_selected = pyqtSignal(str, dict)    # batch_id, batch_info
batch_action_requested = pyqtSignal(str, str)  # action, batch_id

# StepWidget Signals
step_executed = pyqtSignal(int, bool)     # step_num, success

# ConfigWidget Signals
config_changed = pyqtSignal()

# ThemeManager Signals
theme_changed = pyqtSignal(object)        # theme_data

# ZoomManager Signals
zoom_changed = pyqtSignal(float)          # zoom_factor

# LogManager (GUILogHandler) Signals
log_emitted = pyqtSignal(object)          # LogRecord
```

### 7.3 External Tool Interface

#### 7.3.1 ExifTool Integration

```python
# Via PyExifTool wrapper
import exiftool

with exiftool.ExifTool() as et:
    # Read metadata
    metadata = et.get_metadata(image_path)

    # Write metadata
    et.execute(
        "-IPTC:Caption-Abstract=Description text",
        "-EXIF:ImageDescription=Title",
        image_path
    )
```

**Required metadata fields**:

- IPTC:Caption-Abstract
- IPTC:Keywords
- IPTC:Source
- EXIF:ImageDescription
- EXIF:Copyright

---

## 8. Design Patterns

### 8.1 Singleton Pattern

**Used for**: Application-wide resource managers

**Implementations**:

```python
# ThemeManager
class ThemeManager:
    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = ThemeManager()
        return cls._instance

# ZoomManager
class ZoomManager:
    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = ZoomManager()
        return cls._instance

# LogManager
class LogManager:
    _instance = None

    @staticmethod
    def instance():
        if LogManager._instance is None:
            LogManager._instance = LogManager()
        return LogManager._instance
```

### 8.2 Template Method Pattern

**Used for**: Step processor execution lifecycle

```python
class StepProcessor(ABC):
    def run(self, context):  # Template method
        self.setup(context)

        if not self.validate_inputs(context).is_valid:
            return error_result

        result = self.execute(context)  # Abstract - varies

        if not self.validate_outputs(context).is_valid:
            return error_result

        return result

    @abstractmethod
    def execute(self, context): ...  # Subclass implements
```

### 8.3 Observer Pattern (Signals/Slots)

**Used for**: Decoupled component communication in GUI

```python
# Publisher
class StepWidget(QWidget):
    step_executed = pyqtSignal(int, bool)

    def _on_step_complete(self, step_num, success):
        self.step_executed.emit(step_num, success)

# Subscriber
class MainWindow(QMainWindow):
    def __init__(self):
        self.step_widget.step_executed.connect(self._handle_step_result)

    def _handle_step_result(self, step_num, success):
        self._update_batch_progress()
```

### 8.4 Context Object Pattern

**Used for**: Passing shared state through pipeline

```python
class ProcessingContext:
    def __init__(self, paths, config, logger, batch_id):
        self.paths = paths           # Injected dependencies
        self.config = config
        self.logger = logger
        self.batch_id = batch_id
        self.shared_data = {}        # Mutable state container

    def set_data(self, key, value):
        self.shared_data[key] = value

    def get_data(self, key, default=None):
        return self.shared_data.get(key, default)
```

### 8.5 Strategy Pattern

**Used for**: Validation with pluggable rules

```python
class ValidationResult:
    def __init__(self, is_valid, errors=None, warnings=None):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []

class Validator:
    @staticmethod
    def validate_file_exists(path):
        if path.exists():
            return ValidationResult(True)
        return ValidationResult(False, [f"File not found: {path}"])
```

---

## 9. External Dependencies

### 9.1 Python Packages

| Package    | Version  | Purpose                      |
| ---------- | -------- | ---------------------------- |
| PyQt6      | >=6.0.0  | GUI framework                |
| PyYAML     | >=6.0    | YAML configuration parsing   |
| pandas     | >=1.5.0  | CSV/Excel data processing    |
| Pillow     | >=9.0.0  | Image processing (TIFF/JPEG) |
| PyExifTool | >=0.5.0  | ExifTool Python wrapper      |
| pydantic   | >=1.10.0 | Data validation              |
| ftfy       | >=6.0.0  | Unicode text fixing          |
| tqdm       | >=4.64.0 | Progress bars                |
| colorama   | >=0.4.4  | Colored terminal output      |
| structlog  | >=22.0.0 | Structured logging           |
| openpyxl   | >=3.0.0  | Excel .xlsx reading          |
| xlrd       | >=2.0.0  | Excel .xls reading           |

### 9.2 External Tools

| Tool      | Purpose                  | Integration            |
| --------- | ------------------------ | ---------------------- |
| ExifTool  | Metadata read/write      | Via PyExifTool wrapper |
| TagWriter | Image viewing (optional) | System call            |

### 9.3 Network Services

| Service    | Purpose          | Usage                               |
| ---------- | ---------------- | ----------------------------------- |
| GitHub API | Version checking | `api.github.com/repos/.../releases` |
| GitHub     | Source updates   | `git pull` operations               |

---

## 10. Quality Attributes

### 10.1 Performance

| Attribute            | Target            | Implementation              |
| -------------------- | ----------------- | --------------------------- |
| Startup time         | <3 seconds        | Lazy initialization         |
| Step execution       | Progress feedback | Real-time UI updates        |
| Large batch handling | 1000+ images      | Streaming processing        |
| Memory usage         | <500MB typical    | Chunk-based file processing |

### 10.2 Reliability

| Attribute            | Implementation                          |
| -------------------- | --------------------------------------- |
| Error recovery       | Step-level error handling with rollback |
| Data integrity       | Validation before/after each step       |
| Configuration backup | Auto-backup before changes              |
| Crash recovery       | Persistent step completion tracking     |

### 10.3 Maintainability

| Attribute     | Implementation                             |
| ------------- | ------------------------------------------ |
| Modularity    | Layered architecture with clear interfaces |
| Testability   | 296 tests (unit, integration, GUI)         |
| Documentation | Inline docstrings, markdown docs           |
| Logging       | Comprehensive logging at all levels        |

### 10.4 Usability

| Attribute         | Implementation                              |
| ----------------- | ------------------------------------------- |
| Dual interface    | CLI for automation, GUI for interactive use |
| Progress feedback | Real-time status in UI and logs             |
| Error messages    | User-friendly with actionable guidance      |
| Themes            | Light/Dark modes for accessibility          |

### 10.5 Security

| Attribute        | Implementation                               |
| ---------------- | -------------------------------------------- |
| Local processing | No cloud data transmission                   |
| File validation  | Input validation before processing           |
| Safe operations  | Confirmation dialogs for destructive actions |

---

## 11. Appendices

### 11.1 The 8 Processing Steps

| Step | Name                          | Input           | Output                   | Description                              |
| ---- | ----------------------------- | --------------- | ------------------------ | ---------------------------------------- |
| 1    | Excel Spreadsheet Preparation | User selection  | input/spreadsheet/*.xlsx | Select and validate metadata spreadsheet |
| 2    | CSV Conversion                | Excel file      | output/csv/export.csv    | Convert Excel to CSV format              |
| 3    | Unicode Filtering             | CSV file        | Cleaned CSV + report     | Fix encoding issues and mojibake         |
| 4    | TIFF Bit Depth Conversion     | 16-bit TIFFs    | 8-bit TIFFs              | Convert color depth for compatibility    |
| 5    | Metadata Embedding            | TIFFs + CSV     | TIFFs with EXIF/IPTC     | Embed metadata using ExifTool            |
| 6    | JPEG Conversion               | Processed TIFFs | JPEG files               | Convert to JPEG format                   |
| 7    | JPEG Resizing                 | JPEG files      | Resized JPEGs            | Resize to 800x800 max dimension          |
| 8    | Watermark Addition            | Resized JPEGs   | Watermarked JPEGs        | Add watermarks to restricted images      |

### 11.2 Configuration Keys Reference

```
project.name                          # Project name
project.data_directory                # Base data directory
project.created                       # Creation timestamp

steps_completed.step1                 # Step 1 completion status
steps_completed.step2                 # Step 2 completion status
...
steps_completed.step8                 # Step 8 completion status

step_configurations.step1.required_fields
step_configurations.step2.output_filename
step_configurations.step4.target_bit_depth
step_configurations.step5.generate_reports
step_configurations.step6.quality
step_configurations.step7.max_dimension
step_configurations.step8.watermark_opacity

logging.level                         # Log level (DEBUG/INFO/WARNING/ERROR)
logging.verbosity                     # Verbosity (minimal/normal/detailed)

validation.strict_mode                # Strict validation enabled
validation.auto_backup                # Auto-backup enabled
```

### 11.3 Log Levels

| Level    | Value | Emoji | Usage                           |
| -------- | ----- | ----- | ------------------------------- |
| DEBUG    | 10    | ⚡     | Detailed debugging information  |
| INFO     | 20    | 🔹    | General operational information |
| SUCCESS  | 25    | ✅     | Successful operation completion |
| WARNING  | 30    | ⚠️    | Warning conditions              |
| ERROR    | 40    | ❌     | Error conditions                |
| CRITICAL | 50    | ❌     | Critical failures               |

### 11.4 Version History

See [CHANGELOG.md](../CHANGELOG.md) for complete version history.

---

**Document Version:** 1.0
**Last Updated:** 2026-01-23 19:45 CST
**Framework Version:** 0.1.7l
