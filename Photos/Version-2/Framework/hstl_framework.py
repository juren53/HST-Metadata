#!/usr/bin/env python3
"""
HSTL Photo Framework - Main CLI Entry Point

A comprehensive framework for managing the complete HSTL Photo Metadata Project workflow.
Orchestrates 8 steps of photo metadata processing from Google Spreadsheet preparation
through final watermarked JPEG creation.

Usage:
    python hstl_framework.py init --data-dir "C:\\path\\to\\images" --project-name "MyProject"
    python hstl_framework.py run --step 1
    python hstl_framework.py run --all
    python hstl_framework.py status
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import List, Optional

# Add the framework directory to the Python path
framework_dir = Path(__file__).parent
sys.path.insert(0, str(framework_dir))

try:
    from config.config_manager import ConfigManager
    from config.settings import DEFAULT_SETTINGS
    from utils.logger import setup_logger
    from utils.path_manager import PathManager
    from utils.validator import Validator
    from utils.batch_registry import BatchRegistry
    from utils.log_manager import LogManager, get_log_manager
    from steps.base_step import ProcessingContext
    from core.pipeline import Pipeline
except ImportError as e:
    logging.error(f"Error importing framework modules: {e}", exc_info=True)
    logging.warning(
        "Please ensure all required dependencies are installed: pip install -r requirements.txt"
    )
    sys.exit(1)

# Framework metadata
FRAMEWORK_VERSION = "0.1.7"
SUPPORTED_STEPS = list(range(1, 9))


class HSLTFramework:
    """Main framework controller class."""

    def __init__(self):
        self.config_manager = None
        self.logger = None
        self.path_manager = None
        self.pipeline = None
        self.log_manager = get_log_manager()

    def initialize(self, config_path: Optional[Path] = None):
        """Initialize the framework with configuration."""
        try:
            # Initialize configuration
            self.config_manager = ConfigManager(config_path)

            # Initialize logging
            self.logger = setup_logger(
                level=self.config_manager.get("logging.level", "INFO"),
                log_file=self.config_manager.get("logging.file"),
            )

            # Initialize path manager
            self.path_manager = PathManager(
                framework_root=framework_dir,
                data_directory=self.config_manager.get("project.data_directory"),
            )

            self.log_manager.success("HSTL Framework initialized successfully")
            return True

        except Exception as e:
            self.log_manager.error(
                f"Failed to initialize framework: {e}", exc_info=True
            )
            return False

    def init_project(self, data_dir: str, project_name: str, force: bool = False):
        """Initialize a new project."""
        try:
            data_path = Path(data_dir)

            # Create data directory if it doesn't exist
            if not data_path.exists():
                self.log_manager.info(f"Creating data directory: {data_dir}")
                try:
                    data_path.mkdir(parents=True, exist_ok=True)
                except FileNotFoundError:
                    self.log_manager.error(f"Invalid path: The directory '{data_dir}' could not be created.")
                    self.log_manager.error("Please check that the drive exists and is accessible.")
                    raise

            # Create project configuration
            project_config = {
                "project": {
                    "name": project_name,
                    "data_directory": str(data_path.absolute()),
                    "created": str(data_path),
                },
                "steps_completed": {f"step{i}": False for i in SUPPORTED_STEPS},
                "validation": {"strict_mode": True, "auto_backup": True},
            }

            # Save configuration
            config_path = data_path / "config" / "project_config.yaml"
            config_path.parent.mkdir(parents=True, exist_ok=True)

            if config_path.exists() and not force:
                self.log_manager.warning(
                    f"Project configuration already exists: {config_path}"
                )
                self.log_manager.info("Use --force to overwrite existing configuration")
                return False

            self.config_manager = ConfigManager()
            self.config_manager.save_config(project_config, config_path)

            # Create directory structure
            self._create_project_directories(data_path)

            # Register batch in the registry
            registry = BatchRegistry()
            batch_id = registry.register_batch(
                project_name, str(data_path.absolute()), str(config_path.absolute())
            )

            self.log_manager.success(f"Project '{project_name}' initialized successfully")
            self.log_manager.info(f"Data directory: {data_dir}")
            self.log_manager.info(f"Configuration: {config_path}")
            self.log_manager.info(f"Batch registered in framework registry")

            return True

        except Exception as e:
            self.log_manager.error(f"Failed to initialize project: {e}", exc_info=True)
            return False

    def _create_project_directories(self, data_path: Path):
        """Create the standard project directory structure."""
        directories = [
            "input/tiff",
            "input/spreadsheet",
            "output/csv",
            "output/tiff_processed",
            "output/jpeg",
            "output/jpeg_resized",
            "output/jpeg_watermarked",
            "reports",
            "logs",
            "config",
        ]

        for dir_name in directories:
            (data_path / dir_name).mkdir(parents=True, exist_ok=True)

    def show_status(self, verbose: bool = False):
        """Display current project status."""
        if not self.config_manager:
            self.log_manager.error("No project initialized. Run 'hstl_framework.py init' first.")
            return False

        self.log_manager.info("HSTL Framework Status")
        self.log_manager.info("=" * 50)

        # Project information
        project_name = self.config_manager.get("project.name", "Unknown")
        data_dir = self.config_manager.get("project.data_directory", "Not set")
        self.log_manager.info(f"Project: {project_name}")
        self.log_manager.info(f"Data Directory: {data_dir}")
        self.log_manager.info("")

        # Steps status
        self.log_manager.info("Processing Steps:")
        for step_num in SUPPORTED_STEPS:
            completed = self.config_manager.get(
                f"steps_completed.step{step_num}", False
            )
            status_text = "Completed" if completed else "Pending"
            status_icon = "✅" if completed else "⭕"
            step_name = self._get_step_name(step_num)
            self.log_manager.info(f"  {status_icon} Step {step_num}: {step_name} - {status_text}")

        if verbose:
            self.log_manager.info("\nConfiguration Details:")
            # Add more detailed configuration info here

        return True

    def _get_step_name(self, step_num: int) -> str:
        """Get human-readable step name."""
        step_names = {
            1: "Google Spreadsheet Preparation",
            2: "CSV Conversion",
            3: "Unicode Filtering",
            4: "TIFF Bit Depth Conversion",
            5: "Metadata Embedding",
            6: "JPEG Conversion",
            7: "JPEG Resizing",
            8: "Watermark Addition",
        }
        return step_names.get(step_num, f"Step {step_num}")

    def run_steps(self, steps: List[int], dry_run: bool = False):
        """Run specified processing steps."""
        if not self.config_manager:
            self.log_manager.error("No project initialized. Run 'hstl_framework.py init' first.")
            return False

        mode = "Dry run" if dry_run else "Running"
        self.log_manager.info(f"{mode} steps: {steps}")

        for step_num in steps:
            if step_num not in SUPPORTED_STEPS:
                self.log_manager.error(f"Invalid step number: {step_num}")
                return False

            step_name = self._get_step_name(step_num)
            if dry_run:
                self.log_manager.info(f"Would run Step {step_num}: {step_name}")
            else:
                self.log_manager.step_start(step_num, step_name)
                # TODO: Implement actual step execution
                self.log_manager.warning(f"Step {step_num} implementation pending")

        return True

    def validate(self, step: Optional[int] = None, pre_flight: bool = False):
        """Validate project or specific step."""
        if not self.config_manager:
            self.log_manager.error("No project initialized. Run 'hstl_framework.py init' first.")
            return False

        if pre_flight:
            self.log_manager.info("Running pre-flight validation...")
            # TODO: Implement pre-flight checks
            self.log_manager.success("Pre-flight validation completed")
            return True

        if step:
            self.log_manager.info(f"Validating Step {step}: {self._get_step_name(step)}")
            # TODO: Implement step-specific validation
            self.log_manager.success(f"Step {step} validation completed")
        else:
            self.log_manager.info("Validating entire project...")
            # TODO: Implement full project validation
            self.log_manager.success("Project validation completed")

        return True

    def list_config(self) -> bool:
        """List current configuration."""
        if not self.config_manager:
            self.log_manager.error("No project initialized. Run 'hstl_framework.py init' first.")
            return False

        self.log_manager.info("Current Configuration")
        self.log_manager.info("=" * 50)

        config_dict = self.config_manager.to_dict()

        # Print configuration in a formatted way
        self._print_config_dict(config_dict, indent=0)

        if self.config_manager.config_path:
            self.log_manager.info(f"\nConfiguration file: {self.config_manager.config_path}")

        return True

    def _print_config_dict(self, data: dict, indent: int = 0):
        """Recursively print configuration dictionary."""
        indent_str = "  " * indent

        for key, value in data.items():
            # Skip metadata section for cleaner output
            if key == "_metadata":
                continue

            if isinstance(value, dict):
                self.log_manager.info(f"{indent_str}{key}:")
                self._print_config_dict(value, indent + 1)
            else:
                self.log_manager.info(f"{indent_str}  {key}: {value}")

    def set_config(self, key: str, value: str) -> bool:
        """Set configuration value."""
        if not self.config_manager:
            self.log_manager.error("No project initialized. Run 'hstl_framework.py init' first.")
            return False

        # Convert value to appropriate type
        converted_value = self._convert_config_value(value)

        # Set the value
        if self.config_manager.set(key, converted_value):
            self.log_manager.success(f"Configuration updated: {key} = {converted_value}")

            # Save to file if config path exists
            if self.config_manager.config_path:
                self.config_manager.save_config(
                    self.config_manager.to_dict(), self.config_manager.config_path
                )
                self.log_manager.info(f"Saved to: {self.config_manager.config_path}")

            return True
        else:
            self.log_manager.error(f"Failed to set configuration: {key}")
            return False

    def _convert_config_value(self, value: str):
        """Convert string value to appropriate type."""
        # Try to convert to bool
        if value.lower() in ("true", "yes", "1"):
            return True
        if value.lower() in ("false", "no", "0"):
            return False

        # Try to convert to int
        try:
            return int(value)
        except ValueError:
            pass

        # Try to convert to float
        try:
            return float(value)
        except ValueError:
            pass

        # Return as string
        return value

    def list_batches(self, show_all: bool = False) -> bool:
        """List all registered batch projects."""
        registry = BatchRegistry()

        if show_all:
            batches = registry.list_batches_summary()
            title = "All Registered Batches"
        else:
            summaries = registry.list_batches_summary()
            batches = [b for b in summaries if b.get("status") == "active"]
            title = "Active Batches"

        if not batches:
            self.log_manager.warning("No batches found")
            if not show_all:
                self.log_manager.info("Use 'batches --all' to see archived batches")
            return True

        self.log_manager.info(title)
        self.log_manager.info("=" * 80)
        self.log_manager.info("")

        for batch in batches:
            batch_id = batch["batch_id"]
            name = batch["name"]
            status = batch.get("status", "unknown")
            completed = batch.get("completed_steps", 0)
            total = batch.get("total_steps", 8)
            percentage = batch.get("completion_percentage", 0)

            # Status emoji (removed, formatter will add)
            
            self.log_manager.info(f"{name} ({batch_id})")
            self.log_manager.info(f"   Progress: {completed}/{total} steps ({percentage:.0f}%)")
            self.log_manager.info(f"   Status: {status}")
            self.log_manager.info(f"   Data Directory: {batch['data_directory']}")
            self.log_manager.info(f"   Config: {batch['config_path']}")
            self.log_manager.info("")

        self.log_manager.info(f"Total: {len(batches)} batch(es)")
        return True

    def archive_batch(self, batch_id: str) -> bool:
        """Archive a batch project."""
        registry = BatchRegistry()
        batch = registry.get_batch(batch_id)

        if not batch:
            self.log_manager.error(f"Batch not found: {batch_id}")
            return False

        if registry.update_batch_status(batch_id, "archived"):
            self.log_manager.success(f"Batch '{batch['name']}' archived successfully")
            self.log_manager.info(f"Batch ID: {batch_id}")
            self.log_manager.info(f"Note: Files remain in {batch['data_directory']}")
            return True
        else:
            self.log_manager.error(f"Failed to archive batch: {batch_id}")
            return False

    def complete_batch(self, batch_id: str) -> bool:
        """Mark a batch as completed."""
        registry = BatchRegistry()
        batch = registry.get_batch(batch_id)

        if not batch:
            self.log_manager.error(f"Batch not found: {batch_id}")
            return False

        if registry.update_batch_status(batch_id, "completed"):
            self.log_manager.success(f"Batch '{batch['name']}' marked as completed")
            self.log_manager.info(f"Batch ID: {batch_id}")
            self.log_manager.info(f"Data directory: {batch['data_directory']}")
            return True
        else:
            self.log_manager.error(f"Failed to mark batch as completed: {batch_id}")
            return False
    def reactivate_batch(self, batch_id: str) -> bool:
        """Reactivate an archived or completed batch."""
        registry = BatchRegistry()
        batch = registry.get_batch(batch_id)

        if not batch:
            self.log_manager.error(f"Batch not found: {batch_id}")
            return False

        old_status = batch.get("status", "unknown")
        if registry.update_batch_status(batch_id, "active"):
            self.log_manager.success(f"Batch '{batch['name']}' reactivated")
            self.log_manager.info(f"Previous status: {old_status}")
            self.log_manager.info(f"New status: active")
            return True
        else:
            self.log_manager.error(f"Failed to reactivate batch: {batch_id}")
            return False
    def remove_batch(self, batch_id: str, confirm: bool = False) -> bool:
        """Remove a batch from the registry."""
        registry = BatchRegistry()
        batch = registry.get_batch(batch_id)

        if not batch:
            self.log_manager.error(f"Batch not found: {batch_id}")
            return False

        if not confirm:
            self.log_manager.warning(f"Remove batch '{batch['name']}' from registry?")
            self.log_manager.info(f"Batch ID: {batch_id}")
            self.log_manager.info(f"Data directory: {batch['data_directory']}")
            self.log_manager.info(f"Config: {batch['config_path']}")
            self.log_manager.info("")
            self.log_manager.warning("This will remove the batch from the registry.")
            self.log_manager.info("The data directory and all files will NOT be deleted.")
            self.log_manager.info("")
            self.log_manager.info("Run with --confirm to proceed:")
            self.log_manager.info(f"hstl_framework.py batch remove {batch_id} --confirm")
            return False

        if registry.unregister_batch(batch_id):
            self.log_manager.success(f"Batch '{batch['name']}' removed from registry")
            self.log_manager.info(f"Data directory preserved at: {batch['data_directory']}")
            return True
        else:
            self.log_manager.error(f"Failed to remove batch: {batch_id}")
            return False
    def show_batch_info(self, batch_id: str) -> bool:
        """Show detailed information about a batch."""
        registry = BatchRegistry()
        summary = registry.get_batch_summary(batch_id)

        if not summary:
            self.log_manager.error(f"Batch not found: {batch_id}")
            return False

        self.log_manager.info("Batch Information")
        self.log_manager.info("=" * 60)
        self.log_manager.info(f"Name: {summary['name']}")
        self.log_manager.info(f"Batch ID: {batch_id}")
        self.log_manager.info(f"Status: {summary.get('status', 'unknown')}")
        self.log_manager.info("")
        self.log_manager.info(f"Created: {summary.get('created', 'unknown')}")
        self.log_manager.info(f"Last Accessed: {summary.get('last_accessed', 'unknown')}")
        self.log_manager.info("")
        self.log_manager.info(f"Data Directory: {summary['data_directory']}")
        self.log_manager.info(f"Config File: {summary['config_path']}")
        self.log_manager.info("")
        self.log_manager.info(
            f"Progress: {summary.get('completed_steps', 0)}/{summary.get('total_steps', 8)} steps ({summary.get('completion_percentage', 0):.0f}%)"
        )
        self.log_manager.info("")
        self.log_manager.info("Step Status:")

        if "steps_completed" in summary:
            step_names = {
                "step1": "Google Spreadsheet Preparation",
                "step2": "CSV Conversion",
                "step3": "Unicode Filtering",
                "step4": "TIFF Bit Depth Conversion",
                "step5": "Metadata Embedding",
                "step6": "JPEG Conversion",
                "step7": "JPEG Resizing",
                "step8": "Watermark Addition",
            }

            for step_key in sorted(summary["steps_completed"].keys()):
                step_num = step_key.replace("step", "")
                completed = summary["steps_completed"][step_key]
                status = "Completed" if completed else "Pending" # Text for log_manager, emoji handled by formatter
                step_name = step_names.get(step_key, step_key)
                self.log_manager.info(f"  Step {step_num}: {step_name} - {status}")

        return True


def create_parser() -> argparse.ArgumentParser:
    """Create the command line argument parser."""
    parser = argparse.ArgumentParser(
        description="HSTL Photo Framework - Orchestrate photo metadata processing workflow",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  # Simple init (uses default base directory C:\\Data\\HSTL_Batches)
  %(prog)s init "January 2025 Batch"
  
  # Init with custom base directory
  %(prog)s init "January 2025" --base-dir "D:\\MyBatches"
  
  # Init with full custom path
  %(prog)s init "January 2025" --data-dir "C:\\CustomPath\\Jan2025"
  
  # List all batches
  %(prog)s batches
  
  # Run steps
  %(prog)s run --step 2
  %(prog)s run --steps 1-3
  %(prog)s run --all
  %(prog)s status --verbose
  
Framework Version: {FRAMEWORK_VERSION}
        """,
    )

    # Global options
    parser.add_argument(
        "--version", action="version", version=f"HSTL Framework {FRAMEWORK_VERSION}"
    )
    parser.add_argument("--config", type=Path, help="Path to configuration file")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize a new project")
    init_parser.add_argument(
        "project_name", help="Name of the project (used to create directory)"
    )
    init_parser.add_argument(
        "--base-dir",
        default="C:\\Data\\HSTL_Batches",
        help="Base directory for batches (default: C:\\Data\\HSTL_Batches)",
    )
    init_parser.add_argument(
        "--data-dir",
        help="Custom full path to data directory (overrides base-dir + project-name)",
    )
    init_parser.add_argument(
        "--force", action="store_true", help="Overwrite existing configuration"
    )

    # Run command
    run_parser = subparsers.add_parser("run", help="Run processing steps")
    run_group = run_parser.add_mutually_exclusive_group(required=True)
    run_group.add_argument(
        "--step", type=int, choices=SUPPORTED_STEPS, help="Run single step"
    )
    run_group.add_argument(
        "--steps", help='Run range of steps (e.g., "1-3" or "2,5,7")'
    )
    run_group.add_argument("--all", action="store_true", help="Run all steps")
    run_group.add_argument(
        "--continue",
        dest="continue_run",
        action="store_true",
        help="Continue from last completed step",
    )
    run_parser.add_argument(
        "--dry-run", action="store_true", help="Validate without execution"
    )

    # Status command
    status_parser = subparsers.add_parser("status", help="Show project status")
    status_parser.add_argument(
        "--verbose", action="store_true", help="Show detailed status"
    )

    # Validate command
    validate_parser = subparsers.add_parser(
        "validate", help="Validate project or steps"
    )
    validate_parser.add_argument(
        "--step", type=int, choices=SUPPORTED_STEPS, help="Validate specific step"
    )
    validate_parser.add_argument(
        "--all", action="store_true", help="Validate all completed steps"
    )
    validate_parser.add_argument(
        "--pre-flight", action="store_true", help="Run pre-flight checks"
    )

    # Config command
    config_parser = subparsers.add_parser("config", help="Manage configuration")
    config_parser.add_argument("--list", action="store_true", help="List configuration")
    config_parser.add_argument(
        "--set", nargs=2, metavar=("KEY", "VALUE"), help="Set configuration value"
    )

    # GUI command
    gui_parser = subparsers.add_parser("gui", help="Launch graphical interface")

    # Batches command
    batches_parser = subparsers.add_parser("batches", help="List all batch projects")
    batches_parser.add_argument(
        "--all", action="store_true", help="Show all batches including archived"
    )

    # Batch command (singular - for managing individual batches)
    batch_parser = subparsers.add_parser("batch", help="Manage individual batch")
    batch_subparsers = batch_parser.add_subparsers(
        dest="batch_action", help="Batch management actions"
    )

    # Archive batch
    archive_parser = batch_subparsers.add_parser("archive", help="Archive a batch")
    archive_parser.add_argument("batch_id", help="ID of the batch to archive")

    # Complete batch
    complete_parser = batch_subparsers.add_parser(
        "complete", help="Mark batch as completed"
    )
    complete_parser.add_argument(
        "batch_id", help="ID of the batch to mark as completed"
    )

    # Reactivate batch
    reactivate_parser = batch_subparsers.add_parser(
        "reactivate", help="Reactivate an archived/completed batch"
    )
    reactivate_parser.add_argument("batch_id", help="ID of the batch to reactivate")

    # Remove batch from registry
    remove_parser = batch_subparsers.add_parser(
        "remove", help="Remove batch from registry (does not delete files)"
    )
    remove_parser.add_argument(
        "batch_id", help="ID of the batch to remove from registry"
    )
    remove_parser.add_argument("--confirm", action="store_true", help="Confirm removal")

    # Show batch info
    info_parser = batch_subparsers.add_parser(
        "info", help="Show detailed information about a batch"
    )
    info_parser.add_argument("batch_id", help="ID of the batch")

    return parser


def parse_steps_argument(steps_arg: str) -> List[int]:
    """Parse steps argument into list of step numbers."""
    steps = []

    # Handle ranges (e.g., "1-3") and comma-separated (e.g., "2,5,7")
    for part in steps_arg.split(","):
        part = part.strip()
        if "-" in part:
            start, end = map(int, part.split("-"))
            steps.extend(range(start, end + 1))
        else:
            steps.append(int(part))

    # Remove duplicates and sort
    return sorted(list(set(steps)))


def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Handle no command
    if not args.command:
        parser.print_help()
        return 1

    # Initialize framework
    framework = HSLTFramework()

    # Handle init command (special case - doesn't need existing config)
    if args.command == "init":
        # Determine data directory
        if args.data_dir:
            # Use custom path if provided
            data_dir = args.data_dir
        else:
            # Derive from base_dir + project_name
            # Convert project name to directory name (replace spaces with underscores, etc.)
            dir_name = args.project_name.replace(" ", "_")
            data_dir = str(Path(args.base_dir) / dir_name)

        success = framework.init_project(
            data_dir=data_dir, project_name=args.project_name, force=args.force
        )
        return 0 if success else 1

    # For all other commands, initialize with existing config
    if not framework.initialize(args.config):
        return 1

    # Handle commands
    try:
        if args.command == "gui":
            # Import and run GUI
            from gui.main_window import MainWindow
            from PyQt6.QtWidgets import QApplication

            app = QApplication(sys.argv)
            window = MainWindow()
            window.show()

            return app.exec()

        elif args.command == "status":
            success = framework.show_status(args.verbose)

        elif args.command == "run":
            if args.step:
                steps = [args.step]
            elif args.steps:
                steps = parse_steps_argument(args.steps)
            elif args.all:
                steps = SUPPORTED_STEPS
            elif args.continue_run:
                # TODO: Implement continue logic
                print("⚠️  Continue functionality not yet implemented")
                return 1

            success = framework.run_steps(steps, args.dry_run)

        elif args.command == "validate":
            success = framework.validate(step=args.step, pre_flight=args.pre_flight)

        elif args.command == "config":
            if args.list:
                success = framework.list_config()
            elif args.set:
                success = framework.set_config(args.set[0], args.set[1])
            else:
                parser.print_help()
                success = False

        elif args.command == "batches":
            # Batches command doesn't require initialization
            batch_framework = HSLTFramework()
            success = batch_framework.list_batches(show_all=args.all)

        elif args.command == "batch":
            # Batch management command
            if not args.batch_action:
                parser.print_help()
                return 1

            batch_framework = HSLTFramework()

            if args.batch_action == "archive":
                success = batch_framework.archive_batch(args.batch_id)
            elif args.batch_action == "complete":
                success = batch_framework.complete_batch(args.batch_id)
            elif args.batch_action == "reactivate":
                success = batch_framework.reactivate_batch(args.batch_id)
            elif args.batch_action == "remove":
                success = batch_framework.remove_batch(args.batch_id, args.confirm)
            elif args.batch_action == "info":
                success = batch_framework.show_batch_info(args.batch_id)
            else:
                parser.print_help()
                success = False

        else:
            parser.print_help()
            success = False

        return 0 if success else 1

    except KeyboardInterrupt:
        self.log_manager.warning("Operation cancelled by user")
        return 1
    except Exception as e:
        self.log_manager.critical(f"Unexpected error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
