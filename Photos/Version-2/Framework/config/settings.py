"""
Default Settings for HSTL Photo Framework

Contains default configuration values used when no project-specific
configuration is provided.
"""

# Default framework configuration
DEFAULT_SETTINGS = {
    # Project settings (will be overridden by project-specific config)
    "project": {
        "name": "HSTL_Photo_Project",
        "data_directory": None,
        "created": None,
    },
    # Processing steps completion status
    "steps_completed": {
        "step1": False,  # Excel Spreadsheet Preparation
        "step2": False,  # CSV Conversion
        "step3": False,  # Unicode Filtering
        "step4": False,  # TIFF Bit Depth Conversion
        "step5": False,  # Metadata Embedding
        "step6": False,  # JPEG Conversion
        "step7": False,  # JPEG Resizing
        "step8": False,  # Watermark Addition
    },
    # Step-specific configurations
    "step_configurations": {
        "step1": {
            "required_fields": [
                "Title",
                "Accession Number",
                "Restrictions",
                "Scopenote",
                "Related Collection",
                "Source Photographer",
                "Institutional Creator",
            ],
            "validation_strict": True,
            "excel_extensions": [".xlsx", ".xls"],
            "validation_headers": [
                "Title",
                "Accession Number",
                "Restrictions",
                "Scopenote",
                "Related Collection",
                "Source Photographer",
                "Institutional Creator",
            ],
        },
        "step2": {
            "output_filename": "export.csv",
            "validate_row_count": True,
            "excel_required": True,
        },
        "step3": {
            "generate_reports": True,
            "backup_original": True,
            "encoding": "utf-8",
        },
        "step4": {
            "target_bit_depth": 8,
            "backup_original": True,
            "quality_check": True,
        },
        "step5": {
            "generate_reports": True,
            "validate_embedding": True,
            "backup_on_error": True,
        },
        "step6": {
            "quality": 85,
            "validate_count": True,
            "preserve_metadata": True,
        },
        "step7": {
            "max_dimension": 800,
            "maintain_aspect_ratio": True,
            "quality": 85,
        },
        "step8": {
            "watermark_opacity": 0.3,
            "watermark_position": "bottom_right",
            "only_restricted": True,
        },
    },
    # Logging configuration
    "logging": {
        "level": "INFO",
        "verbosity": "normal",  # 'minimal', 'normal', 'detailed'
        "file": None,  # Will be set to data_directory/logs/framework.log
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "max_file_size": "10MB",
        "backup_count": 5,
        "per_batch_logging": True,  # Enable per-batch log files
        "gui_log_buffer": 1000,  # Max lines to keep in GUI log viewer
    },
    # Validation settings
    "validation": {
        "strict_mode": True,
        "auto_backup": True,
        "validate_paths": True,
        "pre_flight_checks": True,
    },
    # Pipeline settings
    "pipeline": {
        "stop_on_error": True,
        "create_checkpoints": True,
        "parallel_processing": False,
        "max_workers": 4,
    },
    # Directory structure
    "directories": {
        "input": {
            "tiff": "input/tiff",
            "spreadsheet": "input/spreadsheet",
        },
        "output": {
            "csv": "output/csv",
            "tiff_processed": "output/tiff_processed",
            "jpeg": "output/jpeg",
            "jpeg_resized": "output/jpeg_resized",
            "jpeg_watermarked": "output/jpeg_watermarked",
        },
        "reports": "reports",
        "logs": "logs",
        "config": "config",
        "temp": "temp",
    },
    # External tool paths (will be auto-detected or configured per project)
    "tools": {
        "nomacs": None,
        "tagwriter": None,
        "exiftool": None,
    },
    # File patterns and extensions
    "file_patterns": {
        "tiff": ["*.tif", "*.tiff"],
        "jpeg": ["*.jpg", "*.jpeg"],
        "csv": ["*.csv"],
        "yaml": ["*.yaml", "*.yml"],
    },
    # Performance settings
    "performance": {
        "chunk_size": 100,
        "memory_limit": "1GB",
        "temp_cleanup": True,
    },
}

# Step names mapping for human-readable display
STEP_NAMES = {
    1: "Google Spreadsheet Preparation",
    2: "CSV Conversion",
    3: "Unicode Filtering",
    4: "TIFF Bit Depth Conversion",
    5: "Metadata Embedding",
    6: "JPEG Conversion",
    7: "JPEG Resizing",
    8: "Watermark Addition",
}

# Validation rules for each step
STEP_VALIDATION_RULES = {
    1: {
        "required_inputs": ["tiff_files"],
        "expected_outputs": ["google_spreadsheet"],
        "validation_checks": ["required_fields_complete"],
    },
    2: {
        "required_inputs": ["google_spreadsheet"],
        "expected_outputs": ["csv_file"],
        "validation_checks": ["row_count_matches_accession_numbers"],
    },
    3: {
        "required_inputs": ["csv_file"],
        "expected_outputs": ["filtered_csv_file", "unicode_report"],
        "validation_checks": ["encoding_issues_resolved"],
    },
    4: {
        "required_inputs": ["tiff_files_16bit"],
        "expected_outputs": ["tiff_files_8bit"],
        "validation_checks": ["bit_depth_conversion"],
    },
    5: {
        "required_inputs": ["tiff_files", "csv_file"],
        "expected_outputs": ["tiff_files_with_metadata", "embedding_report"],
        "validation_checks": ["metadata_embedded_correctly"],
    },
    6: {
        "required_inputs": ["tiff_files_with_metadata"],
        "expected_outputs": ["jpeg_files"],
        "validation_checks": ["file_count_matches"],
    },
    7: {
        "required_inputs": ["jpeg_files"],
        "expected_outputs": ["jpeg_files_resized"],
        "validation_checks": ["dimensions_within_bounds"],
    },
    8: {
        "required_inputs": ["jpeg_files_resized"],
        "expected_outputs": ["jpeg_files_watermarked"],
        "validation_checks": ["watermark_applied_correctly"],
    },
}

# CLI color scheme
CLI_COLORS = {
    "success": "green",
    "warning": "yellow",
    "error": "red",
    "info": "cyan",
    "step": "blue",
    "validation": "magenta",
}
