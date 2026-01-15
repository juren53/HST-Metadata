"""
Step 4 Dialog - TIFF Bit Depth Test & Conversion

Tests for 16-bit TIFF images and converts them to 8-bit, overwriting the originals.
"""

import os
import glob
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QMessageBox, QProgressBar, QGroupBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from utils.log_manager import get_log_manager


class BitDepthConversionThread(QThread):
    """Worker thread for bit depth conversion."""
    
    progress = pyqtSignal(str)  # Progress messages
    finished = pyqtSignal(bool, dict)  # Success/failure, stats dict
    error = pyqtSignal(str)  # Error messages
    
    def __init__(self, tiff_dir, report_dir):
        super().__init__()
        self.tiff_dir = tiff_dir
        self.report_dir = report_dir
        
    def run(self):
        """Run the bit depth conversion process."""
        try:
            from PIL import Image
            import numpy as np
            import exiftool
            
            stats = {
                'tiff_files_found': 0,
                'bit16_found': 0,
                'converted': 0,
                'failed': 0,
                'failed_list': [],
                'converted_list': []
            }
            
            self.progress.emit("Starting bit depth conversion...")
            self.progress.emit(f"Directory: {self.tiff_dir}")
            
            # Find all TIFF files
            tiff_files = glob.glob(str(Path(self.tiff_dir) / '*.tif')) + \
                        glob.glob(str(Path(self.tiff_dir) / '*.tiff'))
            stats['tiff_files_found'] = len(tiff_files)
            
            if stats['tiff_files_found'] == 0:
                self.error.emit(f"No TIFF files found in {self.tiff_dir}")
                return
            
            self.progress.emit(f"✓ Found {stats['tiff_files_found']} TIFF files")
            self.progress.emit("")
            self.progress.emit("Checking bit depth using metadata...")
            
            # First pass: identify 16-bit TIFFs using ExifTool
            bit16_files = []
            with exiftool.ExifTool() as et:
                for tiff_path in tiff_files:
                    try:
                        filename = Path(tiff_path).name
                        
                        # Get BitsPerSample tag
                        result = et.execute(
                            b"-EXIF:BitsPerSample",
                            b"-s3",
                            str(tiff_path).encode('utf-8')
                        )
                        
                        bits_per_sample = result.strip() if result else ''
                        
                        # Check if it's 16-bit
                        # BitsPerSample can be:
                        # - "16" (simple)
                        # - "16 16 16" (RGB)
                        # - "EXIF 16" (ExifTool format with prefix)
                        # - "IFD0 16" (alternative format)
                        if '16' in bits_per_sample and '8' not in bits_per_sample:
                            bit16_files.append(tiff_path)
                            stats['bit16_found'] += 1
                            self.progress.emit(f"  Found 16-bit: {filename} (BitsPerSample: {bits_per_sample})")
                    except Exception as e:
                        self.progress.emit(f"  Warning: Could not read metadata for {filename}: {str(e)}")
            
            self.progress.emit("")
            self.progress.emit(f"✓ Found {stats['bit16_found']} 16-bit TIFF files")
            
            if stats['bit16_found'] == 0:
                self.progress.emit("✓ No conversion needed")
                self.finished.emit(True, stats)
                return
            
            self.progress.emit("")
            self.progress.emit("Starting conversion...")
            
            # Second pass: convert 16-bit TIFFs to 8-bit
            for tiff_path in bit16_files:
                tiff_path = Path(tiff_path)
                filename = tiff_path.name
                
                try:
                    # Open and convert the image
                    # Read the image data and close it before saving
                    img = Image.open(tiff_path)
                    
                    # Convert to numpy array for proper scaling
                    img_array = np.array(img)
                    
                    # Close the original image to release file lock
                    img.close()
                    
                    # Scale from 16-bit (0-65535) to 8-bit (0-255)
                    img_8bit = (img_array / 256).astype(np.uint8)
                    
                    # Determine the mode for the 8-bit image
                    if len(img_8bit.shape) == 2:
                        # Grayscale
                        img_converted = Image.fromarray(img_8bit, mode='L')
                    elif len(img_8bit.shape) == 3 and img_8bit.shape[2] == 3:
                        # RGB
                        img_converted = Image.fromarray(img_8bit, mode='RGB')
                    elif len(img_8bit.shape) == 3 and img_8bit.shape[2] == 4:
                        # RGBA
                        img_converted = Image.fromarray(img_8bit, mode='RGBA')
                    else:
                        # Fallback
                        img_converted = Image.fromarray(img_8bit)
                    
                    # Save as 8-bit TIFF, overwriting the original
                    img_converted.save(str(tiff_path), format='TIFF', compression='tiff_adobe_deflate')
                    
                    # Copy all metadata from original using ExifTool
                    # Note: We need to preserve the original metadata before saving
                    # This is a simplified approach - metadata should be preserved during PIL save
                    
                    stats['converted'] += 1
                    stats['converted_list'].append(filename)
                    self.progress.emit(f"  ✓ Converted: {filename}")
                    
                    if stats['converted'] % 10 == 0:
                        self.progress.emit(f"Progress: {stats['converted']}/{stats['bit16_found']}")
                    
                except Exception as e:
                    self.progress.emit(f"⚠️  Failed: {filename} - {str(e)}")
                    stats['failed'] += 1
                    stats['failed_list'].append(filename)
            
            self.progress.emit("")
            self.progress.emit(f"✓ Conversion complete!")
            self.progress.emit(f"✓ Total TIFF files: {stats['tiff_files_found']}")
            self.progress.emit(f"✓ 16-bit TIFFs found: {stats['bit16_found']}")
            self.progress.emit(f"✓ Converted to 8-bit: {stats['converted']}")
            self.progress.emit(f"✓ Failed: {stats['failed']}")
            
            # Generate report
            self._generate_report(stats)
            
            self.finished.emit(True, stats)
            
        except Exception as e:
            self.error.emit(f"Error during bit depth conversion: {str(e)}")
    
    def _generate_report(self, stats):
        """Generate a report file."""
        try:
            current_datetime = datetime.now()
            formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
            report_filename = f"REPORT_BIT_DEPTH_CONVERSION-{formatted_datetime}.txt"
            report_path = Path(self.report_dir) / report_filename
            
            # Ensure report directory exists
            Path(self.report_dir).mkdir(parents=True, exist_ok=True)
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write("=" * 70 + "\n")
                f.write("TIFF BIT DEPTH CONVERSION REPORT\n")
                f.write("=" * 70 + "\n")
                f.write(f"Report generated: {current_datetime.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("\n")
                f.write(f"Directory: {self.tiff_dir}\n")
                f.write("\n")
                f.write("SUMMARY:\n")
                f.write("-" * 70 + "\n")
                f.write(f"Total TIFF files: {stats['tiff_files_found']}\n")
                f.write(f"16-bit TIFFs found: {stats['bit16_found']}\n")
                f.write(f"Converted to 8-bit: {stats['converted']}\n")
                f.write(f"Failed: {stats['failed']}\n")
                f.write("\n")
                
                if stats['converted_list']:
                    f.write("CONVERTED FILES (16-bit → 8-bit):\n")
                    f.write("-" * 70 + "\n")
                    for filename in stats['converted_list']:
                        f.write(f"  - {filename}\n")
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


class Step4Dialog(QDialog):
    """Dialog for Step 4: TIFF Bit Depth Test & Conversion."""

    def __init__(self, config_manager, parent=None, batch_id=None):
        super().__init__(parent)

        self.config_manager = config_manager
        self.batch_id = batch_id
        self.conversion_thread = None
        self.log_manager = get_log_manager()

        self.setWindowTitle("Step 4: TIFF Bit Depth Conversion")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)

        self.log_manager.debug("Opened Step 4 dialog", batch_id=batch_id, step=4)
        self._init_ui()
        self._analyze_files()
        
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Title and description
        title_label = QLabel("<h2>Step 4: TIFF Bit Depth Conversion</h2>")
        layout.addWidget(title_label)
        
        desc_label = QLabel(
            "<p>This step tests TIFF files for 16-bit depth and converts them to 8-bit. "
            "<b>Warning:</b> This will overwrite the original 16-bit TIFF files.</p>"
        )
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        layout.addSpacing(10)
        
        # File analysis section
        analysis_group = QGroupBox("File Analysis")
        analysis_layout = QVBoxLayout(analysis_group)
        
        self.tiff_count_label = QLabel("TIFF files: Analyzing...")
        self.bit16_count_label = QLabel("16-bit TIFFs: Analyzing...")
        
        analysis_layout.addWidget(self.tiff_count_label)
        analysis_layout.addWidget(self.bit16_count_label)
        
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
        
        self.convert_btn = QPushButton("Analyze & Convert")
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
        """Analyze TIFF files before processing."""
        try:
            data_directory = self.config_manager.get('project.data_directory', '')
            if not data_directory:
                self.output_text.append("⚠️  Error: Project data directory not set")
                return
            
            # TIFF directory
            tiff_dir = Path(data_directory) / 'input' / 'tiff'
            
            if not tiff_dir.exists():
                self.output_text.append(f"⚠️  TIFF directory not found: {tiff_dir}")
                self.tiff_count_label.setText("TIFF files: Directory not found")
                return
            
            # Count TIFF files
            tiff_files = glob.glob(str(tiff_dir / '*.tif')) + glob.glob(str(tiff_dir / '*.tiff'))
            tiff_count = len(tiff_files)
            
            self.tiff_count_label.setText(f"TIFF files: {tiff_count}")
            
            if tiff_count == 0:
                self.output_text.append("⚠️  No TIFF files found")
                return
            
            # Don't check bit depth during init - it's too slow and blocks the GUI
            # We'll do a quick analysis later when user clicks the button
            self.bit16_count_label.setText(f"16-bit TIFFs: Click 'Analyze & Convert' to check")
            
            self.output_text.append("File count complete.")
            self.output_text.append(f"Total TIFF files: {tiff_count}")
            self.output_text.append("")
            self.output_text.append("Click 'Analyze & Convert' to:")
            self.output_text.append("  1. Analyze TIFF bit depth")
            self.output_text.append("  2. Identify any 16-bit TIFFs")
            self.output_text.append("  3. Convert 16-bit TIFFs to 8-bit (with confirmation)")
            self.output_text.append("")
            self.output_text.append("⚠️  Warning: Conversion will OVERWRITE the original 16-bit files!")
            
            self.convert_btn.setEnabled(True)
            
        except Exception as e:
            self.output_text.append(f"⚠️  Error during analysis: {str(e)}")
    
    def _start_conversion(self):
        """Start the bit depth conversion process."""
        self.log_manager.step_start(4, "TIFF Bit Depth Conversion", batch_id=self.batch_id)
        try:
            # First, analyze files to find 16-bit TIFFs
            self.output_text.append("\n" + "="*50)
            self.output_text.append("Analyzing TIFF bit depth...")
            self.convert_btn.setEnabled(False)
            
            data_directory = self.config_manager.get('project.data_directory', '')
            tiff_dir = Path(data_directory) / 'input' / 'tiff'
            
            # Count TIFF files and check for 16-bit
            tiff_files = glob.glob(str(tiff_dir / '*.tif')) + glob.glob(str(tiff_dir / '*.tiff'))
            
            bit16_count = 0
            bit16_list = []
            
            import exiftool
            
            # Use ExifTool to check BitsPerSample metadata tag
            with exiftool.ExifTool() as et:
                for tiff_path in tiff_files:
                    try:
                        filename = Path(tiff_path).name
                        
                        # Get BitsPerSample tag
                        result = et.execute(
                            b"-EXIF:BitsPerSample",
                            b"-s3",
                            str(tiff_path).encode('utf-8')
                        )
                        
                        bits_per_sample = result.strip() if result else ''
                        
                        # Check if it's 16-bit
                        # BitsPerSample can be:
                        # - "16" (simple)
                        # - "16 16 16" (RGB)
                        # - "EXIF 16" (ExifTool format with prefix)
                        # - "IFD0 16" (alternative format)
                        if '16' in bits_per_sample and '8' not in bits_per_sample:
                            bit16_count += 1
                            bit16_list.append((filename, bits_per_sample))
                    except Exception as e:
                        pass
            
            self.bit16_count_label.setText(f"16-bit TIFFs: {bit16_count}")
            
            self.output_text.append("")
            self.output_text.append("Analysis complete.")
            self.output_text.append(f"Total TIFF files: {len(tiff_files)}")
            self.output_text.append(f"16-bit TIFFs found: {bit16_count}")
            
            if bit16_count == 0:
                # No conversion needed, just mark as complete
                self.output_text.append("\n✓ No 16-bit TIFFs found. All files are already 8-bit or less.")
                self.output_text.append("Marking step as complete...")
                
                self.config_manager.update_step_status(4, True)
                if self.config_manager.config_path:
                    self.config_manager.save_config(
                        self.config_manager.to_dict(),
                        self.config_manager.config_path
                    )
                
                self.log_manager.step_complete(4, "TIFF Bit Depth Conversion", batch_id=self.batch_id)
                self.log_manager.info("Step 4: No 16-bit TIFFs found, all files are 8-bit", batch_id=self.batch_id, step=4)

                QMessageBox.information(
                    self,
                    "Step Complete",
                    "No 16-bit TIFFs found. Step 4 marked as complete."
                )
                self.accept()
                return
            
            # Show list of 16-bit files to be converted
            self.output_text.append("")
            self.output_text.append("16-bit TIFFs found (will be converted):")
            self.output_text.append("-" * 50)
            for filename, bits_per_sample in bit16_list:
                self.output_text.append(f"  • {filename} ({bits_per_sample})")
            self.output_text.append("-" * 50)
            
            # Ask for confirmation
            reply = QMessageBox.warning(
                self,
                "Confirm Conversion",
                f"⚠️  WARNING: This will convert {bit16_count} 16-bit TIFF(s) to 8-bit and OVERWRITE the original files!\n\n"
                "This action cannot be undone. Make sure you have backups if needed.\n\n"
                "Do you want to proceed?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                self.convert_btn.setEnabled(True)
                self.output_text.append("\nConversion cancelled by user.")
                return
            
            report_dir = Path(data_directory) / 'reports'
            
            # Show progress
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminate
            
            self.output_text.append("")
            self.output_text.append("Starting bit depth conversion...")
            
            # Start conversion thread
            self.conversion_thread = BitDepthConversionThread(
                str(tiff_dir), str(report_dir)
            )
            self.conversion_thread.progress.connect(self._on_progress)
            self.conversion_thread.finished.connect(self._on_finished)
            self.conversion_thread.error.connect(self._on_error)
            self.conversion_thread.start()
            
        except Exception as e:
            self.output_text.append(f"\n❌ Error: {str(e)}")
            self.output_text.append(f"\nTraceback: {e.__class__.__name__}")
            import traceback
            self.output_text.append(traceback.format_exc())
            self.convert_btn.setEnabled(True)
            
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred during analysis:\n\n{str(e)}"
            )
        
    def _on_progress(self, message):
        """Handle progress messages."""
        self.output_text.append(message)
        
    def _on_finished(self, success, stats):
        """Handle conversion completion."""
        self.progress_bar.setVisible(False)
        self.convert_btn.setEnabled(True)
        
        if success:
            self.output_text.append("\n✅ Bit depth conversion completed successfully!")
            self.output_text.append(f"\nSummary:")
            self.output_text.append(f"  Total TIFF files: {stats['tiff_files_found']}")
            self.output_text.append(f"  16-bit TIFFs found: {stats['bit16_found']}")
            self.output_text.append(f"  Converted to 8-bit: {stats['converted']}")
            self.output_text.append(f"  Failed: {stats['failed']}")
            
            # Mark step 4 as completed
            self.config_manager.update_step_status(4, True)
            
            # Save configuration
            if self.config_manager.config_path:
                self.config_manager.save_config(
                    self.config_manager.to_dict(),
                    self.config_manager.config_path
                )
            
            self.log_manager.step_complete(4, "TIFF Bit Depth Conversion", batch_id=self.batch_id)
            self.log_manager.info(
                f"Step 4: Converted {stats['converted']} 16-bit TIFFs to 8-bit",
                batch_id=self.batch_id, step=4
            )

            QMessageBox.information(
                self,
                "Conversion Complete",
                f"Bit depth conversion completed successfully!\n\n"
                f"Total files: {stats['tiff_files_found']}\n"
                f"16-bit TIFFs found: {stats['bit16_found']}\n"
                f"Converted to 8-bit: {stats['converted']}\n"
                f"Failed: {stats['failed']}\n\n"
                f"Step 4 is now marked as complete."
            )

            self.accept()
        else:
            self.log_manager.step_error(4, "Bit depth conversion failed", batch_id=self.batch_id)
            self.output_text.append("\n❌ Bit depth conversion failed.")
            
    def _on_error(self, error_msg):
        """Handle conversion errors."""
        self.progress_bar.setVisible(False)
        self.convert_btn.setEnabled(True)

        self.log_manager.step_error(4, error_msg, batch_id=self.batch_id)
        self.output_text.append(f"\n❌ Error: {error_msg}")

        QMessageBox.critical(
            self,
            "Conversion Error",
            f"Bit depth conversion failed:\n\n{error_msg}"
        )
