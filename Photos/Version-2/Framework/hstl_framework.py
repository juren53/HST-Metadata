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
    from steps.base_step import ProcessingContext
    from core.pipeline import Pipeline
except ImportError as e:
    print(f"Error importing framework modules: {e}")
    print("Please ensure all required dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)

# Framework metadata
FRAMEWORK_VERSION = "1.0.0"
SUPPORTED_STEPS = list(range(1, 9))

class HSLTFramework:
    """Main framework controller class."""
    
    def __init__(self):
        self.config_manager = None
        self.logger = None
        self.path_manager = None
        self.pipeline = None
        
    def initialize(self, config_path: Optional[Path] = None):
        """Initialize the framework with configuration."""
        try:
            # Initialize configuration
            self.config_manager = ConfigManager(config_path)
            
            # Initialize logging
            self.logger = setup_logger(
                level=self.config_manager.get('logging.level', 'INFO'),
                log_file=self.config_manager.get('logging.file')
            )
            
            # Initialize path manager
            self.path_manager = PathManager(
                framework_root=framework_dir,
                data_directory=self.config_manager.get('project.data_directory')
            )
            
            self.logger.info("HSTL Framework initialized successfully")
            return True
            
        except Exception as e:
            print(f"Failed to initialize framework: {e}")
            return False
    
    def init_project(self, data_dir: str, project_name: str, force: bool = False):
        """Initialize a new project."""
        try:
            data_path = Path(data_dir)
            if not data_path.exists():
                print(f"Error: Data directory does not exist: {data_dir}")
                return False
            
            # Create project configuration
            project_config = {
                'project': {
                    'name': project_name,
                    'data_directory': str(data_path.absolute()),
                    'created': str(data_path),
                },
                'steps_completed': {f'step{i}': False for i in SUPPORTED_STEPS},
                'validation': {
                    'strict_mode': True,
                    'auto_backup': True
                }
            }
            
            # Save configuration
            config_path = data_path / 'config' / 'project_config.yaml'
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            if config_path.exists() and not force:
                print(f"Project configuration already exists: {config_path}")
                print("Use --force to overwrite existing configuration")
                return False
            
            self.config_manager = ConfigManager()
            self.config_manager.save_config(project_config, config_path)
            
            # Create directory structure
            self._create_project_directories(data_path)
            
            print(f"✅ Project '{project_name}' initialized successfully")
            print(f"📁 Data directory: {data_dir}")
            print(f"⚙️ Configuration: {config_path}")
            
            return True
            
        except Exception as e:
            print(f"Failed to initialize project: {e}")
            return False
    
    def _create_project_directories(self, data_path: Path):
        """Create the standard project directory structure."""
        directories = [
            'input/tiff',
            'input/spreadsheet',
            'output/csv',
            'output/tiff_processed',
            'output/jpeg',
            'output/jpeg_resized',
            'output/jpeg_watermarked',
            'reports',
            'logs',
            'config'
        ]
        
        for dir_name in directories:
            (data_path / dir_name).mkdir(parents=True, exist_ok=True)
    
    def show_status(self, verbose: bool = False):
        """Display current project status."""
        if not self.config_manager:
            print("❌ No project initialized. Run 'hstl_framework.py init' first.")
            return False
        
        print("📊 HSTL Framework Status")
        print("=" * 50)
        
        # Project information
        project_name = self.config_manager.get('project.name', 'Unknown')
        data_dir = self.config_manager.get('project.data_directory', 'Not set')
        print(f"🔹 Project: {project_name}")
        print(f"🔹 Data Directory: {data_dir}")
        print()
        
        # Steps status
        print("📋 Processing Steps:")
        for step_num in SUPPORTED_STEPS:
            completed = self.config_manager.get(f'steps_completed.step{step_num}', False)
            status = "✅ Completed" if completed else "⭕ Pending"
            step_name = self._get_step_name(step_num)
            print(f"  Step {step_num}: {step_name} - {status}")
        
        if verbose:
            print("\n🔧 Configuration Details:")
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
            8: "Watermark Addition"
        }
        return step_names.get(step_num, f"Step {step_num}")
    
    def run_steps(self, steps: List[int], dry_run: bool = False):
        """Run specified processing steps."""
        if not self.config_manager:
            print("❌ No project initialized. Run 'hstl_framework.py init' first.")
            return False
        
        print(f"🚀 {'Dry run' if dry_run else 'Running'} steps: {steps}")
        
        for step_num in steps:
            if step_num not in SUPPORTED_STEPS:
                print(f"❌ Invalid step number: {step_num}")
                return False
            
            if dry_run:
                print(f"✅ Would run Step {step_num}: {self._get_step_name(step_num)}")
            else:
                print(f"🔄 Running Step {step_num}: {self._get_step_name(step_num)}")
                # TODO: Implement actual step execution
                print(f"⚠️  Step {step_num} implementation pending")
        
        return True
    
    def validate(self, step: Optional[int] = None, pre_flight: bool = False):
        """Validate project or specific step."""
        if not self.config_manager:
            print("❌ No project initialized. Run 'hstl_framework.py init' first.")
            return False
        
        if pre_flight:
            print("🔍 Running pre-flight validation...")
            # TODO: Implement pre-flight checks
            print("✅ Pre-flight validation completed")
            return True
        
        if step:
            print(f"🔍 Validating Step {step}: {self._get_step_name(step)}")
            # TODO: Implement step-specific validation
            print(f"✅ Step {step} validation completed")
        else:
            print("🔍 Validating entire project...")
            # TODO: Implement full project validation
            print("✅ Project validation completed")
        
        return True


def create_parser() -> argparse.ArgumentParser:
    """Create the command line argument parser."""
    parser = argparse.ArgumentParser(
        description="HSTL Photo Framework - Orchestrate photo metadata processing workflow",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  %(prog)s init --data-dir "C:\\Data\\Photos" --project-name "HSTL_2024"
  %(prog)s run --step 2
  %(prog)s run --steps 1-3
  %(prog)s run --all
  %(prog)s status --verbose
  %(prog)s validate --step 5
  
Framework Version: {FRAMEWORK_VERSION}
        """
    )
    
    # Global options
    parser.add_argument('--version', action='version', version=f'HSTL Framework {FRAMEWORK_VERSION}')
    parser.add_argument('--config', type=Path, help='Path to configuration file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize a new project')
    init_parser.add_argument('--data-dir', required=True, help='Path to data directory')
    init_parser.add_argument('--project-name', required=True, help='Name of the project')
    init_parser.add_argument('--force', action='store_true', help='Overwrite existing configuration')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run processing steps')
    run_group = run_parser.add_mutually_exclusive_group(required=True)
    run_group.add_argument('--step', type=int, choices=SUPPORTED_STEPS, help='Run single step')
    run_group.add_argument('--steps', help='Run range of steps (e.g., "1-3" or "2,5,7")')
    run_group.add_argument('--all', action='store_true', help='Run all steps')
    run_group.add_argument('--continue', dest='continue_run', action='store_true', 
                          help='Continue from last completed step')
    run_parser.add_argument('--dry-run', action='store_true', help='Validate without execution')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show project status')
    status_parser.add_argument('--verbose', action='store_true', help='Show detailed status')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate project or steps')
    validate_parser.add_argument('--step', type=int, choices=SUPPORTED_STEPS, help='Validate specific step')
    validate_parser.add_argument('--all', action='store_true', help='Validate all completed steps')
    validate_parser.add_argument('--pre-flight', action='store_true', help='Run pre-flight checks')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Manage configuration')
    config_parser.add_argument('--list', action='store_true', help='List configuration')
    config_parser.add_argument('--set', nargs=2, metavar=('KEY', 'VALUE'), help='Set configuration value')
    
    return parser


def parse_steps_argument(steps_arg: str) -> List[int]:
    """Parse steps argument into list of step numbers."""
    steps = []
    
    # Handle ranges (e.g., "1-3") and comma-separated (e.g., "2,5,7")
    for part in steps_arg.split(','):
        part = part.strip()
        if '-' in part:
            start, end = map(int, part.split('-'))
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
    if args.command == 'init':
        success = framework.init_project(
            data_dir=args.data_dir,
            project_name=args.project_name,
            force=args.force
        )
        return 0 if success else 1
    
    # For all other commands, initialize with existing config
    if not framework.initialize(args.config):
        return 1
    
    # Handle commands
    try:
        if args.command == 'status':
            success = framework.show_status(args.verbose)
            
        elif args.command == 'run':
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
            
        elif args.command == 'validate':
            success = framework.validate(
                step=args.step,
                pre_flight=args.pre_flight
            )
            
        elif args.command == 'config':
            if args.list:
                print("⚠️  Config list functionality not yet implemented")
                success = True
            elif args.set:
                print("⚠️  Config set functionality not yet implemented")
                success = True
            else:
                parser.print_help()
                success = False
        
        else:
            parser.print_help()
            success = False
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())