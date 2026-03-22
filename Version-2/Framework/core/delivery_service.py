"""
Delivery Service for HSTL Photo Framework

Business logic for creating final delivery packages at the completion
of the 8-step workflow. Handles copying delivery products, moving
intermediate artifacts to trash, and emptying trash.
"""

import shutil
import yaml
from pathlib import Path
from datetime import datetime
from typing import Callable, Optional


class DeliveryService:
    """Manages final delivery package creation and trash operations."""

    def __init__(self, data_directory: Path, log_manager=None):
        self.data_dir = Path(data_directory)
        self.log_manager = log_manager

    # -------------------------------------------------------------------------
    # Source paths (existing workflow output)
    # -------------------------------------------------------------------------

    @property
    def tiff_processed_dir(self) -> Path:
        return self.data_dir / "output" / "tiff_processed"

    @property
    def jpeg_watermarked_dir(self) -> Path:
        return self.data_dir / "output" / "jpeg_watermarked"

    @property
    def jpeg_dir(self) -> Path:
        return self.data_dir / "output" / "jpeg"

    @property
    def jpeg_resized_dir(self) -> Path:
        return self.data_dir / "output" / "jpeg_resized"

    # -------------------------------------------------------------------------
    # Destination paths (new delivery/trash structure)
    # -------------------------------------------------------------------------

    @property
    def delivery_dir(self) -> Path:
        return self.data_dir / "delivery"

    @property
    def delivery_tiff_dir(self) -> Path:
        return self.data_dir / "delivery" / "tiff_delivery"

    @property
    def delivery_jpeg_dir(self) -> Path:
        return self.data_dir / "delivery" / "jpeg_delivery"

    @property
    def trash_dir(self) -> Path:
        return self.data_dir / "trash"

    @property
    def trash_jpeg_converted_dir(self) -> Path:
        return self.data_dir / "trash" / "jpeg_converted"

    @property
    def trash_jpeg_resized_dir(self) -> Path:
        return self.data_dir / "trash" / "jpeg_resized"

    # -------------------------------------------------------------------------
    # State queries
    # -------------------------------------------------------------------------

    def all_steps_complete(self) -> bool:
        """Return True if all 8 workflow steps are marked complete in config."""
        config_path = self.data_dir / "config" / "project_config.yaml"
        if not config_path.exists():
            return False
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
            steps = config.get("steps_completed", {})
            return len(steps) == 8 and all(steps.values())
        except Exception:
            return False

    def delivery_exists(self) -> bool:
        """Return True if a delivery package has already been created."""
        if not self.delivery_dir.exists():
            return False
        return any(self.delivery_dir.rglob("*.*"))

    def trash_has_files(self) -> bool:
        """Return True if the trash directory contains files."""
        if not self.trash_dir.exists():
            return False
        return any(self.trash_dir.rglob("*.*"))

    def get_file_counts(self) -> dict:
        """Return file counts for the confirmation summary."""
        def count(d: Path) -> int:
            return len([f for f in d.iterdir() if f.is_file()]) if d.exists() else 0

        return {
            "tiff_delivery": count(self.tiff_processed_dir),
            "jpeg_delivery": count(self.jpeg_watermarked_dir),
            "jpeg_to_trash": count(self.jpeg_dir),
            "jpeg_resized_to_trash": count(self.jpeg_resized_dir),
        }

    # -------------------------------------------------------------------------
    # Operations
    # -------------------------------------------------------------------------

    def validate(self) -> tuple[bool, str]:
        """
        Validate preconditions before creating a delivery package.

        Returns:
            (True, "ok") on success, (False, reason) on failure.
        """
        if not self.all_steps_complete():
            return False, (
                "Not all 8 steps are complete.\n"
                "Complete all workflow steps before creating a delivery package."
            )
        if not self.tiff_processed_dir.exists() or not any(
            f for f in self.tiff_processed_dir.iterdir() if f.is_file()
        ):
            return False, f"Source directory is empty or missing:\n{self.tiff_processed_dir}"
        if not self.jpeg_watermarked_dir.exists() or not any(
            f for f in self.jpeg_watermarked_dir.iterdir() if f.is_file()
        ):
            return False, f"Source directory is empty or missing:\n{self.jpeg_watermarked_dir}"
        return True, "ok"

    def create_package(
        self, progress_callback: Optional[Callable[[str], None]] = None
    ) -> tuple[bool, str]:
        """
        Create the delivery package.

        Operations performed in sequence:
          1. COPY tiff_processed  → delivery/tiff_delivery
          2. COPY jpeg_watermarked → delivery/jpeg_delivery
          3. MOVE output/jpeg      → trash/jpeg_converted
          4. MOVE output/jpeg_resized → trash/jpeg_resized

        Args:
            progress_callback: Optional callable to receive progress messages.

        Returns:
            (True, summary) on success, (False, error_message) on failure.
        """
        def log(msg: str):
            if progress_callback:
                progress_callback(msg)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log(f"Delivery package creation started: {timestamp}")
        log(f"Batch: {self.data_dir.name}")
        log("")

        try:
            # --- Step 1: Copy TIFFs to delivery ---
            log("Copying TIFFs to delivery/tiff_delivery/...")
            self.delivery_tiff_dir.mkdir(parents=True, exist_ok=True)
            tiff_count = 0
            for f in sorted(self.tiff_processed_dir.iterdir()):
                if f.is_file():
                    shutil.copy2(f, self.delivery_tiff_dir / f.name)
                    tiff_count += 1
                    log(f"  ✓ {f.name}")
            log(f"  {tiff_count} TIFF file(s) copied")
            log("")

            # --- Step 2: Copy JPEGs to delivery ---
            log("Copying JPEGs to delivery/jpeg_delivery/...")
            self.delivery_jpeg_dir.mkdir(parents=True, exist_ok=True)
            jpeg_count = 0
            for f in sorted(self.jpeg_watermarked_dir.iterdir()):
                if f.is_file():
                    shutil.copy2(f, self.delivery_jpeg_dir / f.name)
                    jpeg_count += 1
                    log(f"  ✓ {f.name}")
            log(f"  {jpeg_count} JPEG file(s) copied")
            log("")

            # --- Step 3: Move output/jpeg to trash/jpeg_converted ---
            if self.jpeg_dir.exists():
                files = [f for f in self.jpeg_dir.iterdir() if f.is_file()]
                if files:
                    log("Moving converted JPEGs to trash/jpeg_converted/...")
                    self.trash_jpeg_converted_dir.mkdir(parents=True, exist_ok=True)
                    for f in sorted(files):
                        shutil.move(str(f), self.trash_jpeg_converted_dir / f.name)
                        log(f"  → {f.name}")
                    log(f"  {len(files)} file(s) moved to trash")
                    log("")

            # --- Step 4: Move output/jpeg_resized to trash/jpeg_resized ---
            if self.jpeg_resized_dir.exists():
                files = [f for f in self.jpeg_resized_dir.iterdir() if f.is_file()]
                if files:
                    log("Moving resized JPEGs to trash/jpeg_resized/...")
                    self.trash_jpeg_resized_dir.mkdir(parents=True, exist_ok=True)
                    for f in sorted(files):
                        shutil.move(str(f), self.trash_jpeg_resized_dir / f.name)
                        log(f"  → {f.name}")
                    log(f"  {len(files)} file(s) moved to trash")
                    log("")

            completed = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log(f"✅ Delivery package created successfully: {completed}")
            log(f"   Location: {self.delivery_dir}")

            if self.log_manager:
                self.log_manager.success(
                    f"Delivery package created: {tiff_count} TIFFs, {jpeg_count} JPEGs"
                )

            return True, f"Delivery package created: {tiff_count} TIFFs, {jpeg_count} JPEGs"

        except Exception as e:
            msg = f"Delivery failed: {str(e)}"
            log(f"\n❌ {msg}")
            if self.log_manager:
                self.log_manager.error(msg)
            return False, msg

    def empty_trash(
        self, progress_callback: Optional[Callable[[str], None]] = None
    ) -> tuple[bool, str]:
        """
        Permanently delete all files in the trash directory.

        Returns:
            (True, summary) on success, (False, error_message) on failure.
        """
        def log(msg: str):
            if progress_callback:
                progress_callback(msg)

        if not self.trash_dir.exists():
            return True, "Trash directory does not exist — nothing to delete."

        try:
            file_count = sum(1 for _ in self.trash_dir.rglob("*") if _.is_file())
            shutil.rmtree(self.trash_dir)
            msg = f"Deleted {file_count} file(s) from trash."
            log(f"✅ {msg}")
            if self.log_manager:
                self.log_manager.info(msg)
            return True, msg
        except Exception as e:
            msg = f"Failed to empty trash: {str(e)}"
            log(f"❌ {msg}")
            return False, msg
