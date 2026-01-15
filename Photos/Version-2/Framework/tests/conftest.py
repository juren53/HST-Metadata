"""
Shared test fixtures for HSTL Photo Framework.

This module provides common fixtures used across all test modules.
"""

import pytest
import tempfile
import shutil
import sys
from pathlib import Path
from typing import Generator, Dict, Any

# Add Framework directory to path for imports
FRAMEWORK_DIR = Path(__file__).parent.parent
if str(FRAMEWORK_DIR) not in sys.path:
    sys.path.insert(0, str(FRAMEWORK_DIR))


# ============================================================================
# DIRECTORY FIXTURES
# ============================================================================

@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """
    Create a temporary directory for tests.

    Yields:
        Path to temporary directory

    Note:
        Directory is automatically cleaned up after test.
    """
    tmp = tempfile.mkdtemp(prefix="hpm_test_")
    yield Path(tmp)
    shutil.rmtree(tmp, ignore_errors=True)


@pytest.fixture
def sample_batch_dir(temp_dir: Path) -> Path:
    """
    Create a sample batch directory structure.

    Creates the standard HPM batch directory layout:
    - input/
    - output/
    - logs/
    - config/

    Args:
        temp_dir: Parent temporary directory

    Returns:
        Path to batch directory
    """
    batch_dir = temp_dir / "test_batch"

    # Create standard subdirectories
    (batch_dir / "input").mkdir(parents=True)
    (batch_dir / "output").mkdir(parents=True)
    (batch_dir / "logs").mkdir(parents=True)
    (batch_dir / "config").mkdir(parents=True)

    # Create step-specific output directories
    for step in range(1, 9):
        (batch_dir / "output" / f"step{step}").mkdir(parents=True)

    return batch_dir


@pytest.fixture
def sample_data_dir(temp_dir: Path) -> Path:
    """
    Create a sample data directory with framework structure.

    Args:
        temp_dir: Parent temporary directory

    Returns:
        Path to data directory
    """
    data_dir = temp_dir / "hpm_data"
    data_dir.mkdir(parents=True)

    # Create batches directory
    (data_dir / "batches").mkdir()

    # Create logs directory
    (data_dir / "logs").mkdir()

    return data_dir


# ============================================================================
# CONFIGURATION FIXTURES
# ============================================================================

@pytest.fixture
def sample_config_dict() -> Dict[str, Any]:
    """
    Create a sample configuration dictionary.

    Returns:
        Dictionary with sample configuration values
    """
    return {
        "project": {
            "name": "test_project",
            "description": "Test project for unit tests",
            "data_directory": "/tmp/hpm_test_data",
        },
        "metadata": {
            "framework_version": "0.1.5c",
            "created": "2026-01-15T00:00:00",
            "modified": "2026-01-15T00:00:00",
        },
        "step_status": {
            "step1": {"completed": False},
            "step2": {"completed": False},
            "step3": {"completed": False},
            "step4": {"completed": False},
            "step5": {"completed": False},
            "step6": {"completed": False},
            "step7": {"completed": False},
            "step8": {"completed": False},
        },
        "step_configurations": {
            "step1": {"enabled": True},
            "step2": {"enabled": True},
            "step3": {"enabled": True},
            "step4": {"enabled": True},
            "step5": {"enabled": True},
            "step6": {"enabled": True},
            "step7": {"enabled": True},
            "step8": {"enabled": True},
        },
    }


@pytest.fixture
def sample_config_file(temp_dir: Path, sample_config_dict: Dict[str, Any]) -> Path:
    """
    Create a sample YAML configuration file.

    Args:
        temp_dir: Temporary directory
        sample_config_dict: Configuration dictionary

    Returns:
        Path to configuration file
    """
    import yaml

    config_path = temp_dir / "config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(sample_config_dict, f, default_flow_style=False)

    return config_path


@pytest.fixture
def empty_config_file(temp_dir: Path) -> Path:
    """
    Create an empty configuration file.

    Args:
        temp_dir: Temporary directory

    Returns:
        Path to empty configuration file
    """
    config_path = temp_dir / "empty_config.yaml"
    config_path.write_text("")
    return config_path


@pytest.fixture
def invalid_yaml_file(temp_dir: Path) -> Path:
    """
    Create a file with invalid YAML content.

    Args:
        temp_dir: Temporary directory

    Returns:
        Path to invalid YAML file
    """
    config_path = temp_dir / "invalid.yaml"
    config_path.write_text("invalid: yaml: content: [unclosed")
    return config_path


# ============================================================================
# BATCH REGISTRY FIXTURES
# ============================================================================

@pytest.fixture
def sample_registry_dict() -> Dict[str, Any]:
    """
    Create a sample batch registry dictionary.

    Returns:
        Dictionary with sample registry data
    """
    return {
        "batches": {
            "batch_001": {
                "name": "Test Batch 1",
                "status": "active",
                "created": "2026-01-15",
                "modified": "2026-01-15",
                "steps_completed": [1, 2],
                "data_directory": "/tmp/batch_001",
            },
            "batch_002": {
                "name": "Test Batch 2",
                "status": "completed",
                "created": "2026-01-10",
                "modified": "2026-01-14",
                "steps_completed": [1, 2, 3, 4, 5, 6, 7, 8],
                "data_directory": "/tmp/batch_002",
            },
            "batch_003": {
                "name": "Test Batch 3",
                "status": "archived",
                "created": "2026-01-01",
                "modified": "2026-01-05",
                "steps_completed": [1, 2, 3, 4, 5, 6, 7, 8],
                "data_directory": "/tmp/batch_003",
            },
        }
    }


@pytest.fixture
def sample_registry_file(temp_dir: Path, sample_registry_dict: Dict[str, Any]) -> Path:
    """
    Create a sample batch registry YAML file.

    Args:
        temp_dir: Temporary directory
        sample_registry_dict: Registry dictionary

    Returns:
        Path to registry file
    """
    import yaml

    registry_path = temp_dir / "batch_registry.yaml"
    with open(registry_path, "w") as f:
        yaml.dump(sample_registry_dict, f, default_flow_style=False)

    return registry_path


# ============================================================================
# SAMPLE DATA FIXTURES
# ============================================================================

@pytest.fixture
def sample_csv_content() -> str:
    """
    Create sample CSV content for testing.

    Returns:
        CSV content as string
    """
    return """filename,title,description,date,photographer
IMG_001.tif,Historic Building,A historic building in downtown,2025-01-15,John Doe
IMG_002.tif,City Park,Beautiful park scene,2025-01-16,Jane Smith
IMG_003.tif,Old Church,19th century church,2025-01-17,Bob Wilson
"""


@pytest.fixture
def sample_csv_file(temp_dir: Path, sample_csv_content: str) -> Path:
    """
    Create a sample CSV file.

    Args:
        temp_dir: Temporary directory
        sample_csv_content: CSV content

    Returns:
        Path to CSV file
    """
    csv_path = temp_dir / "metadata.csv"
    csv_path.write_text(sample_csv_content, encoding="utf-8")
    return csv_path


@pytest.fixture
def sample_image_file(temp_dir: Path) -> Path:
    """
    Create a minimal sample image file for testing.

    Creates a small 10x10 pixel RGB image.

    Args:
        temp_dir: Temporary directory

    Returns:
        Path to image file
    """
    try:
        from PIL import Image

        img_path = temp_dir / "sample.tif"
        img = Image.new("RGB", (10, 10), color="red")
        img.save(img_path)
        return img_path
    except ImportError:
        pytest.skip("Pillow not installed")


# ============================================================================
# MOCK FIXTURES
# ============================================================================

@pytest.fixture
def mock_logger(mocker):
    """
    Create a mock logger.

    Args:
        mocker: pytest-mock fixture

    Returns:
        Mock logger object
    """
    return mocker.MagicMock()


@pytest.fixture
def mock_exiftool(mocker):
    """
    Create a mock ExifTool instance.

    Args:
        mocker: pytest-mock fixture

    Returns:
        Mock ExifTool object
    """
    mock = mocker.MagicMock()
    mock.execute.return_value = b""
    return mock


# ============================================================================
# SKIP MARKERS
# ============================================================================

@pytest.fixture
def requires_exiftool():
    """
    Skip test if ExifTool is not installed.
    """
    import shutil
    if not shutil.which("exiftool"):
        pytest.skip("ExifTool not installed")


@pytest.fixture
def requires_pyqt6():
    """
    Skip test if PyQt6 is not installed.
    """
    try:
        import PyQt6
    except ImportError:
        pytest.skip("PyQt6 not installed")


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def create_batch_structure(base_dir: Path, batch_name: str) -> Path:
    """
    Create a complete batch directory structure.

    Args:
        base_dir: Base directory
        batch_name: Name of the batch

    Returns:
        Path to batch directory
    """
    batch_dir = base_dir / batch_name

    directories = [
        "input",
        "output",
        "logs",
        "config",
    ]

    for d in directories:
        (batch_dir / d).mkdir(parents=True, exist_ok=True)

    return batch_dir
