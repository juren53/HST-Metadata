# HSTL Photo Framework Regression Test Suite

This directory contains a comprehensive regression test suite for the HSTL Photo Metatagging Project. The test suite is designed to ensure the framework continues to work correctly as new features are added and existing code is modified.

## Test Structure

```
tests/
├── conftest.py                    # Pytest configuration and fixtures
├── unit/                          # Unit tests for individual components
│   ├── test_config_manager.py      # Configuration management tests
│   ├── test_batch_registry.py     # Batch registry tests
│   ├── test_validator.py          # Validation utility tests
│   ├── test_path_manager.py       # Path management tests
│   └── test_base_step.py         # Base step processor tests
├── integration/                   # Integration tests for component interactions
│   ├── test_pipeline.py          # Pipeline orchestration tests
│   ├── test_cli.py               # CLI interface tests
│   └── test_end_to_end.py       # End-to-end regression tests
└── fixtures/                      # Test data and configurations
    ├── sample_configs/            # Sample configuration files
    └── test_data/               # Sample test data
```

## Test Categories

### Unit Tests
- **ConfigManager**: Tests configuration loading, validation, and dot notation access
- **BatchRegistry**: Tests batch registration, status tracking, and persistence
- **Validator**: Tests file validation, path validation, and data format validation
- **PathManager**: Tests directory creation, file operations, and path resolution
- **BaseStep**: Tests step processor base class functionality

### Integration Tests
- **Pipeline**: Tests step orchestration, error handling, and state management
- **CLI**: Tests command-line interface, argument parsing, and error handling
- **End-to-End**: Tests complete workflows, data integrity, and performance

## Running Tests

### Quick Start

```bash
# Run all tests
python run_tests.py

# Run with coverage report
python run_tests.py --coverage

# Run only unit tests
python run_tests.py --category unit

# Run only integration tests
python run_tests.py --category integration

# Run with verbose output
python run_tests.py --verbose

# Run tests in parallel
python run_tests.py --parallel
```

### Using Pytest Directly

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/unit/test_config_manager.py

# Run specific test class
pytest tests/unit/test_config_manager.py::TestConfigManager

# Run specific test method
pytest tests/unit/test_config_manager.py::TestConfigManager::test_load_valid_config

# Run with markers
pytest -m unit          # Run only unit tests
pytest -m integration   # Run only integration tests
pytest -m regression     # Run only regression tests
```

### Test Runner Options

```bash
# List all available tests
python run_tests.py --list

# Clean test results
python run_tests.py --clean

# Generate HTML report
python run_tests.py --coverage --html

# Run tests without coverage
python run_tests.py --no-coverage

# Disable HTML report
python run_tests.py --no-html
```

## Test Configuration

### Pytest Configuration (pytest.ini)

The test suite is configured via `pytest.ini` with the following settings:

- **Test paths**: `tests/`
- **Test patterns**: `test_*.py`, `Test*`, `test_*`
- **Coverage**: HTML and terminal reports, 80% minimum coverage
- **Markers**: `unit`, `integration`, `regression`, `slow`, `network`

### Environment Variables

- `HSTL_TEST_MODE`: Set to '1' to enable test mode
- `HSTL_TEMP_DIR`: Override temporary directory for tests

## Test Fixtures

The test suite provides comprehensive fixtures in `conftest.py`:

### Core Fixtures
- `temp_dir`: Temporary directory for each test
- `sample_config`: Sample configuration data
- `config_file`: Sample configuration file
- `config_manager`: ConfigManager instance with sample config
- `batch_registry_file`: Sample batch registry file
- `batch_registry`: BatchRegistry instance with sample data

### Data Fixtures
- `sample_project_structure`: Complete project directory structure
- `sample_csv_data`: Sample CSV metadata
- `sample_tiff_file`: Sample TIFF image file
- `generate_test_files`: Helper to generate test files
- `cleanup_test_files`: Helper to clean up test files

### Mock Fixtures
- `mock_external_tools`: Mock external tool dependencies
- `mock_environment`: Mock environment variables and paths

## Writing New Tests

### Unit Test Template

```python
import pytest
from your_module import YourClass

class TestYourClass:
    def test_method_success(self, fixture):
        """Test successful method execution."""
        obj = YourClass(fixture)
        result = obj.method()
        assert result is True
    
    def test_method_failure(self, fixture):
        """Test method failure handling."""
        obj = YourClass(fixture)
        with pytest.raises(ExpectedException):
            obj.method_that_fails()
```

### Integration Test Template

```python
import pytest
from unittest.mock import Mock, patch

class TestIntegration:
    def test_component_interaction(self, config_manager):
        """Test interaction between components."""
        with patch('external_dependency') as mock_dep:
            mock_dep.return_value = Mock()
            
            # Test integration
            result = your_integration_function(config_manager)
            
            assert result is expected_value
            mock_dep.assert_called_once()
```

### End-to-End Test Template

```python
import pytest
import os
import yaml

class TestEndToEnd:
    def test_complete_workflow(self, temp_dir):
        """Test complete workflow from start to finish."""
        # Setup
        project_dir = os.path.join(temp_dir, 'test_project')
        config_data = {...}
        
        # Execute
        result = run_complete_workflow(project_dir, config_data)
        
        # Verify
        assert result is True
        assert os.path.exists(os.path.join(project_dir, 'output'))
```

## Test Coverage

The test suite aims for comprehensive coverage:

- **Unit Tests**: 90%+ coverage of core components
- **Integration Tests**: 80%+ coverage of component interactions
- **End-to-End Tests**: Coverage of critical user workflows

### Coverage Reports

- **Terminal**: Summary displayed after test run
- **HTML**: Detailed report in `htmlcov/` directory
- **XML**: Machine-readable report for CI/CD

## Continuous Integration

### GitHub Actions

The test suite is designed to run in CI/CD environments:

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-html
      - name: Run tests
        run: python run_tests.py --coverage
      - name: Upload coverage
        uses: codecov/codecov-action@v1
```

### Test Reports

- **JUnit XML**: `test_results/junit.xml`
- **HTML Report**: `test_results/report.html`
- **Coverage HTML**: `htmlcov/index.html`
- **Summary**: `test_results/summary.txt`

## Performance Testing

The test suite includes performance regression tests:

- **Configuration Loading**: Should complete in < 1 second
- **Batch Registration**: Should handle 1000+ batches efficiently
- **Pipeline Execution**: Should complete within expected timeframes

### Running Performance Tests

```bash
# Run performance-specific tests
pytest -m performance

# Run with timing information
pytest --durations=10
```

## Debugging Tests

### Running Tests in Debug Mode

```bash
# Run with Python debugger
pytest --pdb

# Stop on first failure
pytest -x

# Run with verbose output
pytest -v -s

# Show local variables on failure
pytest --tb=long
```

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Path Issues**: Check that working directory is correct
3. **Permission Errors**: Ensure test directories are writable
4. **External Dependencies**: Mock external tools/services

## Best Practices

### Test Organization
- Group related tests in classes
- Use descriptive test names
- Follow Arrange-Act-Assert pattern
- Test both success and failure scenarios

### Test Data
- Use fixtures for reusable test data
- Clean up temporary files after tests
- Use realistic data for integration tests
- Mock external dependencies

### Assertions
- Use specific assertions for clarity
- Include helpful error messages
- Test edge cases and boundary conditions
- Verify both positive and negative cases

## Contributing

When adding new features:

1. **Write tests first** (TDD approach)
2. **Ensure all tests pass** before submitting
3. **Maintain coverage levels** (80%+ minimum)
4. **Add integration tests** for new components
5. **Update documentation** for new test cases

### Test Review Checklist

- [ ] Tests cover all new code paths
- [ ] Tests handle error conditions
- [ ] Tests are independent and isolated
- [ ] Test data is appropriate and realistic
- [ ] Assertions are specific and meaningful
- [ ] Test names are descriptive
- [ ] Documentation is updated

## Troubleshooting

### Common Test Failures

1. **Configuration Loading Errors**
   - Check YAML syntax
   - Verify file paths
   - Ensure required fields are present

2. **File System Errors**
   - Check permissions
   - Verify directory structure
   - Clean up temporary files

3. **Import Errors**
   - Install missing dependencies
   - Check Python path
   - Verify module structure

4. **Timeout Errors**
   - Increase timeout values
   - Check for infinite loops
   - Optimize test performance

### Getting Help

- Check test logs in `test_results/`
- Run tests with `--verbose` flag
- Use `--pdb` to debug failures
- Review pytest documentation

## Test Metrics

The test suite tracks:

- **Code Coverage**: Percentage of code tested
- **Test Count**: Number of tests in each category
- **Execution Time**: Time to run test suite
- **Pass Rate**: Percentage of tests passing
- **Flaky Tests**: Tests with inconsistent results

These metrics help maintain code quality and identify areas for improvement.