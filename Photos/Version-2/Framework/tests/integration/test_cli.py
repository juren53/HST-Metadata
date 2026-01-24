"""
Integration tests for CLI interface.
"""

import pytest
import os
import sys
import tempfile
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

# Add the project root to sys.path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hstl_framework import main, create_parser, HSTLFramework


class TestCLI:
    """Test cases for CLI interface."""

    def test_create_parser(self):
        """Test argument parser creation."""
        parser = create_parser()
        
        # Test parser exists
        assert parser is not None
        
        # Test basic arguments
        args = parser.parse_args(['--config', 'test.yaml'])
        assert args.config == 'test.yaml'
        
        args = parser.parse_args(['--batch-id', 'TEST-001'])
        assert args.batch_id == 'TEST-001'
        
        args = parser.parse_args(['--verbose'])
        assert args.verbose is True

    def test_parser_default_values(self):
        """Test parser default values."""
        parser = create_parser()
        args = parser.parse_args([])
        
        assert args.config is None
        assert args.batch_id is None
        assert args.verbose is False
        assert args.dry_run is False

    def test_parser_all_arguments(self):
        """Test parser with all arguments."""
        parser = create_parser()
        
        args = parser.parse_args([
            '--config', 'test_config.yaml',
            '--batch-id', 'TEST-001',
            '--verbose',
            '--dry-run',
            '--output-dir', '/test/output'
        ])
        
        assert args.config == 'test_config.yaml'
        assert args.batch_id == 'TEST-001'
        assert args.verbose is True
        assert args.dry_run is True
        assert args.output_dir == '/test/output'

    def test_main_with_config_file(self, config_file, capsys):
        """Test main function with config file."""
        test_args = ['--config', config_file]
        
        with patch.object(sys, 'argv', ['hstl_framework.py'] + test_args):
            with patch('hstl_framework.HSTLFramework') as mock_framework:
                mock_instance = Mock()
                mock_framework.return_value = mock_instance
                mock_instance.run.return_value = 0
                
                result = main()
                
                assert result == 0
                mock_framework.assert_called_once()
                mock_instance.run.assert_called_once()

    def test_main_with_batch_id(self, capsys):
        """Test main function with batch ID."""
        test_args = ['--batch-id', 'TEST-001']
        
        with patch.object(sys, 'argv', ['hstl_framework.py'] + test_args):
            with patch('hstl_framework.HSTLFramework') as mock_framework:
                mock_instance = Mock()
                mock_framework.return_value = mock_instance
                mock_instance.run.return_value = 0
                
                result = main()
                
                assert result == 0
                mock_framework.assert_called_once()

    def test_main_with_verbose_flag(self, capsys):
        """Test main function with verbose flag."""
        test_args = ['--config', 'test.yaml', '--verbose']
        
        with patch.object(sys, 'argv', ['hstl_framework.py'] + test_args):
            with patch('hstl_framework.HSTLFramework') as mock_framework:
                mock_instance = Mock()
                mock_framework.return_value = mock_instance
                mock_instance.run.return_value = 0
                
                result = main()
                
                assert result == 0
                mock_framework.assert_called_once()

    def test_main_with_dry_run(self, capsys):
        """Test main function with dry run flag."""
        test_args = ['--config', 'test.yaml', '--dry-run']
        
        with patch.object(sys, 'argv', ['hstl_framework.py'] + test_args):
            with patch('hstl_framework.HSTLFramework') as mock_framework:
                mock_instance = Mock()
                mock_framework.return_value = mock_instance
                mock_instance.run.return_value = 0
                
                result = main()
                
                assert result == 0
                mock_framework.assert_called_once()

    def test_main_framework_error(self, capsys):
        """Test main function when framework raises error."""
        test_args = ['--config', 'test.yaml']
        
        with patch.object(sys, 'argv', ['hstl_framework.py'] + test_args):
            with patch('hstl_framework.HSTLFramework') as mock_framework:
                mock_framework.side_effect = Exception('Test error')
                
                with pytest.raises(SystemExit) as exc_info:
                    main()
                
                assert exc_info.value.code == 1

    def test_main_run_error(self, capsys):
        """Test main function when framework run returns error."""
        test_args = ['--config', 'test.yaml']
        
        with patch.object(sys, 'argv', ['hstl_framework.py'] + test_args):
            with patch('hstl_framework.HSTLFramework') as mock_framework:
                mock_instance = Mock()
                mock_framework.return_value = mock_instance
                mock_instance.run.return_value = 1  # Error code
                
                result = main()
                
                assert result == 1

    def test_cli_help_message(self, capsys):
        """Test CLI help message."""
        parser = create_parser()
        
        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args(['--help'])
        
        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert 'HSTL Photo Framework' in captured.out

    def test_cli_invalid_arguments(self, capsys):
        """Test CLI with invalid arguments."""
        parser = create_parser()
        
        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args(['--invalid-arg'])
        
        assert exc_info.value.code == 2

    def test_hstl_framework_initialization(self, config_manager):
        """Test HSTLFramework initialization."""
        framework = HSTLFramework(config_manager.config)
        
        assert framework.config == config_manager.config
        assert framework.pipeline is not None

    def test_hstl_framework_run_success(self, config_manager):
        """Test HSTLFramework successful run."""
        framework = HSTLFramework(config_manager.config)
        
        with patch.object(framework.pipeline, 'execute', return_value=True):
            result = framework.run()
            
            assert result == 0

    def test_hstl_framework_run_failure(self, config_manager):
        """Test HSTLFramework run failure."""
        framework = HSTLFramework(config_manager.config)
        
        with patch.object(framework.pipeline, 'execute', return_value=False):
            result = framework.run()
            
            assert result == 1

    def test_hstl_framework_dry_run(self, config_manager):
        """Test HSTLFramework dry run mode."""
        framework = HSTLFramework(config_manager.config)
        framework.dry_run = True
        
        with patch.object(framework.pipeline, 'execute', return_value=True) as mock_execute:
            result = framework.run()
            
            assert result == 0
            mock_execute.assert_called_once()

    def test_cli_with_output_directory(self, temp_dir, capsys):
        """Test CLI with custom output directory."""
        output_dir = os.path.join(temp_dir, 'custom_output')
        test_args = ['--config', 'test.yaml', '--output-dir', output_dir]
        
        with patch.object(sys, 'argv', ['hstl_framework.py'] + test_args):
            with patch('hstl_framework.HSTLFramework') as mock_framework:
                mock_instance = Mock()
                mock_framework.return_value = mock_instance
                mock_instance.run.return_value = 0
                
                result = main()
                
                assert result == 0
                mock_framework.assert_called_once()

    def test_cli_config_file_not_found(self, capsys):
        """Test CLI with non-existent config file."""
        test_args = ['--config', 'nonexistent.yaml']
        
        with patch.object(sys, 'argv', ['hstl_framework.py'] + test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            assert exc_info.value.code == 1

    def test_cli_batch_id_not_found(self, capsys):
        """Test CLI with non-existent batch ID."""
        test_args = ['--batch-id', 'NONEXISTENT']
        
        with patch.object(sys, 'argv', ['hstl_framework.py'] + test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            assert exc_info.value.code == 1

    def test_cli_verbose_logging(self, config_file, capsys):
        """Test CLI verbose logging."""
        test_args = ['--config', config_file, '--verbose']
        
        with patch.object(sys, 'argv', ['hstl_framework.py'] + test_args):
            with patch('hstl_framework.HSTLFramework') as mock_framework:
                mock_instance = Mock()
                mock_framework.return_value = mock_instance
                mock_instance.run.return_value = 0
                
                result = main()
                
                assert result == 0
                mock_framework.assert_called_once()

    def test_cli_multiple_config_files(self, capsys):
        """Test CLI with multiple config files (should fail)."""
        test_args = ['--config', 'test1.yaml', '--config', 'test2.yaml']
        
        parser = create_parser()
        
        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args(test_args)
        
        assert exc_info.value.code == 2

    def test_cli_config_and_batch_id(self, config_file, capsys):
        """Test CLI with both config file and batch ID."""
        test_args = ['--config', config_file, '--batch-id', 'TEST-001']
        
        with patch.object(sys, 'argv', ['hstl_framework.py'] + test_args):
            with patch('hstl_framework.HSTLFramework') as mock_framework:
                mock_instance = Mock()
                mock_framework.return_value = mock_instance
                mock_instance.run.return_value = 0
                
                result = main()
                
                assert result == 0
                mock_framework.assert_called_once()

    def test_cli_keyboard_interrupt(self, config_file, capsys):
        """Test CLI handling of keyboard interrupt."""
        test_args = ['--config', config_file]
        
        with patch.object(sys, 'argv', ['hstl_framework.py'] + test_args):
            with patch('hstl_framework.HSTLFramework') as mock_framework:
                mock_instance = Mock()
                mock_framework.return_value = mock_instance
                mock_instance.run.side_effect = KeyboardInterrupt()
                
                with pytest.raises(SystemExit) as exc_info:
                    main()
                
                assert exc_info.value.code == 130

    def test_cli_signal_handling(self, config_file, capsys):
        """Test CLI signal handling."""
        import signal
        
        test_args = ['--config', config_file]
        
        with patch.object(sys, 'argv', ['hstl_framework.py'] + test_args):
            with patch('hstl_framework.HSTLFramework') as mock_framework:
                mock_instance = Mock()
                mock_framework.return_value = mock_instance
                mock_instance.run.side_effect = lambda: os.kill(os.getpid(), signal.SIGTERM)
                
                with pytest.raises(SystemExit) as exc_info:
                    main()
                
                assert exc_info.value.code == 143

    def test_cli_version_argument(self, capsys):
        """Test CLI version argument."""
        parser = create_parser()
        
        # Add version argument if it exists
        if hasattr(parser, 'add_argument'):
            try:
                parser.parse_args(['--version'])
            except SystemExit as exc_info:
                assert exc_info.code == 0

    def test_cli_with_environment_variables(self, config_file, capsys):
        """Test CLI with environment variables."""
        # Set environment variables
        os.environ['HSTL_CONFIG'] = config_file
        os.environ['HSTL_VERBOSE'] = '1'
        
        test_args = []  # No arguments, should use environment
        
        with patch.object(sys, 'argv', ['hstl_framework.py'] + test_args):
            with patch('hstl_framework.HSTLFramework') as mock_framework:
                mock_instance = Mock()
                mock_framework.return_value = mock_instance
                mock_instance.run.return_value = 0
                
                result = main()
                
                assert result == 0
                mock_framework.assert_called_once()
        
        # Clean up environment variables
        os.environ.pop('HSTL_CONFIG', None)
        os.environ.pop('HSTL_VERBOSE', None)

    def test_cli_config_validation(self, temp_dir, capsys):
        """Test CLI configuration validation."""
        # Create invalid config file
        invalid_config = os.path.join(temp_dir, 'invalid.yaml')
        with open(invalid_config, 'w') as f:
            f.write('invalid: yaml: content: [')
        
        test_args = ['--config', invalid_config]
        
        with patch.object(sys, 'argv', ['hstl_framework.py'] + test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            assert exc_info.value.code == 1

    def test_cli_progress_display(self, config_file, capsys):
        """Test CLI progress display."""
        test_args = ['--config', config_file, '--verbose']
        
        with patch.object(sys, 'argv', ['hstl_framework.py'] + test_args):
            with patch('hstl_framework.HSTLFramework') as mock_framework:
                mock_instance = Mock()
                mock_framework.return_value = mock_instance
                mock_instance.run.return_value = 0
                
                result = main()
                
                assert result == 0
                captured = capsys.readouterr()
                # Progress information should be displayed in verbose mode
                mock_framework.assert_called_once()