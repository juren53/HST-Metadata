"""
Integration tests for the HPM Delivery workflow.

Tests end-to-end file operations on real temporary directories.
No mocking — all file I/O is real. This is the highest-value layer
for the delivery feature because the work is fundamentally filesystem
operations and real tests catch failures that mocked tests miss.
"""

import shutil
import yaml
import pytest
from pathlib import Path

from core.delivery_service import DeliveryService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run_delivery(data_dir: Path) -> tuple:
    """Create a DeliveryService and run create_package. Returns (success, svc)."""
    svc = DeliveryService(data_dir)
    success, _ = svc.create_package()
    return success, svc


# ---------------------------------------------------------------------------
# Full delivery package creation
# ---------------------------------------------------------------------------

class TestDeliveryPackageCreation:
    """End-to-end delivery package creation on real filesystem."""

    @pytest.mark.integration
    def test_full_delivery_creates_expected_directory_structure(self, completed_batch):
        """create_package produces delivery/ and trash/ with all required subdirs."""
        data_dir = completed_batch["data_dir"]
        success, _ = run_delivery(data_dir)

        assert success is True
        assert (data_dir / "delivery" / "tiff_delivery").exists()
        assert (data_dir / "delivery" / "jpeg_delivery").exists()
        assert (data_dir / "trash" / "jpeg_converted").exists()
        assert (data_dir / "trash" / "jpeg_resized").exists()

    @pytest.mark.integration
    def test_delivery_blocked_on_incomplete_batch(self, temp_dir):
        """create_package is blocked when not all 8 steps are complete."""
        data_dir = temp_dir / "incomplete_batch"
        (data_dir / "config").mkdir(parents=True)
        (data_dir / "output" / "tiff_processed").mkdir(parents=True)
        (data_dir / "output" / "jpeg_watermarked").mkdir(parents=True)
        (data_dir / "output" / "tiff_processed" / "IMG_001.tif").write_bytes(b"x")
        (data_dir / "output" / "jpeg_watermarked" / "IMG_001.jpg").write_bytes(b"x")

        config_path = data_dir / "config" / "project_config.yaml"
        with open(config_path, "w") as f:
            yaml.dump(
                {"steps_completed": {f"step{i}": (i < 6) for i in range(1, 9)}}, f
            )

        svc = DeliveryService(data_dir)
        valid, reason = svc.validate()

        assert valid is False
        assert not (data_dir / "delivery").exists(), \
            "delivery/ should not be created for an incomplete batch"

    @pytest.mark.integration
    def test_delivery_tiff_count_matches_source(self, completed_batch):
        """delivery/tiff_delivery file count equals tiff_processed file count."""
        data_dir = completed_batch["data_dir"]
        source_count = len(list((data_dir / "output" / "tiff_processed").iterdir()))

        run_delivery(data_dir)

        delivered_count = len(list((data_dir / "delivery" / "tiff_delivery").iterdir()))
        assert delivered_count == source_count

    @pytest.mark.integration
    def test_delivery_jpeg_count_matches_source(self, completed_batch):
        """delivery/jpeg_delivery file count equals jpeg_watermarked file count."""
        data_dir = completed_batch["data_dir"]
        source_count = len(list((data_dir / "output" / "jpeg_watermarked").iterdir()))

        run_delivery(data_dir)

        delivered_count = len(list((data_dir / "delivery" / "jpeg_delivery").iterdir()))
        assert delivered_count == source_count

    @pytest.mark.integration
    def test_delivered_tiff_filenames_match_source(self, completed_batch):
        """Filenames in delivery/tiff_delivery match the source files exactly."""
        data_dir = completed_batch["data_dir"]
        source_names = {f.name for f in (data_dir / "output" / "tiff_processed").iterdir()}

        run_delivery(data_dir)

        delivered_names = {f.name for f in (data_dir / "delivery" / "tiff_delivery").iterdir()}
        assert delivered_names == source_names

    @pytest.mark.integration
    def test_delivered_jpeg_filenames_match_source(self, completed_batch):
        """Filenames in delivery/jpeg_delivery match the source files exactly."""
        data_dir = completed_batch["data_dir"]
        source_names = {f.name for f in (data_dir / "output" / "jpeg_watermarked").iterdir()}

        run_delivery(data_dir)

        delivered_names = {f.name for f in (data_dir / "delivery" / "jpeg_delivery").iterdir()}
        assert delivered_names == source_names

    @pytest.mark.integration
    def test_intermediate_jpegs_absent_from_output_after_delivery(self, completed_batch):
        """output/jpeg and output/jpeg_resized are empty of files after delivery."""
        data_dir = completed_batch["data_dir"]
        run_delivery(data_dir)

        jpeg_files = [f for f in (data_dir / "output" / "jpeg").iterdir() if f.is_file()]
        resized_files = [f for f in (data_dir / "output" / "jpeg_resized").iterdir() if f.is_file()]

        assert jpeg_files == [], "output/jpeg should be empty after delivery"
        assert resized_files == [], "output/jpeg_resized should be empty after delivery"

    @pytest.mark.integration
    def test_intermediate_jpegs_present_in_trash_after_delivery(self, completed_batch):
        """Files that were in output/jpeg appear in trash/jpeg_converted after delivery."""
        data_dir = completed_batch["data_dir"]
        original_jpeg_names = {f.name for f in (data_dir / "output" / "jpeg").iterdir()}

        run_delivery(data_dir)

        trash_names = {f.name for f in (data_dir / "trash" / "jpeg_converted").iterdir()}
        assert trash_names == original_jpeg_names

    @pytest.mark.integration
    def test_retained_artifacts_untouched(self, completed_batch):
        """Excel file, CSV export, logs, and reports remain in original locations."""
        data_dir = completed_batch["data_dir"]
        run_delivery(data_dir)

        assert (data_dir / "input" / "spreadsheet" / "source.xlsx").exists()
        assert (data_dir / "output" / "csv" / "export.csv").exists()
        assert (data_dir / "config" / "project_config.yaml").exists()

    @pytest.mark.integration
    def test_source_tiffs_retained_after_delivery(self, completed_batch):
        """output/tiff_processed is unchanged after delivery (copy, not move)."""
        data_dir = completed_batch["data_dir"]
        source_names_before = {f.name for f in (data_dir / "output" / "tiff_processed").iterdir()}

        run_delivery(data_dir)

        source_names_after = {f.name for f in (data_dir / "output" / "tiff_processed").iterdir()}
        assert source_names_after == source_names_before

    @pytest.mark.integration
    def test_idempotent_with_second_run(self, completed_batch):
        """Running create_package a second time succeeds and delivery is intact."""
        data_dir = completed_batch["data_dir"]
        run_delivery(data_dir)

        # Second run — delivery dir already exists
        success, _ = DeliveryService(data_dir).create_package()
        assert success is True
        assert (data_dir / "delivery" / "tiff_delivery").exists()
        assert (data_dir / "delivery" / "jpeg_delivery").exists()

    @pytest.mark.integration
    def test_delivery_with_multiple_tiff_files(self, temp_dir):
        """Delivery handles batches with many TIFF files correctly."""
        data_dir = temp_dir / "multi_tiff_batch"
        (data_dir / "output" / "tiff_processed").mkdir(parents=True)
        (data_dir / "output" / "jpeg_watermarked").mkdir(parents=True)
        (data_dir / "output" / "jpeg").mkdir(parents=True)
        (data_dir / "output" / "jpeg_resized").mkdir(parents=True)
        (data_dir / "config").mkdir(parents=True)

        # Create 10 dummy TIFF files
        for i in range(1, 11):
            (data_dir / "output" / "tiff_processed" / f"IMG_{i:03d}.tif").write_bytes(
                b"fake tiff content"
            )
            (data_dir / "output" / "jpeg_watermarked" / f"IMG_{i:03d}.jpg").write_bytes(
                b"fake jpeg content"
            )

        config_path = data_dir / "config" / "project_config.yaml"
        with open(config_path, "w") as f:
            yaml.dump({"steps_completed": {f"step{i}": True for i in range(1, 9)}}, f)

        success, _ = run_delivery(data_dir)

        assert success is True
        assert len(list((data_dir / "delivery" / "tiff_delivery").iterdir())) == 10
        assert len(list((data_dir / "delivery" / "jpeg_delivery").iterdir())) == 10


# ---------------------------------------------------------------------------
# Empty trash workflow
# ---------------------------------------------------------------------------

class TestEmptyTrash:
    """Empty trash workflow."""

    @pytest.mark.integration
    def test_empty_trash_removes_all_trash_contents(self, completed_batch):
        """All files under trash/ are deleted by empty_trash."""
        data_dir = completed_batch["data_dir"]
        svc = DeliveryService(data_dir)
        svc.create_package()
        assert svc.trash_has_files() is True

        success, _ = svc.empty_trash()

        assert success is True
        assert not svc.trash_has_files()

    @pytest.mark.integration
    def test_empty_trash_removes_trash_directory_itself(self, completed_batch):
        """trash/ directory is removed by empty_trash, not just emptied."""
        data_dir = completed_batch["data_dir"]
        svc = DeliveryService(data_dir)
        svc.create_package()

        svc.empty_trash()

        assert not svc.trash_dir.exists()

    @pytest.mark.integration
    def test_empty_trash_leaves_delivery_directory_intact(self, completed_batch):
        """delivery/ directory and its contents are untouched by empty_trash."""
        data_dir = completed_batch["data_dir"]
        svc = DeliveryService(data_dir)
        svc.create_package()

        tiff_names_before = {f.name for f in svc.delivery_tiff_dir.iterdir()}
        jpeg_names_before = {f.name for f in svc.delivery_jpeg_dir.iterdir()}

        svc.empty_trash()

        assert svc.delivery_dir.exists()
        assert {f.name for f in svc.delivery_tiff_dir.iterdir()} == tiff_names_before
        assert {f.name for f in svc.delivery_jpeg_dir.iterdir()} == jpeg_names_before

    @pytest.mark.integration
    def test_empty_trash_noop_before_delivery(self, completed_batch):
        """empty_trash returns success even when trash/ has never been created."""
        svc = DeliveryService(completed_batch["data_dir"])
        assert not svc.trash_dir.exists()

        success, _ = svc.empty_trash()

        assert success is True

    @pytest.mark.integration
    def test_empty_trash_noop_when_trash_already_empty(self, completed_batch):
        """empty_trash called twice returns success on the second call."""
        svc = DeliveryService(completed_batch["data_dir"])
        svc.create_package()
        svc.empty_trash()

        success, _ = svc.empty_trash()
        assert success is True


# ---------------------------------------------------------------------------
# Service state after operations
# ---------------------------------------------------------------------------

class TestDeliveryServiceStateIntegration:
    """Integration-level verification of state query methods."""

    @pytest.mark.integration
    def test_delivery_exists_reflects_filesystem(self, completed_batch):
        """delivery_exists() matches actual filesystem state before and after."""
        svc = DeliveryService(completed_batch["data_dir"])

        assert svc.delivery_exists() is False
        svc.create_package()
        assert svc.delivery_exists() is True

    @pytest.mark.integration
    def test_trash_has_files_reflects_filesystem(self, completed_batch):
        """trash_has_files() matches actual filesystem state before and after."""
        svc = DeliveryService(completed_batch["data_dir"])

        assert svc.trash_has_files() is False
        svc.create_package()
        assert svc.trash_has_files() is True
        svc.empty_trash()
        assert svc.trash_has_files() is False
