"""
Unit tests for DeliveryService.

Tests business logic for delivery package creation and trash management.
All operations run against real temporary directories — no filesystem mocking —
because the feature is fundamentally file I/O and real tests are more reliable.
"""

import shutil
import pytest
from pathlib import Path

from core.delivery_service import DeliveryService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_service(completed_batch) -> DeliveryService:
    return DeliveryService(completed_batch["data_dir"])


def run_delivery(completed_batch) -> tuple:
    """Run create_package and return (success, message, log_lines)."""
    log = []
    svc = make_service(completed_batch)
    success, message = svc.create_package(progress_callback=log.append)
    return success, message, log


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

class TestDeliveryServiceValidation:
    """Guard conditions checked before package creation begins."""

    @pytest.mark.unit
    def test_rejects_incomplete_batch(self, temp_dir):
        """Returns failure when steps are not all complete."""
        data_dir = temp_dir / "incomplete"
        (data_dir / "config").mkdir(parents=True)

        import yaml
        config_path = data_dir / "config" / "project_config.yaml"
        with open(config_path, "w") as f:
            yaml.dump(
                {"steps_completed": {f"step{i}": False for i in range(1, 9)}}, f
            )

        svc = DeliveryService(data_dir)
        valid, reason = svc.validate()

        assert valid is False
        assert "steps" in reason.lower() or "complete" in reason.lower()

    @pytest.mark.unit
    def test_rejects_missing_tiff_processed_dir(self, completed_batch):
        """Returns failure when output/tiff_processed does not exist."""
        shutil.rmtree(completed_batch["data_dir"] / "output" / "tiff_processed")
        svc = make_service(completed_batch)
        valid, reason = svc.validate()
        assert valid is False
        assert "tiff_processed" in reason

    @pytest.mark.unit
    def test_rejects_missing_jpeg_watermarked_dir(self, completed_batch):
        """Returns failure when output/jpeg_watermarked does not exist."""
        shutil.rmtree(completed_batch["data_dir"] / "output" / "jpeg_watermarked")
        svc = make_service(completed_batch)
        valid, reason = svc.validate()
        assert valid is False
        assert "jpeg_watermarked" in reason

    @pytest.mark.unit
    def test_rejects_empty_tiff_processed_dir(self, completed_batch):
        """Returns failure when tiff_processed exists but contains no files."""
        tiff_dir = completed_batch["data_dir"] / "output" / "tiff_processed"
        for f in tiff_dir.iterdir():
            f.unlink()
        svc = make_service(completed_batch)
        valid, reason = svc.validate()
        assert valid is False

    @pytest.mark.unit
    def test_rejects_empty_jpeg_watermarked_dir(self, completed_batch):
        """Returns failure when jpeg_watermarked exists but contains no files."""
        jpeg_dir = completed_batch["data_dir"] / "output" / "jpeg_watermarked"
        for f in jpeg_dir.iterdir():
            f.unlink()
        svc = make_service(completed_batch)
        valid, reason = svc.validate()
        assert valid is False

    @pytest.mark.unit
    def test_accepts_valid_completed_batch(self, completed_batch):
        """Validation passes when all 8 steps done and source dirs populated."""
        svc = make_service(completed_batch)
        valid, reason = svc.validate()
        assert valid is True
        assert reason == "ok"


# ---------------------------------------------------------------------------
# Execution — file operations
# ---------------------------------------------------------------------------

class TestDeliveryServiceExecution:
    """File operations performed during package creation."""

    @pytest.mark.unit
    def test_returns_success(self, completed_batch):
        """create_package returns (True, message) on success."""
        success, message, _ = run_delivery(completed_batch)
        assert success is True
        assert message

    @pytest.mark.unit
    def test_creates_delivery_tiff_directory(self, completed_batch):
        """delivery/tiff_delivery/ is created."""
        run_delivery(completed_batch)
        assert (completed_batch["data_dir"] / "delivery" / "tiff_delivery").exists()

    @pytest.mark.unit
    def test_creates_delivery_jpeg_directory(self, completed_batch):
        """delivery/jpeg_delivery/ is created."""
        run_delivery(completed_batch)
        assert (completed_batch["data_dir"] / "delivery" / "jpeg_delivery").exists()

    @pytest.mark.unit
    def test_copies_tiffs_to_delivery(self, completed_batch):
        """All files from tiff_processed land in delivery/tiff_delivery/."""
        data_dir = completed_batch["data_dir"]
        source_files = {f.name for f in (data_dir / "output" / "tiff_processed").iterdir()}

        run_delivery(completed_batch)

        delivered = {f.name for f in (data_dir / "delivery" / "tiff_delivery").iterdir()}
        assert delivered == source_files

    @pytest.mark.unit
    def test_copies_jpegs_to_delivery(self, completed_batch):
        """All files from jpeg_watermarked land in delivery/jpeg_delivery/."""
        data_dir = completed_batch["data_dir"]
        source_files = {f.name for f in (data_dir / "output" / "jpeg_watermarked").iterdir()}

        run_delivery(completed_batch)

        delivered = {f.name for f in (data_dir / "delivery" / "jpeg_delivery").iterdir()}
        assert delivered == source_files

    @pytest.mark.unit
    def test_source_tiffs_remain_after_copy(self, completed_batch):
        """tiff_processed still has files after delivery (copy, not move)."""
        data_dir = completed_batch["data_dir"]
        source_count_before = len(list((data_dir / "output" / "tiff_processed").iterdir()))

        run_delivery(completed_batch)

        source_count_after = len(list((data_dir / "output" / "tiff_processed").iterdir()))
        assert source_count_after == source_count_before

    @pytest.mark.unit
    def test_moves_intermediate_jpegs_to_trash(self, completed_batch):
        """output/jpeg contents are moved to trash/jpeg_converted/ (not copied)."""
        data_dir = completed_batch["data_dir"]
        jpeg_dir = data_dir / "output" / "jpeg"
        source_files = {f.name for f in jpeg_dir.iterdir()}

        run_delivery(completed_batch)

        # Moved — source should now be empty
        remaining = [f for f in jpeg_dir.iterdir() if f.is_file()]
        assert len(remaining) == 0
        # And present in trash
        trash_files = {f.name for f in (data_dir / "trash" / "jpeg_converted").iterdir()}
        assert trash_files == source_files

    @pytest.mark.unit
    def test_moves_resized_jpegs_to_trash(self, completed_batch):
        """output/jpeg_resized contents are moved to trash/jpeg_resized/ (not copied)."""
        data_dir = completed_batch["data_dir"]
        resized_dir = data_dir / "output" / "jpeg_resized"
        source_files = {f.name for f in resized_dir.iterdir()}

        run_delivery(completed_batch)

        remaining = [f for f in resized_dir.iterdir() if f.is_file()]
        assert len(remaining) == 0
        trash_files = {f.name for f in (data_dir / "trash" / "jpeg_resized").iterdir()}
        assert trash_files == source_files

    @pytest.mark.unit
    def test_progress_callback_receives_messages(self, completed_batch):
        """progress_callback is called with log messages during execution."""
        log = []
        svc = make_service(completed_batch)
        svc.create_package(progress_callback=log.append)
        assert len(log) > 0
        full_log = "\n".join(log)
        assert "delivery" in full_log.lower() or "tiff" in full_log.lower()

    @pytest.mark.unit
    def test_progress_callback_is_optional(self, completed_batch):
        """create_package succeeds when no progress_callback is provided."""
        svc = make_service(completed_batch)
        success, _ = svc.create_package()
        assert success is True


# ---------------------------------------------------------------------------
# State queries
# ---------------------------------------------------------------------------

class TestDeliveryServiceStateQueries:
    """Tests for delivery_exists, trash_has_files, get_file_counts."""

    @pytest.mark.unit
    def test_delivery_exists_false_before_package_created(self, completed_batch):
        """delivery_exists() is False before create_package is called."""
        svc = make_service(completed_batch)
        assert svc.delivery_exists() is False

    @pytest.mark.unit
    def test_delivery_exists_true_after_package_created(self, completed_batch):
        """delivery_exists() is True after create_package succeeds."""
        svc = make_service(completed_batch)
        svc.create_package()
        assert svc.delivery_exists() is True

    @pytest.mark.unit
    def test_trash_has_files_false_before_delivery(self, completed_batch):
        """trash_has_files() is False before create_package is called."""
        svc = make_service(completed_batch)
        assert svc.trash_has_files() is False

    @pytest.mark.unit
    def test_trash_has_files_true_after_delivery(self, completed_batch):
        """trash_has_files() is True after intermediate files moved to trash."""
        svc = make_service(completed_batch)
        svc.create_package()
        assert svc.trash_has_files() is True

    @pytest.mark.unit
    def test_get_file_counts_returns_correct_tiff_count(self, completed_batch):
        """get_file_counts tiff_delivery count matches tiff_processed file count."""
        data_dir = completed_batch["data_dir"]
        expected = len(list((data_dir / "output" / "tiff_processed").iterdir()))
        svc = make_service(completed_batch)
        counts = svc.get_file_counts()
        assert counts["tiff_delivery"] == expected

    @pytest.mark.unit
    def test_get_file_counts_returns_correct_jpeg_count(self, completed_batch):
        """get_file_counts jpeg_delivery count matches jpeg_watermarked file count."""
        data_dir = completed_batch["data_dir"]
        expected = len(list((data_dir / "output" / "jpeg_watermarked").iterdir()))
        svc = make_service(completed_batch)
        counts = svc.get_file_counts()
        assert counts["jpeg_delivery"] == expected

    @pytest.mark.unit
    def test_all_steps_complete_true_for_completed_batch(self, completed_batch):
        """all_steps_complete() returns True for a batch with all steps done."""
        svc = make_service(completed_batch)
        assert svc.all_steps_complete() is True

    @pytest.mark.unit
    def test_all_steps_complete_false_when_config_missing(self, temp_dir):
        """all_steps_complete() returns False when config file is absent."""
        svc = DeliveryService(temp_dir / "no_such_batch")
        assert svc.all_steps_complete() is False


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestDeliveryServiceEdgeCases:
    """Error handling and boundary conditions."""

    @pytest.mark.unit
    def test_second_run_succeeds(self, completed_batch):
        """Calling create_package twice succeeds (delivery dir exists but is overwritten)."""
        svc = make_service(completed_batch)
        svc.create_package()

        # Re-add source JPEG files so second run has something to move
        data_dir = completed_batch["data_dir"]
        (data_dir / "output" / "jpeg" / "IMG_002.jpg").write_bytes(b"new file")
        (data_dir / "output" / "jpeg_resized" / "IMG_002.jpg").write_bytes(b"new file")

        success, _ = svc.create_package()
        assert success is True

    @pytest.mark.unit
    def test_create_package_skips_absent_jpeg_dir(self, completed_batch):
        """create_package succeeds even if output/jpeg does not exist."""
        data_dir = completed_batch["data_dir"]
        shutil.rmtree(data_dir / "output" / "jpeg")
        success, _ = make_service(completed_batch).create_package()
        assert success is True

    @pytest.mark.unit
    def test_create_package_skips_absent_jpeg_resized_dir(self, completed_batch):
        """create_package succeeds even if output/jpeg_resized does not exist."""
        data_dir = completed_batch["data_dir"]
        shutil.rmtree(data_dir / "output" / "jpeg_resized")
        success, _ = make_service(completed_batch).create_package()
        assert success is True

    @pytest.mark.unit
    def test_empty_trash_removes_all_files(self, completed_batch):
        """empty_trash deletes every file under trash/."""
        svc = make_service(completed_batch)
        svc.create_package()
        assert svc.trash_has_files() is True

        success, _ = svc.empty_trash()

        assert success is True
        assert svc.trash_has_files() is False

    @pytest.mark.unit
    def test_empty_trash_noop_when_trash_dir_absent(self, completed_batch):
        """empty_trash returns success even if trash/ does not exist."""
        svc = make_service(completed_batch)
        assert not svc.trash_dir.exists()
        success, message = svc.empty_trash()
        assert success is True

    @pytest.mark.unit
    def test_empty_trash_leaves_delivery_intact(self, completed_batch):
        """empty_trash does not touch the delivery/ directory."""
        svc = make_service(completed_batch)
        svc.create_package()

        tiff_count_before = len(list(svc.delivery_tiff_dir.iterdir()))
        jpeg_count_before = len(list(svc.delivery_jpeg_dir.iterdir()))

        svc.empty_trash()

        assert len(list(svc.delivery_tiff_dir.iterdir())) == tiff_count_before
        assert len(list(svc.delivery_jpeg_dir.iterdir())) == jpeg_count_before

    @pytest.mark.unit
    def test_partial_failure_returns_false(self, completed_batch, monkeypatch):
        """If shutil.copy2 raises mid-run, create_package returns (False, error)."""
        import shutil as _shutil

        monkeypatch.setattr(_shutil, "copy2", lambda src, dst: (_ for _ in ()).throw(OSError("Disk full")))
        svc = make_service(completed_batch)
        success, message = svc.create_package()
        assert success is False
        assert message  # some error description returned
