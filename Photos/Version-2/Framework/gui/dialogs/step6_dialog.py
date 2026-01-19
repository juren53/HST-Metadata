"""
Step 6 Dialog - JPEG Conversion

Converts processed TIFF files to JPEG format while preserving all metadata.
"""

import os
import glob
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QMessageBox, QProgressBar, QGroupBox, QSpinBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from utils.log_manager import get_log_manager


class JpegConversionThread(QThread):
    """Worker thread for JPEG conversion."""
    
    progress = pyqtSignal(str)  # Progress messages
    finished = pyqtSignal(bool, dict)  # Success/failure, stats dict
    error = pyqtSignal(str)  # Error messages
    
    def __init__(self, tiff_dir, output_dir, report_dir, quality):
        super().__init__()
        self.tiff_dir = tiff_dir
        self.output_dir = output_dir
        self.report_dir = report_dir
        self.quality = quality
        
    def run(self):
        """Run the JPEG conversion process."""
        try:
            from PIL import Image
            import exiftool
            
            stats = {
                'tiff_files_found': 0,
                'converted': 0,
                'failed': 0,
                'failed_list': []
            }
            
            self.progress.emit("Starting JPEG conversion...")
            self.progress.emit(f"Source directory: {self.tiff_dir}")
            self.progress.emit(f"Output directory: {self.output_dir}")
            self.progress.emit(f"Quality setting: {self.quality}")
            
            # Ensure output directory exists
            Path(self.output_dir).mkdir(parents=True, exist_ok=True)
            
            # Find all TIFF files
            tiff_files = glob.glob(str(Path(self.tiff_dir) / '*.tif')) + \
                        glob.glob(str(Path(self.tiff_dir) / '*.tiff'))
            stats['tiff_files_found'] = len(tiff_files)
            
            if stats['tiff_files_found'] == 0:
                self.error.emit(f"No TIFF files found in {self.tiff_dir}")
                return
            
            self.progress.emit(f"✓ Found {stats['tiff_files_found']} TIFF files")
            self.progress.emit("")
            self.progress.emit("Starting conversion...")
            
            # Process each TIFF file
            for tiff_path in tiff_files:
                tiff_path = Path(tiff_path)
                jpeg_filename = tiff_path.stem + '.jpg'
                jpeg_path = Path(self.output_dir) / jpeg_filename
                
                try:
                    # Show progress for current file
                    self.progress.emit(f"Converting: {tiff_path.name} → {jpeg_filename}")
                    
                    # Open TIFF image
                    with Image.open(tiff_path) as img:
                        # Get image dimensions for feedback
                        dimensions = f"{img.width}x{img.height}"
                        
                        # Convert to RGB if necessary (JPEG doesn't support transparency)
                        if img.mode in ('RGBA', 'LA', 'P'):
                            # Create white background
                            background = Image.new('RGB', img.size, (255, 255, 255))
                            if img.mode == 'P':
                                img = img.convert('RGBA')
                            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                            img = background
                        elif img.mode != 'RGB':
                            img = img.convert('RGB')
                        
                        # Extract EXIF data if present
                        exif_data = None
                        if 'exif' in img.info:
                            exif_data = img.info['exif']
                        
                        # Save as JPEG with metadata
                        save_kwargs = {
                            'format': 'JPEG',
                            'quality': self.quality,
                            'optimize': True
                        }
                        
                        if exif_data:
                            save_kwargs['exif'] = exif_data
                        
                        img.save(jpeg_path, **save_kwargs)
                    
                    # Use exiftool to copy all metadata tags from TIFF to JPEG
                    # This ensures IPTC and XMP metadata are preserved
                    import exiftool
                    with exiftool.ExifTool() as et:
                        # Copy all tags from source TIFF to destination JPEG
                        et.execute(
                            b"-TagsFromFile",
                            str(tiff_path).encode('utf-8'),
                            b"-all:all",
                            b"-overwrite_original",
                            str(jpeg_path).encode('utf-8')
                        )
                    
                    # Get file size for feedback
                    jpeg_size_kb = jpeg_path.stat().st_size / 1024
                    
                    stats['converted'] += 1
                    self.progress.emit(f"  ✓ Saved: {jpeg_filename} ({dimensions}, {jpeg_size_kb:.1f} KB, quality {self.quality}%)")
                    
                    if stats['converted'] % 10 == 0:
                        self.progress.emit(f"\n--- Progress checkpoint: {stats['converted']}/{stats['tiff_files_found']} files completed ---\n")
                    
                except Exception as e:
                    self.progress.emit(f"⚠️  Failed: {tiff_path.name} - {str(e)}")
                    stats['failed'] += 1
                    stats['failed_list'].append(tiff_path.name)
            
            self.progress.emit("")
            self.progress.emit(f"✓ Conversion complete!")
            self.progress.emit(f"✓ Converted: {stats['converted']} files")
            self.progress.emit(f"✓ Failed: {stats['failed']} files")
            self.progress.emit(f"")
            self.progress.emit(f"✓ JPEG files saved to: {self.output_dir}")
            
            # Generate report
            self._generate_report(stats)
            
            self.finished.emit(True, stats)
            
        except Exception as e:
            self.error.emit(f"Error during JPEG conversion: {str(e)}")
    
    def _generate_report(self, stats):
        """Generate a report file."""
        try:
            current_datetime = datetime.now()
            formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
            report_filename = f"REPORT_JPEG_CONVERSION-{formatted_datetime}.txt"
            report_path = Path(self.report_dir) / report_filename
            
            # Ensure report directory exists
            Path(self.report_dir).mkdir(parents=True, exist_ok=True)
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write("=" * 70 + "\n")
                f.write("JPEG CONVERSION REPORT\n")
                f.write("=" * 70 + "\n")
                f.write(f"Report generated: {current_datetime.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("\n")
                f.write(f"Source directory: {self.tiff_dir}\n")
                f.write(f"Output directory: {self.output_dir}\n")
                f.write(f"Quality setting: {self.quality}\n")
                f.write("\n")
                f.write("SUMMARY:\n")
                f.write("-" * 70 + "\n")
                f.write(f"TIFF files found: {stats['tiff_files_found']}\n")
                f.write(f"Successfully converted: {stats['converted']}\n")
                f.write(f"Failed: {stats['failed']}\n")
                f.write("\n")
                
                if stats['failed_list']:
                    f.write("FAILED CONVERSIONS:\n")
                    f.write("-" * 70 + "\n")
                    for failed in stats['failed_list']:
                        f.write(f"  - {failed}\n")
                    f.write("\n")
                
                f.write("=" * 70 + "\n")
            
            self.progress.emit(f"✓ Report saved: {report_filename}")
            
        except Exception as e:
            self.progress.emit(f"⚠️  Failed to generate report: {str(e)}")


class Step6Dialog(QDialog):
    """Dialog for Step 6: JPEG Conversion."""

    def __init__(self, config_manager, parent=None, batch_id=None):
        super().__init__(parent)

        self.config_manager = config_manager
        self.batch_id = batch_id
        self.conversion_thread = None
        self.log_manager = get_log_manager()

        self.setWindowTitle("Step 6: JPEG Conversion")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)

        self.log_manager.debug("Opened Step 6 dialog", batch_id=batch_id, step=6)
        self._init_ui()
        self._analyze_files()
        
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Title and description
        title_label = QLabel("<h2>Step 6: JPEG Conversion</h2>")
        layout.addWidget(title_label)
        
        desc_label = QLabel(
            "<p>This step converts processed TIFF files to JPEG format while "
            "preserving all metadata tags (EXIF, IPTC, XMP).</p>"
        )
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        layout.addSpacing(10)
        
        # Settings section
        settings_group = QGroupBox("Conversion Settings")
        settings_layout = QHBoxLayout(settings_group)
        
        quality_label = QLabel("JPEG Quality:")
        settings_layout.addWidget(quality_label)
        
        self.quality_spinbox = QSpinBox()
        self.quality_spinbox.setRange(1, 100)
        self.quality_spinbox.setValue(
            self.config_manager.get('step_configurations.step6.quality', 85)
        )
        self.quality_spinbox.setSuffix("%")
        self.quality_spinbox.setToolTip("Higher values = better quality, larger file size")
        settings_layout.addWidget(self.quality_spinbox)
        
        settings_layout.addStretch()
        
        layout.addWidget(settings_group)
        
        layout.addSpacing(10)
        
        # File analysis section
        analysis_group = QGroupBox("File Analysis")
        analysis_layout = QVBoxLayout(analysis_group)
        
        self.tiff_count_label = QLabel("TIFF files: Analyzing...")
        self.jpeg_count_label = QLabel("Existing JPEGs: Analyzing...")
        
        analysis_layout.addWidget(self.tiff_count_label)
        analysis_layout.addWidget(self.jpeg_count_label)
        
        layout.addWidget(analysis_group)
        
        layout.addSpacing(10)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Output/Status section
        status_label = QLabel("<b>Status & Output:</b>")
        layout.addWidget(status_label)
        
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setMinimumHeight(250)
        layout.addWidget(self.output_text)
        
        layout.addSpacing(20)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.convert_btn = QPushButton("Start Conversion")
        self.convert_btn.setDefault(True)
        self.convert_btn.setEnabled(False)
        self.convert_btn.clicked.connect(self._start_conversion)
        button_layout.addWidget(self.convert_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.reject)
        button_layout.addWidget(close_btn)
        
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
    def _analyze_files(self):
        """Analyze TIFF and JPEG files before processing."""
        try:
            data_directory = self.config_manager.get('project.data_directory', '')
            if not data_directory:
                self.log_manager.warning("Error: Project data directory not set", batch_id=self.batch_id, step=6)
                return
            
            # TIFF directory (processed)
            tiff_dir = Path(data_directory) / 'output' / 'tiff_processed'
            
            # JPEG output directory
            jpeg_dir = Path(data_directory) / 'output' / 'jpeg'
            
            if not tiff_dir.exists():
                self.log_manager.warning(f"TIFF directory not found: {tiff_dir}", batch_id=self.batch_id, step=6)
                self.tiff_count_label.setText("TIFF files: Directory not found")
                self.log_manager.warning("Have you completed Step 5?", batch_id=self.batch_id, step=6)
                return
            
            # Count TIFF files
            tiff_files = glob.glob(str(tiff_dir / '*.tif')) + glob.glob(str(tiff_dir / '*.tiff'))
            tiff_count = len(tiff_files)
            
            self.tiff_count_label.setText(f"TIFF files: {tiff_count}")
            
            # Count existing JPEG files
            jpeg_files = glob.glob(str(jpeg_dir / '*.jpg')) + glob.glob(str(jpeg_dir / '*.jpeg'))
            jpeg_count = len(jpeg_files)
            
            self.jpeg_count_label.setText(f"Existing JPEGs: {jpeg_count}")
            
            if tiff_count == 0:
                self.log_manager.warning("No TIFF files found for conversion", batch_id=self.batch_id, step=6)
                self.log_manager.warning("Please complete Step 5 first", batch_id=self.batch_id, step=6)
                return
            
            self.log_manager.info("File analysis complete.", batch_id=self.batch_id, step=6)
            self.log_manager.info(f"TIFF files to convert: {tiff_count}", batch_id=self.batch_id, step=6)
            
            if jpeg_count > 0:
                self.log_manager.warning(f"Warning: {jpeg_count} JPEG files already exist and will be overwritten", batch_id=self.batch_id, step=6)
            
            self.log_manager.info("Ready to proceed with JPEG conversion.", batch_id=self.batch_id, step=6)
            
            self.convert_btn.setEnabled(True)
            
        except Exception as e:
            self.log_manager.error(f"Error during analysis: {str(e)}", batch_id=self.batch_id, step=6)
    
    def _start_conversion(self):
        """Start the JPEG conversion process."""
        self.log_manager.step_start(6, "JPEG Conversion", batch_id=self.batch_id)
        message = f"Are you sure you want to proceed with JPEG conversion?\n\n" \
                  f"Quality: {self.quality_spinbox.value()}%\n" \
                  "All metadata will be preserved."
        self.log_manager.info(f"User confirmation requested for JPEG conversion: {message}", batch_id=self.batch_id, step=6)
        reply = QMessageBox.question(
            self,
            "Confirm Conversion",
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            self.log_manager.info("User cancelled JPEG conversion.", batch_id=self.batch_id, step=6)
            return
        
        data_directory = self.config_manager.get('project.data_directory', '')
        tiff_dir = Path(data_directory) / 'output' / 'tiff_processed'
        jpeg_dir = Path(data_directory) / 'output' / 'jpeg'
        report_dir = Path(data_directory) / 'reports'
        
        # Get quality setting
        quality = self.quality_spinbox.value()
        
        # Save quality setting to config
        self.config_manager.set('step_configurations.step6.quality', quality)
        if self.config_manager.config_path:
            self.config_manager.save_config(
                self.config_manager.to_dict(),
                self.config_manager.config_path
            )
        
        # Create output directory
        jpeg_dir.mkdir(parents=True, exist_ok=True)
        
        # Disable button and show progress
        self.convert_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        
        self.log_manager.info("="*50, batch_id=self.batch_id, step=6)
        self.log_manager.info("Starting JPEG conversion...", batch_id=self.batch_id, step=6)
        
        # Start conversion thread
        self.conversion_thread = JpegConversionThread(
            str(tiff_dir), str(jpeg_dir), str(report_dir), quality
        )
        self.conversion_thread.progress.connect(self._on_progress)
        self.conversion_thread.finished.connect(self._on_finished)
        self.conversion_thread.error.connect(self._on_error)
        self.conversion_thread.start()
        
    def _on_progress(self, message):
        """Handle progress messages."""
        self.log_manager.info(message, batch_id=self.batch_id, step=6)
        
    def _on_finished(self, success, stats):
        """Handle conversion completion."""
        self.progress_bar.setVisible(False)
        self.convert_btn.setEnabled(True)
        
        if success:
            self.log_manager.success("JPEG conversion completed successfully!", batch_id=self.batch_id, step=6)
            self.log_manager.info("Summary:", batch_id=self.batch_id, step=6)
            self.log_manager.info(f"  Converted: {stats['converted']} files", batch_id=self.batch_id, step=6)
            self.log_manager.info(f"  Failed: {stats['failed']} files", batch_id=self.batch_id, step=6)
            
            # Show output directory
            data_directory = self.config_manager.get('project.data_directory', '')
            jpeg_dir = Path(data_directory) / 'output' / 'jpeg'
            self.log_manager.info(f"JPEG files saved to:\n  {jpeg_dir}", batch_id=self.batch_id, step=6)
            
            # Mark step 6 as completed
            self.config_manager.update_step_status(6, True)
            
            # Save configuration
            if self.config_manager.config_path:
                self.config_manager.save_config(
                    self.config_manager.to_dict(),
                    self.config_manager.config_path
                )
            
            self.log_manager.step_complete(6, "JPEG Conversion", batch_id=self.batch_id)
            self.log_manager.info(
                f"Step 6: Converted {stats['converted']} TIFFs to JPEG",
                batch_id=self.batch_id, step=6
            )

            message = f"JPEG conversion completed successfully!\n\n" \
                      f"Converted: {stats['converted']} files\n" \
                      f"Failed: {stats['failed']} files\n\n" \
                      f"JPEG files saved to:\n{jpeg_dir}\n\n" \
                      f"Step 6 is now marked as complete."
            self.log_manager.success(f"Conversion Complete: {message}", batch_id=self.batch_id, step=6)
            QMessageBox.information(
                self,
                "Conversion Complete",
                message
            )

            self.accept()
        else:
            self.log_manager.step_error(6, "JPEG conversion failed", batch_id=self.batch_id)
            self.log_manager.error("JPEG conversion failed.", batch_id=self.batch_id, step=6)            
    def _on_error(self, error_msg):
        """Handle conversion errors."""
        self.progress_bar.setVisible(False)
        self.convert_btn.setEnabled(True)

        self.log_manager.step_error(6, error_msg, batch_id=self.batch_id)
        
        message = f"JPEG conversion failed:\n\n{error_msg}"
        self.log_manager.critical(f"Conversion Error: {message}", batch_id=self.batch_id, step=6)
        QMessageBox.critical(
            self,
            "Conversion Error",
            message
        )
