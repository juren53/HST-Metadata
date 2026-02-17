"""
Step 7 Dialog - JPEG Resizing

Resizes JPEG files to fit within specified dimensions while maintaining aspect ratio
and preserving all metadata.
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


class JpegResizeThread(QThread):
    """Worker thread for JPEG resizing."""
    
    progress = pyqtSignal(str)  # Progress messages
    finished = pyqtSignal(bool, dict)  # Success/failure, stats dict
    error = pyqtSignal(str)  # Error messages
    
    def __init__(self, jpeg_dir, output_dir, report_dir, max_dimension, quality):
        super().__init__()
        self.jpeg_dir = jpeg_dir
        self.output_dir = output_dir
        self.report_dir = report_dir
        self.max_dimension = max_dimension
        self.quality = quality
        
    def run(self):
        """Run the JPEG resizing process."""
        try:
            from PIL import Image
            from utils.file_utils import create_exiftool_instance
            
            stats = {
                'jpeg_files_found': 0,
                'resized': 0,
                'skipped': 0,  # Already within size constraints
                'failed': 0,
                'failed_list': [],
                'size_info': []
            }
            
            self.progress.emit("Starting JPEG resizing...")
            self.progress.emit(f"Source directory: {self.jpeg_dir}")
            self.progress.emit(f"Output directory: {self.output_dir}")
            self.progress.emit(f"Max dimension: {self.max_dimension}x{self.max_dimension} px")
            self.progress.emit(f"Quality setting: {self.quality}")
            
            # Ensure output directory exists
            Path(self.output_dir).mkdir(parents=True, exist_ok=True)
            
            # Find all JPEG files
            jpeg_files = glob.glob(str(Path(self.jpeg_dir) / '*.jpg')) + \
                        glob.glob(str(Path(self.jpeg_dir) / '*.jpeg'))
            stats['jpeg_files_found'] = len(jpeg_files)
            
            if stats['jpeg_files_found'] == 0:
                self.error.emit(f"No JPEG files found in {self.jpeg_dir}")
                return
            
            self.progress.emit(f"✓ Found {stats['jpeg_files_found']} JPEG files")
            self.progress.emit("")
            self.progress.emit("Starting resize operation...")
            
            # Process each JPEG file
            for jpeg_path in jpeg_files:
                jpeg_path = Path(jpeg_path)
                output_filename = jpeg_path.name
                output_path = Path(self.output_dir) / output_filename
                
                try:
                    # Open JPEG image
                    with Image.open(jpeg_path) as img:
                        original_size = img.size
                        width, height = original_size
                        
                        # Check if image needs resizing
                        if width <= self.max_dimension and height <= self.max_dimension:
                            # Image is already within constraints, just copy with metadata
                            self.progress.emit(f"  {jpeg_path.name}: {width}x{height} (no resize needed)")
                            
                            # Extract EXIF data if present
                            exif_data = None
                            if 'exif' in img.info:
                                exif_data = img.info['exif']
                            
                            # Save as-is
                            save_kwargs = {
                                'format': 'JPEG',
                                'quality': self.quality,
                                'optimize': True
                            }
                            if exif_data:
                                save_kwargs['exif'] = exif_data
                            
                            img.save(output_path, **save_kwargs)
                            stats['skipped'] += 1
                        else:
                            # Calculate new dimensions maintaining aspect ratio
                            if width > height:
                                new_width = self.max_dimension
                                new_height = int((height / width) * self.max_dimension)
                            else:
                                new_height = self.max_dimension
                                new_width = int((width / height) * self.max_dimension)
                            
                            # Resize image using high-quality Lanczos resampling
                            resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                            
                            # Extract EXIF data if present
                            exif_data = None
                            if 'exif' in img.info:
                                exif_data = img.info['exif']
                            
                            # Save resized image
                            save_kwargs = {
                                'format': 'JPEG',
                                'quality': self.quality,
                                'optimize': True
                            }
                            if exif_data:
                                save_kwargs['exif'] = exif_data
                            
                            resized_img.save(output_path, **save_kwargs)
                            
                            self.progress.emit(f"  {jpeg_path.name}: {width}x{height} → {new_width}x{new_height}")
                            stats['resized'] += 1
                            stats['size_info'].append({
                                'filename': jpeg_path.name,
                                'original': f"{width}x{height}",
                                'resized': f"{new_width}x{new_height}"
                            })
                    
                    # Use exiftool to copy all metadata tags from source to destination
                    # This ensures IPTC and XMP metadata are fully preserved
                    with create_exiftool_instance() as et:
                        et.execute(
                            b"-TagsFromFile",
                            str(jpeg_path).encode('utf-8'),
                            b"-all:all",
                            b"-overwrite_original",
                            str(output_path).encode('utf-8')
                        )
                    
                    if (stats['resized'] + stats['skipped']) % 10 == 0:
                        self.progress.emit(f"Processed: {stats['resized'] + stats['skipped']}/{stats['jpeg_files_found']}")
                    
                except Exception as e:
                    self.progress.emit(f"⚠️  Failed: {jpeg_path.name} - {str(e)}")
                    stats['failed'] += 1
                    stats['failed_list'].append(jpeg_path.name)
            
            self.progress.emit("")
            self.progress.emit(f"✓ Resize operation complete!")
            self.progress.emit(f"✓ Resized: {stats['resized']} files")
            self.progress.emit(f"✓ Skipped (already within size): {stats['skipped']} files")
            self.progress.emit(f"✓ Failed: {stats['failed']} files")
            self.progress.emit(f"")
            self.progress.emit(f"✓ Resized JPEGs saved to: {self.output_dir}")
            
            # Generate report
            self._generate_report(stats)
            
            self.finished.emit(True, stats)
            
        except Exception as e:
            self.error.emit(f"Error during JPEG resizing: {str(e)}")
    
    def _generate_report(self, stats):
        """Generate a report file."""
        try:
            current_datetime = datetime.now()
            formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
            report_filename = f"REPORT_JPEG_RESIZE-{formatted_datetime}.txt"
            report_path = Path(self.report_dir) / report_filename
            
            # Ensure report directory exists
            Path(self.report_dir).mkdir(parents=True, exist_ok=True)
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write("=" * 70 + "\n")
                f.write("JPEG RESIZE REPORT\n")
                f.write("=" * 70 + "\n")
                f.write(f"Report generated: {current_datetime.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("\n")
                f.write(f"Source directory: {self.jpeg_dir}\n")
                f.write(f"Output directory: {self.output_dir}\n")
                f.write(f"Max dimension: {self.max_dimension}x{self.max_dimension} px\n")
                f.write(f"Quality setting: {self.quality}\n")
                f.write("\n")
                f.write("SUMMARY:\n")
                f.write("-" * 70 + "\n")
                f.write(f"JPEG files found: {stats['jpeg_files_found']}\n")
                f.write(f"Resized: {stats['resized']}\n")
                f.write(f"Skipped (already within size): {stats['skipped']}\n")
                f.write(f"Failed: {stats['failed']}\n")
                f.write("\n")
                
                if stats['size_info']:
                    f.write("RESIZE DETAILS:\n")
                    f.write("-" * 70 + "\n")
                    for info in stats['size_info']:
                        f.write(f"  {info['filename']}: {info['original']} → {info['resized']}\n")
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


class Step7Dialog(QDialog):
    """Dialog for Step 7: JPEG Resizing."""

    def __init__(self, config_manager, parent=None, batch_id=None):
        super().__init__(parent)

        self.config_manager = config_manager
        self.batch_id = batch_id
        self.resize_thread = None
        self.log_manager = get_log_manager()

        self.setWindowTitle("Step 7: JPEG Resizing")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)

        self.log_manager.debug("Opened Step 7 dialog", batch_id=batch_id, step=7)
        self._init_ui()
        self._analyze_files()
        
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Title and description
        title_label = QLabel("<h2>Step 7: JPEG Resizing</h2>")
        layout.addWidget(title_label)
        
        desc_label = QLabel(
            "<p>This step resizes JPEG files to fit within a specified box dimension "
            "while maintaining aspect ratio and preserving all metadata tags.</p>"
        )
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        layout.addSpacing(10)
        
        # Settings section
        settings_group = QGroupBox("Resize Settings")
        settings_layout = QHBoxLayout(settings_group)
        
        # Max dimension
        dimension_label = QLabel("Max Dimension:")
        settings_layout.addWidget(dimension_label)
        
        self.dimension_spinbox = QSpinBox()
        self.dimension_spinbox.setRange(100, 10000)
        self.dimension_spinbox.setValue(
            self.config_manager.get('step_configurations.step7.max_dimension', 800)
        )
        self.dimension_spinbox.setSuffix(" px")
        self.dimension_spinbox.setToolTip("Images will fit within this box size (e.g., 800x800)")
        settings_layout.addWidget(self.dimension_spinbox)
        
        settings_layout.addSpacing(20)
        
        # Quality
        quality_label = QLabel("JPEG Quality:")
        settings_layout.addWidget(quality_label)
        
        self.quality_spinbox = QSpinBox()
        self.quality_spinbox.setRange(1, 100)
        self.quality_spinbox.setValue(
            self.config_manager.get('step_configurations.step7.quality', 85)
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
        
        self.jpeg_count_label = QLabel("JPEG files: Analyzing...")
        self.resized_count_label = QLabel("Existing resized JPEGs: Analyzing...")
        
        analysis_layout.addWidget(self.jpeg_count_label)
        analysis_layout.addWidget(self.resized_count_label)
        
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
        
        self.resize_btn = QPushButton("Start Resizing")
        self.resize_btn.setDefault(True)
        self.resize_btn.setEnabled(False)
        self.resize_btn.clicked.connect(self._start_resizing)
        button_layout.addWidget(self.resize_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.reject)
        button_layout.addWidget(close_btn)
        
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
    def _analyze_files(self):
        """Analyze JPEG files before processing."""
        try:
            data_directory = self.config_manager.get('project.data_directory', '')
            if not data_directory:
                self.log_manager.warning("Error: Project data directory not set", batch_id=self.batch_id, step=7)
                return
            
            # JPEG source directory
            jpeg_dir = Path(data_directory) / 'output' / 'jpeg'
            
            # Resized JPEG output directory
            resized_dir = Path(data_directory) / 'output' / 'jpeg_resized'
            
            if not jpeg_dir.exists():
                self.log_manager.warning(f"JPEG directory not found: {jpeg_dir}", batch_id=self.batch_id, step=7)
                self.jpeg_count_label.setText("JPEG files: Directory not found")
                self.log_manager.warning("Have you completed Step 6?", batch_id=self.batch_id, step=7)
                return
            
            # Count JPEG files
            jpeg_files = glob.glob(str(jpeg_dir / '*.jpg')) + glob.glob(str(jpeg_dir / '*.jpeg'))
            jpeg_count = len(jpeg_files)
            
            self.jpeg_count_label.setText(f"JPEG files: {jpeg_count}")
            
            # Count existing resized JPEG files
            resized_files = glob.glob(str(resized_dir / '*.jpg')) + glob.glob(str(resized_dir / '*.jpeg'))
            resized_count = len(resized_files)
            
            self.resized_count_label.setText(f"Existing resized JPEGs: {resized_count}")
            
            if jpeg_count == 0:
                self.log_manager.warning("No JPEG files found for resizing", batch_id=self.batch_id, step=7)
                self.log_manager.warning("Please complete Step 6 first", batch_id=self.batch_id, step=7)
                return
            
            self.log_manager.info("File analysis complete.", batch_id=self.batch_id, step=7)
            self.log_manager.info(f"JPEG files to resize: {jpeg_count}", batch_id=self.batch_id, step=7)
            
            if resized_count > 0:
                self.log_manager.warning(f"Warning: {resized_count} resized JPEG files already exist and will be overwritten", batch_id=self.batch_id, step=7)
            
            self.log_manager.info("Ready to proceed with JPEG resizing.", batch_id=self.batch_id, step=7)
            
            self.resize_btn.setEnabled(True)
            
        except Exception as e:
            self.log_manager.error(f"Error during analysis: {str(e)}", batch_id=self.batch_id, step=7)
    
    def _start_resizing(self):
        """Start the JPEG resizing process."""
        self.log_manager.step_start(7, "JPEG Resizing", batch_id=self.batch_id)
        max_dim = self.dimension_spinbox.value()
        quality = self.quality_spinbox.value()

        message = f"Are you sure you want to proceed with JPEG resizing?\n\n" \
                  f"Max dimension: {max_dim}x{max_dim} px\n" \
                  f"Quality: {quality}%\n" \
                  "Aspect ratio will be maintained.\n" \
                  "All metadata will be preserved."
        self.log_manager.info(f"User confirmation requested for resizing: {message}", batch_id=self.batch_id, step=7)
        reply = QMessageBox.question(
            self,
            "Confirm Resizing",
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            self.log_manager.info("User cancelled JPEG resizing.", batch_id=self.batch_id, step=7)
            return
        
        data_directory = self.config_manager.get('project.data_directory', '')
        jpeg_dir = Path(data_directory) / 'output' / 'jpeg'
        resized_dir = Path(data_directory) / 'output' / 'jpeg_resized'
        report_dir = Path(data_directory) / 'reports'
        
        # Save settings to config
        self.config_manager.set('step_configurations.step7.max_dimension', max_dim)
        self.config_manager.set('step_configurations.step7.quality', quality)
        if self.config_manager.config_path:
            self.config_manager.save_config(
                self.config_manager.to_dict(),
                self.config_manager.config_path
            )
        
        # Create output directory
        resized_dir.mkdir(parents=True, exist_ok=True)
        
        # Disable button and show progress
        self.resize_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        
        self.log_manager.info("="*50, batch_id=self.batch_id, step=7)
        self.log_manager.info("Starting JPEG resizing...", batch_id=self.batch_id, step=7)
        
        # Start resize thread
        self.resize_thread = JpegResizeThread(
            str(jpeg_dir), str(resized_dir), str(report_dir), max_dim, quality
        )
        self.resize_thread.progress.connect(self._on_progress)
        self.resize_thread.finished.connect(self._on_finished)
        self.resize_thread.error.connect(self._on_error)
        self.resize_thread.start()
        
    def _on_progress(self, message):
        """Handle progress messages."""
        self.output_text.append(message)
        self.log_manager.info(message, batch_id=self.batch_id, step=7)
        
    def _on_finished(self, success, stats):
        """Handle resize completion."""
        self.progress_bar.setVisible(False)
        self.resize_btn.setEnabled(True)
        
        if success:
            self.log_manager.success("JPEG resizing completed successfully!", batch_id=self.batch_id, step=7)
            self.log_manager.info("Summary:", batch_id=self.batch_id, step=7)
            self.log_manager.info(f"  Resized: {stats['resized']} files", batch_id=self.batch_id, step=7)
            self.log_manager.info(f"  Skipped (already within size): {stats['skipped']} files", batch_id=self.batch_id, step=7)
            self.log_manager.info(f"  Failed: {stats['failed']} files", batch_id=self.batch_id, step=7)
            
            # Show output directory
            data_directory = self.config_manager.get('project.data_directory', '')
            resized_dir = Path(data_directory) / 'output' / 'jpeg_resized'
            self.log_manager.info(f"Resized JPEGs saved to:\n  {resized_dir}", batch_id=self.batch_id, step=7)
            
            # Mark step 7 as completed
            self.config_manager.update_step_status(7, True)
            
            # Save configuration
            if self.config_manager.config_path:
                self.config_manager.save_config(
                    self.config_manager.to_dict(),
                    self.config_manager.config_path
                )
            
            self.log_manager.step_complete(7, "JPEG Resizing", batch_id=self.batch_id)
            self.log_manager.info(
                f"Step 7: Resized {stats['resized']} JPEGs, skipped {stats['skipped']}",
                batch_id=self.batch_id, step=7
            )

            message = f"JPEG resizing completed successfully!\n\n" \
                      f"Resized: {stats['resized']} files\n" \
                      f"Skipped: {stats['skipped']} files\n" \
                      f"Failed: {stats['failed']} files\n\n" \
                      f"Resized JPEGs saved to:\n{resized_dir}\n\n" \
                      f"Step 7 is now marked as complete."
            self.log_manager.success(f"Resizing Complete: {message}", batch_id=self.batch_id, step=7)
            QMessageBox.information(
                self,
                "Resizing Complete",
                message
            )

            self.accept()
        else:
            self.log_manager.step_error(7, "JPEG resizing failed", batch_id=self.batch_id)
            self.log_manager.error("JPEG resizing failed.", batch_id=self.batch_id, step=7)            
    def _on_error(self, error_msg):
        """Handle resize errors."""
        self.progress_bar.setVisible(False)
        self.resize_btn.setEnabled(True)

        self.log_manager.step_error(7, error_msg, batch_id=self.batch_id)
        
        message = f"JPEG resizing failed:\n\n{error_msg}"
        self.log_manager.critical(f"Resizing Error: {message}", batch_id=self.batch_id, step=7)
        QMessageBox.critical(
            self,
            "Resizing Error",
            message
        )
