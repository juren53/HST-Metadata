"""
Step 8 Dialog - Watermark Addition

Adds copyright watermark to JPEG files that contain 'Restricted' in their Copyright field.
"""

import os
import glob
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QMessageBox, QProgressBar, QGroupBox, QSlider, QScrollArea, QWidget
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from utils.log_manager import get_log_manager


class WatermarkThread(QThread):
    """Worker thread for watermarking."""
    
    progress = pyqtSignal(str)  # Progress messages
    finished = pyqtSignal(bool, dict)  # Success/failure, stats dict
    error = pyqtSignal(str)  # Error messages
    
    def __init__(self, jpeg_dir, output_dir, report_dir, watermark_path, opacity):
        super().__init__()
        self.jpeg_dir = jpeg_dir
        self.output_dir = output_dir
        self.report_dir = report_dir
        self.watermark_path = watermark_path
        self.opacity = opacity
        
    def run(self):
        """Run the watermarking process."""
        try:
            from PIL import Image
            import exiftool
            
            stats = {
                'jpeg_files_found': 0,
                'restricted_found': 0,
                'watermarked': 0,
                'copied_unrestricted': 0,
                'failed': 0,
                'failed_list': [],
                'restricted_list': []
            }
            
            self.progress.emit("Starting watermark process...")
            self.progress.emit(f"Source directory: {self.jpeg_dir}")
            self.progress.emit(f"Output directory: {self.output_dir}")
            self.progress.emit(f"Watermark file: {self.watermark_path}")
            self.progress.emit(f"Opacity: {self.opacity:.0%}")
            
            # Ensure output directory exists
            Path(self.output_dir).mkdir(parents=True, exist_ok=True)
            
            # Load watermark image
            try:
                watermark = Image.open(self.watermark_path).convert("RGBA")
                self.progress.emit(f"✓ Loaded watermark: {watermark.size[0]}x{watermark.size[1]} px")
            except Exception as e:
                self.error.emit(f"Failed to load watermark image: {str(e)}")
                return
            
            # Find all JPEG files
            jpeg_files = glob.glob(str(Path(self.jpeg_dir) / '*.jpg')) + \
                        glob.glob(str(Path(self.jpeg_dir) / '*.jpeg'))
            stats['jpeg_files_found'] = len(jpeg_files)
            
            if stats['jpeg_files_found'] == 0:
                self.error.emit(f"No JPEG files found in {self.jpeg_dir}")
                return
            
            self.progress.emit(f"✓ Found {stats['jpeg_files_found']} JPEG files")
            self.progress.emit("")
            self.progress.emit("Checking Copyright fields...")
            
            # Process each JPEG file
            with exiftool.ExifTool() as et:
                for jpeg_path in jpeg_files:
                    jpeg_path = Path(jpeg_path)
                    output_filename = jpeg_path.name
                    output_path = Path(self.output_dir) / output_filename
                    
                    try:
                        # Read copyright metadata using exiftool
                        # Get the raw tag value for IPTC:CopyrightNotice
                        result = et.execute(
                            b"-IPTC:CopyrightNotice",
                            b"-s3",  # Short output, values only
                            str(jpeg_path).encode('utf-8')
                        )
                        
                        # Result is already a string, not bytes
                        copyright_notice = result.strip() if result else ''
                        
                        # Debug output for first few files
                        if stats['jpeg_files_found'] <= 5:
                            self.progress.emit(f"  Debug: {jpeg_path.name} - Copyright: '{copyright_notice}'")
                        
                        # Check if 'Restricted' is in copyright notice (case-insensitive)
                        # But exclude 'Unrestricted'
                        copyright_lower = copyright_notice.lower()
                        is_restricted = ('restricted' in copyright_lower and 'unrestricted' not in copyright_lower) if copyright_notice else False
                        
                        if is_restricted:
                            stats['restricted_found'] += 1
                            stats['restricted_list'].append(jpeg_path.name)
                            
                            # Show progress for current file
                            self.progress.emit(f"Processing RESTRICTED: {jpeg_path.name} - applying watermark")
                            
                            # Apply watermark
                            with Image.open(jpeg_path) as img:
                                # Convert to RGBA for watermarking
                                if img.mode != 'RGBA':
                                    img = img.convert('RGBA')
                                
                                # Resize watermark to cover entire image
                                img_width, img_height = img.size
                                dimensions = f"{img_width}x{img_height}"
                                
                                # Scale watermark to match image size exactly
                                watermark_resized = watermark.resize(
                                    (img_width, img_height),
                                    Image.Resampling.LANCZOS
                                )
                                
                                # Adjust watermark opacity
                                watermark_with_opacity = watermark_resized.copy()
                                alpha = watermark_with_opacity.split()[3]
                                alpha = alpha.point(lambda p: int(p * self.opacity))
                                watermark_with_opacity.putalpha(alpha)
                                
                                # Position at top-left (covers entire image)
                                x = 0
                                y = 0
                                
                                # Create a transparent layer for watermark
                                watermark_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
                                watermark_layer.paste(watermark_with_opacity, (x, y), watermark_with_opacity)
                                
                                # Composite watermark onto image
                                watermarked = Image.alpha_composite(img, watermark_layer)
                                
                                # Convert back to RGB for JPEG
                                watermarked = watermarked.convert('RGB')
                                
                                # Save watermarked image
                                watermarked.save(output_path, 'JPEG', quality=95, optimize=True)
                            
                            # Copy all metadata from source to watermarked image
                            et.execute(
                                b"-TagsFromFile",
                                str(jpeg_path).encode('utf-8'),
                                b"-all:all",
                                b"-overwrite_original",
                                str(output_path).encode('utf-8')
                            )
                            
                            # Get file size for feedback
                            output_size_kb = output_path.stat().st_size / 1024
                            
                            stats['watermarked'] += 1
                            self.progress.emit(f"  ✓ Watermarked: {jpeg_path.name} ({dimensions}, {output_size_kb:.1f} KB, opacity {self.opacity:.0%})")
                        else:
                            # Not restricted, just copy the file
                            self.progress.emit(f"Processing UNRESTRICTED: {jpeg_path.name} - copying without watermark")
                            
                            with Image.open(jpeg_path) as img:
                                # Get dimensions for feedback
                                dimensions = f"{img.width}x{img.height}"
                                
                                # Extract EXIF data if present
                                exif_data = None
                                if 'exif' in img.info:
                                    exif_data = img.info['exif']
                                
                                # Save copy
                                save_kwargs = {
                                    'format': 'JPEG',
                                    'quality': 95,
                                    'optimize': True
                                }
                                if exif_data:
                                    save_kwargs['exif'] = exif_data
                                
                                img.save(output_path, **save_kwargs)
                            
                            # Copy all metadata
                            et.execute(
                                b"-TagsFromFile",
                                str(jpeg_path).encode('utf-8'),
                                b"-all:all",
                                b"-overwrite_original",
                                str(output_path).encode('utf-8')
                            )
                            
                            # Get file size for feedback
                            output_size_kb = output_path.stat().st_size / 1024
                            
                            stats['copied_unrestricted'] += 1
                            self.progress.emit(f"  ✓ Copied: {jpeg_path.name} ({dimensions}, {output_size_kb:.1f} KB)")
                        
                        if (stats['watermarked'] + stats['copied_unrestricted']) % 10 == 0:
                            self.progress.emit(f"\n--- Progress checkpoint: {stats['watermarked'] + stats['copied_unrestricted']}/{stats['jpeg_files_found']} files completed ---\n")
                        
                    except Exception as e:
                        self.progress.emit(f"⚠️  Failed: {jpeg_path.name} - {str(e)}")
                        stats['failed'] += 1
                        stats['failed_list'].append(jpeg_path.name)
            
            self.progress.emit("")
            self.progress.emit(f"✓ Watermarking process complete!")
            self.progress.emit(f"✓ Total files processed: {stats['jpeg_files_found']}")
            self.progress.emit(f"✓ Restricted images watermarked: {stats['watermarked']}")
            self.progress.emit(f"✓ Unrestricted images copied: {stats['copied_unrestricted']}")
            self.progress.emit(f"✓ Failed: {stats['failed']}")
            self.progress.emit(f"")
            self.progress.emit(f"✓ Output saved to: {self.output_dir}")
            
            # Generate report
            self._generate_report(stats)
            
            self.finished.emit(True, stats)
            
        except Exception as e:
            self.error.emit(f"Error during watermarking: {str(e)}")
    
    def _generate_report(self, stats):
        """Generate a report file."""
        try:
            current_datetime = datetime.now()
            formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
            report_filename = f"REPORT_WATERMARK-{formatted_datetime}.txt"
            report_path = Path(self.report_dir) / report_filename
            
            # Ensure report directory exists
            Path(self.report_dir).mkdir(parents=True, exist_ok=True)
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write("=" * 70 + "\n")
                f.write("WATERMARK APPLICATION REPORT\n")
                f.write("=" * 70 + "\n")
                f.write(f"Report generated: {current_datetime.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("\n")
                f.write(f"Source directory: {self.jpeg_dir}\n")
                f.write(f"Output directory: {self.output_dir}\n")
                f.write(f"Watermark file: {self.watermark_path}\n")
                f.write(f"Opacity: {self.opacity:.0%}\n")
                f.write("\n")
                f.write("SUMMARY:\n")
                f.write("-" * 70 + "\n")
                f.write(f"JPEG files found: {stats['jpeg_files_found']}\n")
                f.write(f"Restricted images found: {stats['restricted_found']}\n")
                f.write(f"Watermarked: {stats['watermarked']}\n")
                f.write(f"Copied (unrestricted): {stats['copied_unrestricted']}\n")
                f.write(f"Failed: {stats['failed']}\n")
                f.write("\n")
                
                if stats['restricted_list']:
                    f.write("RESTRICTED IMAGES (WATERMARKED):\n")
                    f.write("-" * 70 + "\n")
                    for filename in stats['restricted_list']:
                        f.write(f"  - {filename}\n")
                    f.write("\n")
                
                if stats['failed_list']:
                    f.write("FAILED PROCESSING:\n")
                    f.write("-" * 70 + "\n")
                    for failed in stats['failed_list']:
                        f.write(f"  - {failed}\n")
                    f.write("\n")
                
                f.write("=" * 70 + "\n")
            
            self.progress.emit(f"✓ Report saved: {report_filename}")
            
        except Exception as e:
            self.progress.emit(f"⚠️  Failed to generate report: {str(e)}")


class Step8Dialog(QDialog):
    """Dialog for Step 8: Watermark Addition."""

    def __init__(self, config_manager, parent=None, batch_id=None):
        super().__init__(parent)

        self.config_manager = config_manager
        self.batch_id = batch_id
        self.watermark_thread = None
        self.log_manager = get_log_manager()

        self.setWindowTitle("Step 8: Watermark Addition")
        self.setMinimumWidth(800)
        self.setMinimumHeight(500)  # Reduced from 600
        self.resize(810, 585)  # Default size (10% smaller: 900->810, 650->585)

        self.log_manager.debug("Opened Step 8 dialog", batch_id=batch_id, step=8)
        self._init_ui()
        self._analyze_files()
        
    def _init_ui(self):
        """Initialize the user interface."""
        # Main layout for dialog
        main_layout = QVBoxLayout(self)
        
        # Create scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Content widget inside scroll area
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        
        # Title and description
        title_label = QLabel("<h2>Step 8: Watermark Addition</h2>")
        layout.addWidget(title_label)
        
        desc_label = QLabel(
            "<p>This step adds a copyright watermark to JPEG files that contain "
            "'Restricted' in their Copyright field. Unrestricted images are copied "
            "without watermarks.</p>"
        )
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        layout.addSpacing(10)
        
        # Settings section
        settings_group = QGroupBox("Watermark Settings")
        settings_layout = QVBoxLayout(settings_group)
        
        # Opacity slider
        opacity_layout = QHBoxLayout()
        opacity_label = QLabel("Watermark Opacity:")
        opacity_layout.addWidget(opacity_label)
        
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(10, 100)  # 10% to 100%
        default_opacity = int(self.config_manager.get('step_configurations.step8.watermark_opacity', 0.3) * 100)
        self.opacity_slider.setValue(default_opacity)
        self.opacity_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.opacity_slider.setTickInterval(10)
        self.opacity_slider.valueChanged.connect(self._on_opacity_changed)
        opacity_layout.addWidget(self.opacity_slider)
        
        self.opacity_value_label = QLabel(f"{default_opacity}%")
        self.opacity_value_label.setMinimumWidth(50)
        opacity_layout.addWidget(self.opacity_value_label)
        
        settings_layout.addLayout(opacity_layout)
        
        # Watermark file info
        watermark_path = Path(__file__).parent.parent / 'Copyright_Watermark.png'
        watermark_info = QLabel(f"<i>Watermark file: {watermark_path.name}</i>")
        settings_layout.addWidget(watermark_info)
        
        layout.addWidget(settings_group)
        
        layout.addSpacing(10)
        
        # File analysis section
        analysis_group = QGroupBox("File Analysis")
        analysis_layout = QVBoxLayout(analysis_group)
        
        self.jpeg_count_label = QLabel("Resized JPEG files: Analyzing...")
        self.restricted_count_label = QLabel("Restricted images: Analyzing...")
        self.watermarked_count_label = QLabel("Existing watermarked files: Analyzing...")
        
        analysis_layout.addWidget(self.jpeg_count_label)
        analysis_layout.addWidget(self.restricted_count_label)
        analysis_layout.addWidget(self.watermarked_count_label)
        
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
        self.output_text.setMinimumHeight(200)  # Reduced from 250
        layout.addWidget(self.output_text)
        
        # Set the content widget to the scroll area
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
        
        # Buttons - OUTSIDE scroll area so they're always visible
        button_layout = QHBoxLayout()
        
        self.watermark_btn = QPushButton("Apply Watermarks")
        self.watermark_btn.setDefault(True)
        self.watermark_btn.setEnabled(False)
        self.watermark_btn.clicked.connect(self._start_watermarking)
        button_layout.addWidget(self.watermark_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.reject)
        button_layout.addWidget(close_btn)
        
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)
        
    def _on_opacity_changed(self, value):
        """Handle opacity slider change."""
        self.opacity_value_label.setText(f"{value}%")
        
    def _analyze_files(self):
        """Analyze JPEG files before processing."""
        try:
            data_directory = self.config_manager.get('project.data_directory', '')
            if not data_directory:
                self.output_text.append("⚠️  Error: Project data directory not set")
                return
            
            # Resized JPEG source directory
            jpeg_dir = Path(data_directory) / 'output' / 'jpeg_resized'
            
            # Watermarked JPEG output directory
            watermarked_dir = Path(data_directory) / 'output' / 'jpeg_watermarked'
            
            if not jpeg_dir.exists():
                self.output_text.append(f"⚠️  Resized JPEG directory not found: {jpeg_dir}")
                self.jpeg_count_label.setText("Resized JPEG files: Directory not found")
                self.output_text.append("⚠️  Have you completed Step 7?")
                return
            
            # Count JPEG files
            jpeg_files = glob.glob(str(jpeg_dir / '*.jpg')) + glob.glob(str(jpeg_dir / '*.jpeg'))
            jpeg_count = len(jpeg_files)
            
            self.jpeg_count_label.setText(f"Resized JPEG files: {jpeg_count}")
            
            if jpeg_count == 0:
                self.output_text.append("⚠️  No resized JPEG files found for watermarking")
                self.output_text.append("⚠️  Please complete Step 7 first")
                return
            
            # Check for restricted images
            self.output_text.append("Analyzing copyright fields...")
            restricted_count = 0
            restricted_list = []
            
            import exiftool
            with exiftool.ExifTool() as et:
                for jpeg_path in jpeg_files:
                    try:
                        filename = Path(jpeg_path).name
                        
                        # Get copyright notice
                        result = et.execute(
                            b"-IPTC:CopyrightNotice",
                            b"-s3",
                            str(jpeg_path).encode('utf-8')
                        )
                        # Result is already a string, not bytes
                        copyright_notice = result.strip() if result else ''
                        
                        # Debug output for all files
                        self.output_text.append(f"  {filename}: Copyright='{copyright_notice}' (len={len(copyright_notice)})")
                        
                        # Check for 'Restricted' but exclude 'Unrestricted'
                        copyright_lower = copyright_notice.lower()
                        if copyright_notice and 'restricted' in copyright_lower and 'unrestricted' not in copyright_lower:
                            restricted_count += 1
                            restricted_list.append(filename)
                            self.output_text.append(f"    -> MATCH: This file is restricted!")
                    except Exception as e:
                        self.output_text.append(f"  {Path(jpeg_path).name}: Error reading metadata: {str(e)}")
            
            self.restricted_count_label.setText(f"Restricted images: {restricted_count}")
            
            # Count existing watermarked files
            watermarked_files = glob.glob(str(watermarked_dir / '*.jpg')) + glob.glob(str(watermarked_dir / '*.jpeg'))
            watermarked_count = len(watermarked_files)
            
            self.watermarked_count_label.setText(f"Existing watermarked files: {watermarked_count}")
            
            self.output_text.append("File analysis complete.")
            self.output_text.append(f"Total JPEG files: {jpeg_count}")
            self.output_text.append(f"Restricted images found: {restricted_count}")
            
            if restricted_count > 0:
                self.output_text.append(f"\nRestricted images to be watermarked:")
                for filename in restricted_list[:10]:  # Show first 10
                    self.output_text.append(f"  - {filename}")
                if len(restricted_list) > 10:
                    self.output_text.append(f"  ... and {len(restricted_list) - 10} more")
            else:
                self.output_text.append("⚠️  No restricted images found. All images will be copied without watermarks.")
            
            if watermarked_count > 0:
                self.output_text.append(f"\n⚠️  Warning: {watermarked_count} watermarked files already exist and will be overwritten")
            
            self.output_text.append("\nReady to proceed with watermarking.")
            
            self.watermark_btn.setEnabled(True)
            
        except Exception as e:
            self.output_text.append(f"⚠️  Error during analysis: {str(e)}")
    
    def _start_watermarking(self):
        """Start the watermarking process."""
        self.log_manager.step_start(8, "Watermark Addition", batch_id=self.batch_id)
        opacity = self.opacity_slider.value() / 100.0

        reply = QMessageBox.question(
            self,
            "Confirm Watermarking",
            f"Are you sure you want to proceed with watermarking?\n\n"
            f"Opacity: {self.opacity_slider.value()}%\n\n"
            "Watermarks will be applied only to images with 'Restricted' in the Copyright field.\n"
            "All other images will be copied without watermarks.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        data_directory = self.config_manager.get('project.data_directory', '')
        jpeg_dir = Path(data_directory) / 'output' / 'jpeg_resized'
        watermarked_dir = Path(data_directory) / 'output' / 'jpeg_watermarked'
        report_dir = Path(data_directory) / 'reports'
        
        # Watermark file path
        watermark_path = Path(__file__).parent.parent / 'Copyright_Watermark.png'
        
        if not watermark_path.exists():
            QMessageBox.critical(
                self,
                "Watermark Not Found",
                f"Watermark file not found:\n\n{watermark_path}\n\n"
                "Please ensure the watermark file exists."
            )
            return
        
        # Save opacity setting to config
        self.config_manager.set('step_configurations.step8.watermark_opacity', opacity)
        if self.config_manager.config_path:
            self.config_manager.save_config(
                self.config_manager.to_dict(),
                self.config_manager.config_path
            )
        
        # Create output directory
        watermarked_dir.mkdir(parents=True, exist_ok=True)
        
        # Disable button and show progress
        self.watermark_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        
        self.output_text.append("\n" + "="*50)
        self.output_text.append("Starting watermark process...")
        
        # Start watermark thread
        self.watermark_thread = WatermarkThread(
            str(jpeg_dir), str(watermarked_dir), str(report_dir), 
            str(watermark_path), opacity
        )
        self.watermark_thread.progress.connect(self._on_progress)
        self.watermark_thread.finished.connect(self._on_finished)
        self.watermark_thread.error.connect(self._on_error)
        self.watermark_thread.start()
        
    def _on_progress(self, message):
        """Handle progress messages."""
        self.output_text.append(message)
        
    def _on_finished(self, success, stats):
        """Handle watermarking completion."""
        self.progress_bar.setVisible(False)
        self.watermark_btn.setEnabled(True)
        
        if success:
            self.output_text.append("\n✅ Watermarking process completed successfully!")
            self.output_text.append(f"\nSummary:")
            self.output_text.append(f"  Total files processed: {stats['jpeg_files_found']}")
            self.output_text.append(f"  Restricted images watermarked: {stats['watermarked']}")
            self.output_text.append(f"  Unrestricted images copied: {stats['copied_unrestricted']}")
            self.output_text.append(f"  Failed: {stats['failed']}")
            
            # Show output directory
            data_directory = self.config_manager.get('project.data_directory', '')
            watermarked_dir = Path(data_directory) / 'output' / 'jpeg_watermarked'
            self.output_text.append(f"\n✓ Output saved to:\n  {watermarked_dir}")
            
            # Mark step 8 as completed
            self.config_manager.update_step_status(8, True)
            
            # Save configuration
            if self.config_manager.config_path:
                self.config_manager.save_config(
                    self.config_manager.to_dict(),
                    self.config_manager.config_path
                )
            
            self.log_manager.step_complete(8, "Watermark Addition", batch_id=self.batch_id)
            self.log_manager.info(
                f"Step 8: Watermarked {stats['watermarked']} restricted, copied {stats['copied_unrestricted']} unrestricted",
                batch_id=self.batch_id, step=8
            )

            QMessageBox.information(
                self,
                "Watermarking Complete",
                f"Watermarking process completed successfully!\n\n"
                f"Total processed: {stats['jpeg_files_found']} files\n"
                f"Watermarked (restricted): {stats['watermarked']} files\n"
                f"Copied (unrestricted): {stats['copied_unrestricted']} files\n"
                f"Failed: {stats['failed']} files\n\n"
                f"Output saved to:\n{watermarked_dir}\n\n"
                f"Step 8 is now marked as complete."
            )

            self.accept()
        else:
            self.log_manager.step_error(8, "Watermarking process failed", batch_id=self.batch_id)
            self.output_text.append("\n❌ Watermarking process failed.")
            
    def _on_error(self, error_msg):
        """Handle watermarking errors."""
        self.progress_bar.setVisible(False)
        self.watermark_btn.setEnabled(True)

        self.log_manager.step_error(8, error_msg, batch_id=self.batch_id)
        self.output_text.append(f"\n❌ Error: {error_msg}")

        QMessageBox.critical(
            self,
            "Watermarking Error",
            f"Watermarking process failed:\n\n{error_msg}"
        )
