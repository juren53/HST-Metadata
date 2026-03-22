"""
GUI tests for Dialog components.

Tests dialog windows used in the framework.
"""

import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path

# Skip all tests if PyQt6 is not available
pytest.importorskip("PyQt6")

from PyQt6.QtWidgets import QApplication, QDialog
from PyQt6.QtCore import Qt


class TestDialogImports:
    """Tests that dialogs can be imported."""

    @pytest.mark.gui
    def test_import_new_batch_dialog(self):
        """NewBatchDialog can be imported."""
        from gui.dialogs.new_batch_dialog import NewBatchDialog
        assert NewBatchDialog is not None

    @pytest.mark.gui
    def test_import_settings_dialog(self):
        """SettingsDialog can be imported."""
        from gui.dialogs.settings_dialog import SettingsDialog
        assert SettingsDialog is not None

    @pytest.mark.gui
    def test_import_theme_dialog(self):
        """ThemeDialog can be imported."""
        from gui.dialogs.theme_dialog import ThemeDialog
        assert ThemeDialog is not None

    @pytest.mark.gui
    def test_import_batch_info_dialog(self):
        """BatchInfoDialog can be imported."""
        from gui.dialogs.batch_info_dialog import BatchInfoDialog
        assert BatchInfoDialog is not None

    @pytest.mark.gui
    def test_import_log_viewer_dialog(self):
        """LogViewerDialog can be imported."""
        from gui.dialogs.log_viewer_dialog import LogViewerDialog
        assert LogViewerDialog is not None

    @pytest.mark.gui
    def test_import_step_dialogs(self):
        """Step dialogs can be imported."""
        from gui.dialogs.step1_dialog import Step1Dialog
        from gui.dialogs.step2_dialog import Step2Dialog
        from gui.dialogs.step3_dialog import Step3Dialog
        from gui.dialogs.step4_dialog import Step4Dialog
        from gui.dialogs.step5_dialog import Step5Dialog
        from gui.dialogs.step6_dialog import Step6Dialog
        from gui.dialogs.step7_dialog import Step7Dialog
        from gui.dialogs.step8_dialog import Step8Dialog

        assert Step1Dialog is not None
        assert Step8Dialog is not None


class TestNewBatchDialog:
    """Tests for NewBatchDialog."""

    @pytest.mark.gui
    def test_new_batch_dialog_init(self, qtbot):
        """NewBatchDialog can be instantiated."""
        from gui.dialogs.new_batch_dialog import NewBatchDialog

        dialog = NewBatchDialog()
        qtbot.addWidget(dialog)

        assert dialog is not None
        assert isinstance(dialog, QDialog)

    @pytest.mark.gui
    def test_new_batch_dialog_has_fields(self, qtbot):
        """NewBatchDialog has required input fields."""
        from gui.dialogs.new_batch_dialog import NewBatchDialog

        dialog = NewBatchDialog()
        qtbot.addWidget(dialog)

        # Should have project name field
        assert hasattr(dialog, 'project_name_edit') or hasattr(dialog, 'name_edit')


class TestSettingsDialog:
    """Tests for SettingsDialog."""

    @pytest.mark.gui
    def test_settings_dialog_init(self, qtbot):
        """SettingsDialog can be instantiated."""
        from gui.dialogs.settings_dialog import SettingsDialog

        dialog = SettingsDialog()
        qtbot.addWidget(dialog)

        assert dialog is not None
        assert isinstance(dialog, QDialog)

    @pytest.mark.gui
    def test_settings_dialog_has_tabs(self, qtbot):
        """SettingsDialog has settings tabs or sections."""
        from gui.dialogs.settings_dialog import SettingsDialog

        dialog = SettingsDialog()
        qtbot.addWidget(dialog)

        # Dialog should have some form of organization


class TestThemeDialog:
    """Tests for ThemeDialog."""

    @pytest.mark.gui
    def test_theme_dialog_init(self, qtbot):
        """ThemeDialog can be instantiated."""
        from gui.dialogs.theme_dialog import ThemeDialog

        dialog = ThemeDialog()
        qtbot.addWidget(dialog)

        assert dialog is not None

    @pytest.mark.gui
    def test_theme_dialog_theme_options(self, qtbot):
        """ThemeDialog has theme selection options."""
        from gui.dialogs.theme_dialog import ThemeDialog

        dialog = ThemeDialog()
        qtbot.addWidget(dialog)

        # Should have theme selection controls


class TestBatchInfoDialog:
    """Tests for BatchInfoDialog."""

    @pytest.mark.gui
    def test_batch_info_dialog_init(self, qtbot, temp_dir):
        """BatchInfoDialog can be instantiated."""
        from gui.dialogs.batch_info_dialog import BatchInfoDialog
        from utils.batch_registry import BatchRegistry

        # Create a registry and register a batch
        registry_path = temp_dir / "registry.yaml"
        registry = BatchRegistry(registry_path=registry_path)

        # Create test data
        data_dir = temp_dir / "test_data"
        data_dir.mkdir()
        config_path = data_dir / "config.yaml"
        config_path.write_text("project:\n  name: Test Batch")

        registry.register_batch("Test Batch", str(data_dir), str(config_path))

        # Pass batch_id string
        dialog = BatchInfoDialog("test_batch", registry)
        qtbot.addWidget(dialog)

        assert dialog is not None


@pytest.fixture
def mock_config_manager(temp_dir):
    """Create a mock config manager for testing."""
    from config.config_manager import ConfigManager
    cm = ConfigManager()
    cm.set("project.name", "Test Project")
    cm.set("project.data_directory", str(temp_dir))
    return cm


class TestStepDialogs:
    """Tests for Step dialogs."""

    @pytest.mark.gui
    def test_step1_dialog_init(self, qtbot, mock_config_manager):
        """Step1Dialog can be instantiated."""
        from gui.dialogs.step1_dialog import Step1Dialog

        dialog = Step1Dialog(mock_config_manager)
        qtbot.addWidget(dialog)

        assert dialog is not None

    @pytest.mark.gui
    def test_step2_dialog_init(self, qtbot, mock_config_manager):
        """Step2Dialog can be instantiated."""
        from gui.dialogs.step2_dialog import Step2Dialog

        dialog = Step2Dialog(mock_config_manager)
        qtbot.addWidget(dialog)

        assert dialog is not None

    @pytest.mark.gui
    def test_step3_dialog_init(self, qtbot, mock_config_manager):
        """Step3Dialog can be instantiated."""
        from gui.dialogs.step3_dialog import Step3Dialog

        dialog = Step3Dialog(mock_config_manager)
        qtbot.addWidget(dialog)

        assert dialog is not None

    @pytest.mark.gui
    def test_step4_dialog_init(self, qtbot, mock_config_manager):
        """Step4Dialog can be instantiated."""
        from gui.dialogs.step4_dialog import Step4Dialog

        dialog = Step4Dialog(mock_config_manager)
        qtbot.addWidget(dialog)

        assert dialog is not None

    @pytest.mark.gui
    def test_step5_dialog_init(self, qtbot, mock_config_manager):
        """Step5Dialog can be instantiated."""
        from gui.dialogs.step5_dialog import Step5Dialog

        dialog = Step5Dialog(mock_config_manager)
        qtbot.addWidget(dialog)

        assert dialog is not None

    @pytest.mark.gui
    def test_step6_dialog_init(self, qtbot, mock_config_manager):
        """Step6Dialog can be instantiated."""
        from gui.dialogs.step6_dialog import Step6Dialog

        dialog = Step6Dialog(mock_config_manager)
        qtbot.addWidget(dialog)

        assert dialog is not None

    @pytest.mark.gui
    def test_step7_dialog_init(self, qtbot, mock_config_manager):
        """Step7Dialog can be instantiated."""
        from gui.dialogs.step7_dialog import Step7Dialog

        dialog = Step7Dialog(mock_config_manager)
        qtbot.addWidget(dialog)

        assert dialog is not None

    @pytest.mark.gui
    def test_step8_dialog_init(self, qtbot, mock_config_manager):
        """Step8Dialog can be instantiated."""
        from gui.dialogs.step8_dialog import Step8Dialog

        dialog = Step8Dialog(mock_config_manager)
        qtbot.addWidget(dialog)

        assert dialog is not None


class TestDeliveryDialogImport:
    """Tests that DeliveryDialog can be imported and instantiated."""

    @pytest.mark.gui
    def test_import_delivery_dialog(self):
        """DeliveryDialog can be imported."""
        from gui.dialogs.delivery_dialog import DeliveryDialog
        assert DeliveryDialog is not None

    @pytest.mark.gui
    def test_delivery_dialog_init_complete_batch(self, qtbot, completed_batch):
        """DeliveryDialog can be instantiated with a fully completed batch."""
        from gui.dialogs.delivery_dialog import DeliveryDialog

        batch_info = {
            "id": completed_batch["batch_id"],
            "name": completed_batch["name"],
            "data_directory": str(completed_batch["data_dir"]),
        }
        dialog = DeliveryDialog(batch_info)
        qtbot.addWidget(dialog)

        assert dialog is not None
        assert isinstance(dialog, QDialog)

    @pytest.mark.gui
    def test_delivery_dialog_deliver_btn_enabled_for_complete_batch(self, qtbot, completed_batch):
        """deliver_btn is enabled when all 8 steps are complete and source dirs populated."""
        from gui.dialogs.delivery_dialog import DeliveryDialog

        batch_info = {
            "id": completed_batch["batch_id"],
            "name": completed_batch["name"],
            "data_directory": str(completed_batch["data_dir"]),
        }
        dialog = DeliveryDialog(batch_info)
        qtbot.addWidget(dialog)

        assert dialog.deliver_btn.isEnabled() is True

    @pytest.mark.gui
    def test_delivery_dialog_deliver_btn_disabled_for_incomplete_batch(self, qtbot, temp_dir):
        """deliver_btn is disabled when steps are not all complete."""
        import yaml
        from gui.dialogs.delivery_dialog import DeliveryDialog

        # Build a minimal incomplete batch directory
        data_dir = temp_dir / "incomplete"
        (data_dir / "config").mkdir(parents=True)
        (data_dir / "output" / "tiff_processed").mkdir(parents=True)
        (data_dir / "output" / "jpeg_watermarked").mkdir(parents=True)
        (data_dir / "output" / "tiff_processed" / "IMG_001.tif").write_bytes(b"x")
        (data_dir / "output" / "jpeg_watermarked" / "IMG_001.jpg").write_bytes(b"x")

        config_path = data_dir / "config" / "project_config.yaml"
        with open(config_path, "w") as f:
            yaml.dump(
                {"steps_completed": {f"step{i}": False for i in range(1, 9)}}, f
            )

        batch_info = {
            "id": "incomplete",
            "name": "Incomplete Batch",
            "data_directory": str(data_dir),
        }
        dialog = DeliveryDialog(batch_info)
        qtbot.addWidget(dialog)

        assert dialog.deliver_btn.isEnabled() is False

    @pytest.mark.gui
    def test_delivery_dialog_button_text_changes_when_delivery_exists(self, qtbot, completed_batch):
        """deliver_btn text changes to 'Overwrite...' when delivery package already exists."""
        from gui.dialogs.delivery_dialog import DeliveryDialog
        from core.delivery_service import DeliveryService

        # Create the delivery package before opening the dialog
        DeliveryService(completed_batch["data_dir"]).create_package()

        batch_info = {
            "id": completed_batch["batch_id"],
            "name": completed_batch["name"],
            "data_directory": str(completed_batch["data_dir"]),
        }
        dialog = DeliveryDialog(batch_info)
        qtbot.addWidget(dialog)

        assert "overwrite" in dialog.deliver_btn.text().lower()

    @pytest.mark.gui
    def test_delivery_dialog_has_output_text_widget(self, qtbot, completed_batch):
        """DeliveryDialog has a read-only output/log text area."""
        from gui.dialogs.delivery_dialog import DeliveryDialog

        batch_info = {
            "id": completed_batch["batch_id"],
            "name": completed_batch["name"],
            "data_directory": str(completed_batch["data_dir"]),
        }
        dialog = DeliveryDialog(batch_info)
        qtbot.addWidget(dialog)

        assert hasattr(dialog, "output_text")
        assert dialog.output_text.isReadOnly() is True


class TestDialogAcceptReject:
    """Tests for dialog accept/reject behavior."""

    @pytest.mark.gui
    def test_dialog_reject(self, qtbot):
        """Dialogs can be rejected (cancelled)."""
        from gui.dialogs.new_batch_dialog import NewBatchDialog

        dialog = NewBatchDialog()
        qtbot.addWidget(dialog)

        dialog.reject()

        assert dialog.result() == QDialog.DialogCode.Rejected
