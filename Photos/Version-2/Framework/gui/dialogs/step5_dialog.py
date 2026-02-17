"""
Step 5 Dialog - Metadata Embedding

Embeds IPTC metadata into TIFF files based on export.csv data.
"""

import os
import csv
import glob
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QMessageBox, QProgressBar, QGroupBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from utils.log_manager import get_log_manager


class MetadataEmbeddingThread(QThread):
    """Worker thread for metadata embedding."""
    
    progress = pyqtSignal(str)  # Progress messages
    finished = pyqtSignal(bool, dict)  # Success/failure, stats dict
    error = pyqtSignal(str)  # Error messages
    
    def __init__(self, csv_path, tiff_dir, output_dir, report_dir):
        super().__init__()
        self.csv_path = csv_path
        self.tiff_dir = tiff_dir
        self.output_dir = output_dir
        self.report_dir = report_dir
        
    def run(self):
        """Run the metadata embedding process."""
        try:
            import re
            import datetime as dt
            import shutil
            from utils.file_utils import create_exiftool_instance
            
            stats = {
                'csv_records': 0,
                'tiff_files_found': 0,
                'processed': 0,
                'missing': 0,
                'missing_list': []
            }
            
            self.progress.emit("Starting metadata embedding...")
            self.progress.emit(f"CSV file: {self.csv_path}")
            self.progress.emit(f"TIFF source directory: {self.tiff_dir}")
            self.progress.emit(f"Output directory: {self.output_dir}")
            
            # Ensure output directory exists (defensive; UI already creates it)
            Path(self.output_dir).mkdir(parents=True, exist_ok=True)
            
            # Count CSV records with valid ObjectName (Accession Number)
            # Filter out rows without ObjectName or with artifact patterns
            artifact_patterns = {
                'ObjectName', 'Accession Number', 'Local Identifier', 
                'record.localIdentifier', 'Headline', 'Caption-Abstract',
                'Source', 'By-line', 'By-lineTitle', 'CopyrightNotice',
                'DateCreated', 'Credit', 'SpecialInstructions'
            }
            
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    obj_name = row.get('ObjectName', '').strip()
                    # Only count records with valid ObjectName
                    if obj_name and obj_name not in artifact_patterns:
                        stats['csv_records'] += 1
            
            self.progress.emit(f"✓ CSV records with Accession Numbers: {stats['csv_records']}")
            
            # Count TIFF files (in source dir)
            tiff_files = glob.glob(str(Path(self.tiff_dir) / '*.tif')) + \
                        glob.glob(str(Path(self.tiff_dir) / '*.tiff'))
            stats['tiff_files_found'] = len(tiff_files)
            
            self.progress.emit(f"✓ TIFF files in source: {stats['tiff_files_found']}")
            
            # Date conversion function from the original script
            def convert_date(date_str):
                if date_str == 'None':
                    return "0000-00-00"
                
                if re.match(r'\d{4}-\d{4}', date_str):
                    year_range = date_str.split('-')
                    return f"{year_range[1]}-00-00"
                
                elif re.match(r'\d{1,2}/\d{1,2}/\d{2}', date_str):
                    components = date_str.split('/')
                    return f"20{components[2]}-{components[0]:0>2}-{components[1]:0>2}"
                
                elif re.match(r'c\. ?\d{4}', date_str):
                    year = re.findall(r'\d{4}', date_str)[0]
                    return f"{year}-00-00"
                
                elif re.match(r"ca\. ?\d{4}", date_str):
                    year = date_str.split(".")[1].strip()
                    return f"{year}-00-00"
                
                elif re.match(r"Ca\. ?\d{4}", date_str):
                    year = date_str.split(".")[1].strip()
                    return f"{year}-00-00"
                
                elif re.match(r'\d{4}', date_str):
                    return f"{date_str}-00-00"
                
                elif re.match(r'[A-Za-z]+, \d{2}/\d{2}/\d{4}', date_str):
                    try:
                        date_object = dt.datetime.strptime(date_str, "%A, %m/%d/%Y")
                        return date_object.strftime("%Y-%m-%d")
                    except ValueError:
                        return date_str
                
                elif re.match(r'[A-Za-z]+ \d{4}', date_str):
                    try:
                        date_object = dt.datetime.strptime(date_str, "%B %Y")
                        return date_object.strftime("%Y-%m-00")
                    except ValueError:
                        return date_str
                
                elif re.match(r"([A-Za-z]+) (\d{1,2}), (\d{4})", date_str):
                    try:
                        date_object = dt.datetime.strptime(date_str, "%B %d, %Y")
                        return date_object.strftime("%Y-%m-%d")
                    except ValueError:
                        return date_str
                
                return date_str
            
            # Process each record in CSV
            self.progress.emit("\nStarting metadata embedding...")
            
            with open(self.csv_path, 'r', encoding='utf-8', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                
                # Check for required columns
                if reader.fieldnames:
                    self.progress.emit(f"CSV columns found: {', '.join(reader.fieldnames)}")
                    required_fields = ['ObjectName', 'Headline', 'CopyrightNotice', 'By-line',
                                     'Source', 'Caption-Abstract', 'By-lineTitle']
                    missing_fields = [f for f in required_fields if f not in reader.fieldnames]
                    if missing_fields:
                        self.error.emit(f"Missing required CSV columns: {', '.join(missing_fields)}\n\n"
                                      f"Expected columns: {', '.join(required_fields)}\n\n"
                                      f"Found columns: {', '.join(reader.fieldnames)}")
                        return
                
                # Create ExifTool instance with UTF-8 encoding to prevent mojibake
                with create_exiftool_instance() as et:
                    for row in reader:
                        obj_name = row.get('ObjectName', '').strip()
                        
                        # Skip rows without valid ObjectName or with artifact patterns
                        if not obj_name or obj_name in artifact_patterns:
                            continue
                        
                        photo = f"{obj_name}.tif"
                        src_path = Path(self.tiff_dir) / photo
                        
                        if not src_path.exists():
                            # Try .tiff extension
                            photo = f"{row['ObjectName']}.tiff"
                            src_path = Path(self.tiff_dir) / photo
                            
                            if not src_path.exists():
                                self.progress.emit(f"⚠️  Missing: {row['ObjectName']}")
                                stats['missing'] += 1
                                stats['missing_list'].append(row['ObjectName'])
                                continue
                        
                        # Destination path in output directory
                        dest_path = Path(self.output_dir) / photo
                        
                        try:
                            # Copy source to destination (overwrite if exists) preserving metadata/timestamps
                            shutil.copy2(src_path, dest_path)
                        except PermissionError as e:
                            self.progress.emit(f"⚠️  Cannot copy {photo}: File is locked or in use")
                            self.progress.emit(f"   Please close the file in any image viewer or other application")
                            stats['missing'] += 1
                            stats['missing_list'].append(f"{row['ObjectName']} (locked)")
                            continue
                        
                        # Convert date - DateCreated column has the date
                        date_str = row.get("DateCreated", "")
                        converted_date = convert_date(date_str) if date_str else "0000-00-00"
                        
                        # Show progress for current file
                        headline = row.get("Headline", "")[:50]  # Truncate for display
                        if len(row.get("Headline", "")) > 50:
                            headline += "..."
                        self.progress.emit(f"Processing: {photo} - {headline}")
                        
                        try:
                            # Write all metadata tags in a SINGLE command to preserve bit depth
                            # Using -overwrite_original_in_place to only update metadata without rewriting image data
                            # ExifTool instance uses UTF-8 encoding, so pass strings (not bytes)
                            # Set CodedCharacterSet to UTF8 so IPTC tags are stored as UTF-8, not Latin1
                            # Credit is always set to 'Harry S. Truman Library' regardless of CSV content
                            et.execute(
                                "-overwrite_original_in_place",
                                "-IPTC:CodedCharacterSet=UTF8",
                                f"-Headline={row.get('Headline', '')}",
                                "-Credit=Harry S. Truman Library",
                                f"-By-line={row.get('By-line', '')}",
                                f"-SpecialInstructions={row.get('SpecialInstructions', '')}",
                                f"-ObjectName={row.get('ObjectName', '')}",
                                f"-Source={row.get('Source', '')}",
                                f"-Caption-Abstract={row.get('Caption-Abstract', '')}",
                                f"-DateCreated={converted_date}",
                                f"-CopyrightNotice={row.get('CopyrightNotice', '')}",
                                f"-By-lineTitle={row.get('By-lineTitle', '')}",
                                str(dest_path)
                            )
                            
                            stats['processed'] += 1
                            self.progress.emit(f"  ✓ Embedded metadata: {photo}")
                            
                            if stats['processed'] % 10 == 0:
                                self.progress.emit(f"\n--- Progress checkpoint: {stats['processed']} files completed ---\n")
                                
                        except Exception as e:
                            self.progress.emit(f"⚠️  Failed to embed metadata in {photo}: {str(e)}")
                            if "WinError 32" in str(e) or "being used by another process" in str(e):
                                self.progress.emit(f"   File is locked - please close it in any image viewer or application")
                            stats['missing'] += 1
                            stats['missing_list'].append(f"{row['ObjectName']} (embed failed)")
            
            self.progress.emit(f"\n✓ Embedding complete!")
            self.progress.emit(f"✓ Processed (written to output): {stats['processed']} images")
            self.progress.emit(f"✓ Missing: {stats['missing']} images")
            self.progress.emit(f"\n✓ Processed TIFFs saved to: {self.output_dir}")
            
            # Generate report
            self._generate_report(stats)
            
            self.finished.emit(True, stats)
            
        except Exception as e:
            self.error.emit(f"Error during metadata embedding: {str(e)}")
    
    def _generate_report(self, stats):
        """Generate a report file."""
        try:
            current_datetime = datetime.now()
            formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
            report_filename = f"REPORT_METADATA_EMBEDDING-{formatted_datetime}.txt"
            report_path = Path(self.report_dir) / report_filename
            
            # Ensure report directory exists
            Path(self.report_dir).mkdir(parents=True, exist_ok=True)
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write("=" * 70 + "\n")
                f.write("METADATA EMBEDDING REPORT\n")
                f.write("=" * 70 + "\n")
                f.write(f"Report generated: {current_datetime.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("\n")
                f.write(f"CSV file: {self.csv_path}\n")
                f.write(f"TIFF source directory: {self.tiff_dir}\n")
                f.write(f"Output directory: {self.output_dir}\n")
                f.write("\n")
                f.write("SUMMARY:\n")
                f.write("-" * 70 + "\n")
                f.write(f"Records in CSV: {stats['csv_records']}\n")
                f.write(f"TIFF files found (source): {stats['tiff_files_found']}\n")
                f.write(f"Images processed (written to output): {stats['processed']}\n")
                f.write(f"Missing images: {stats['missing']}\n")
                f.write("\n")
                
                if stats['missing_list']:
                    f.write("MISSING IMAGES:\n")
                    f.write("-" * 70 + "\n")
                    for missing in stats['missing_list']:
                        f.write(f"  - {missing}\n")
                    f.write("\n")
                
                f.write("=" * 70 + "\n")
            
            self.progress.emit(f"✓ Report saved: {report_filename}")
            
        except Exception as e:
            self.progress.emit(f"⚠️  Failed to generate report: {str(e)}")


class Step5Dialog(QDialog):
    """Dialog for Step 5: Metadata Embedding."""

    def __init__(self, config_manager, parent=None, batch_id=None):
        super().__init__(parent)

        self.config_manager = config_manager
        self.embedding_thread = None
        self.batch_id = batch_id
        self.log_manager = get_log_manager()

        self.setWindowTitle("Step 5: Metadata Embedding")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)

        self.log_manager.info("Opened Step 5: Metadata Embedding dialog", batch_id=batch_id, step=5)
        self._init_ui()
        self._analyze_files()
        
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Title and description
        title_label = QLabel("<h2>Step 5: Metadata Embedding</h2>")
        layout.addWidget(title_label)
        
        desc_label = QLabel(
            "<p>This step embeds IPTC metadata tags into TIFF files based on the "
            "export.csv file created in Step 2.</p>"
        )
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        layout.addSpacing(10)
        
        # File analysis section
        analysis_group = QGroupBox("File Analysis")
        analysis_layout = QVBoxLayout(analysis_group)
        
        self.csv_count_label = QLabel("CSV records: Analyzing...")
        self.tiff_count_label = QLabel("TIFF files: Analyzing...")
        self.matched_label = QLabel("Matched: Analyzing...")
        self.missing_tiff_label = QLabel("Missing TIFF files: Analyzing...")
        self.comparison_label = QLabel("Status: Analyzing...")
        
        analysis_layout.addWidget(self.csv_count_label)
        analysis_layout.addWidget(self.tiff_count_label)
        analysis_layout.addWidget(self.matched_label)
        analysis_layout.addWidget(self.missing_tiff_label)
        analysis_layout.addWidget(self.comparison_label)
        
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
        
        self.report_btn = QPushButton("Generate Comparison Report")
        self.report_btn.setVisible(False)
        self.report_btn.clicked.connect(self._generate_comparison_report)
        button_layout.addWidget(self.report_btn)

        self.embed_btn = QPushButton("Proceed with Embedding")
        self.embed_btn.setDefault(True)
        self.embed_btn.setEnabled(False)
        self.embed_btn.clicked.connect(self._start_embedding)
        button_layout.addWidget(self.embed_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.reject)
        button_layout.addWidget(close_btn)
        
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Store missing files for reporting
        self.missing_tiffs = []
        self.data_directory = None

        # Store analysis results for reporting
        self.csv_object_names = []
        self.tiff_basenames = []
        
    def _generate_comparison_report(self):
        """Generate a comparison report of CSV records vs TIFF files."""
        try:
            if not self.csv_object_names and not self.tiff_basenames:
                self.log_manager.warning("No analysis data available. Please run the analysis first.", batch_id=self.batch_id, step=5)
                QMessageBox.warning(self, "No Data", "No analysis data available. Please run the analysis first.")
                return
            
            # Get report directory
            data_directory = self.config_manager.get('project.data_directory', '')
            report_dir = Path(data_directory) / 'reports'
            report_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate report filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = report_dir / f"step5_comparison_report_{timestamp}.txt"
            
            # Prepare report content
            csv_only = sorted(set(self.csv_object_names) - set(self.tiff_basenames))
            tiff_only = sorted(set(self.tiff_basenames) - set(self.csv_object_names))
            tiff_set = set(self.tiff_basenames)
            
            # Calculate column widths
            max_csv_len = max(len(name) for name in self.csv_object_names) if self.csv_object_names else 20
            col_width = max(max_csv_len, 30) + 2
            
            # Build report
            lines = []
            lines.append("="*100)
            lines.append("STEP 5 - CSV RECORDS vs TIFF FILES COMPARISON REPORT")
            lines.append("="*100)
            lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append(f"Batch: {Path(data_directory).name}")
            lines.append("")
            lines.append("NOTE: CSV records without Accession Numbers (ObjectName) are excluded.")
            lines.append("")
            lines.append(f"Total CSV Records: {len(self.csv_object_names)}")
            lines.append(f"Total TIFF Files:  {len(self.tiff_basenames)}")
            lines.append(f"Matched:           {len(set(self.csv_object_names) & set(self.tiff_basenames))}")
            lines.append(f"CSV Only:          {len(csv_only)}")
            lines.append(f"TIFF Only:         {len(tiff_only)}")
            lines.append("")
            lines.append("="*100)
            lines.append("CSV RECORDS WITH MATCHING STATUS (Sorted by Accession Number)")
            lines.append("="*100)
            lines.append(f"{'CSV Record (Accession Number)':<{col_width}} | Matching TIFF")
            lines.append("-"*100)
            
            # List CSV records with their matching status
            for csv_name in self.csv_object_names:
                if csv_name in tiff_set:
                    lines.append(f"{csv_name:<{col_width}} | {csv_name}")
                else:
                    lines.append(f"{csv_name:<{col_width}} | MISS - (no matching TIFF found)")
            
            # Extra TIFF files section
            if tiff_only:
                lines.append("")
                lines.append("="*100)
                lines.append(f"TIFF FILES WITHOUT MATCHING CSV RECORDS ({len(tiff_only)} items)")
                lines.append("="*100)
                for name in tiff_only:
                    lines.append(f"  - {name}")
            
            lines.append("")
            lines.append("="*100)
            lines.append("LEGEND")
            lines.append("="*100)
            lines.append("MISS - CSV record does NOT have a corresponding TIFF file")
            lines.append("(Records with matching TIFFs show the filename directly)")
            lines.append("")
            lines.append("="*100)
            lines.append("END OF REPORT")
            lines.append("="*100)
            
            # Write report to file
            report_content = "\n".join(lines)
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            self.log_manager.success(f"Comparison report generated: {report_path.name}", batch_id=self.batch_id, step=5)
            
            # Show report in dialog
            self._show_report_dialog(report_content, str(report_path))
            
        except Exception as e:
            self.log_manager.critical(f"Failed to generate report: {str(e)}", batch_id=self.batch_id, step=5)
            QMessageBox.critical(self, "Report Error", f"Failed to generate report:\n\n{str(e)}")
    
    def _show_report_dialog(self, report_content, report_path):
        """Display report in a dialog window."""
        dialog = QDialog(self)
        dialog.setWindowTitle("CSV vs TIFF Comparison Report")
        dialog.setMinimumSize(1100, 650)
        
        layout = QVBoxLayout(dialog)
        
        # Info label
        info_label = QLabel(f"<b>Report saved to:</b> {report_path}")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Report text
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setPlainText(report_content)
        
        # Set monospace font for proper column alignment
        from PyQt6.QtGui import QFont
        font = QFont("Courier New", 10)
        font.setStyleHint(QFont.StyleHint.Monospace)
        font.setFixedPitch(True)
        text_edit.setFont(font)
        
        layout.addWidget(text_edit)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec()
        
        
    def _analyze_files(self):
        """Analyze CSV and TIFF files before processing."""
        try:
            self.data_directory = self.config_manager.get('project.data_directory', '')
            if not self.data_directory:
                self.log_manager.warning("Error: Project data directory not set", batch_id=self.batch_id, step=5)
                return
            
            data_directory = self.data_directory
            
            # CSV file path
            csv_dir = Path(data_directory) / 'output' / 'csv'
            csv_path = csv_dir / 'export.csv'
            
            # TIFF directory
            tiff_dir = Path(data_directory) / 'input' / 'tiff'
            
            if not csv_path.exists():
                self.log_manager.warning(f"CSV file not found: {csv_path}", batch_id=self.batch_id, step=5)
                self.csv_count_label.setText("CSV records: Not found")
                return
            
            if not tiff_dir.exists():
                self.log_manager.warning(f"TIFF directory not found: {tiff_dir}", batch_id=self.batch_id, step=5)
                self.tiff_count_label.setText("TIFF files: Directory not found")
                return
            
            # Get CSV ObjectNames (filter out empty/whitespace and artifact records)
            # Artifact patterns to exclude: header names, field references, empty values
            artifact_patterns = {
                'ObjectName', 'Accession Number', 'Local Identifier', 
                'record.localIdentifier', 'Headline', 'Caption-Abstract',
                'Source', 'By-line', 'By-lineTitle', 'CopyrightNotice',
                'DateCreated', 'Credit', 'SpecialInstructions'
            }
            
            csv_object_names = []
            with open(csv_path, 'r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    obj_name = row.get('ObjectName', '').strip()
                    # Skip empty values, whitespace-only, and known artifact patterns
                    if obj_name and obj_name not in artifact_patterns:
                        csv_object_names.append(obj_name)
            
            # Store for reporting
            self.csv_object_names = sorted(csv_object_names)
            
            csv_count = len(csv_object_names)
            self.csv_count_label.setText(f"CSV records: {csv_count}")
            
            # Get TIFF filenames (without extensions)
            tiff_files = glob.glob(str(tiff_dir / '*.tif')) + glob.glob(str(tiff_dir / '*.tiff'))
            tiff_count = len(tiff_files)
            tiff_basenames = [Path(f).stem for f in tiff_files]  # Get filename without extension
            
            # Store for reporting
            self.tiff_basenames = sorted(tiff_basenames)
            
            self.tiff_count_label.setText(f"TIFF files: {tiff_count}")
            
            # Find matches and missing
            matched = [name for name in csv_object_names if name in tiff_basenames]
            missing_tiffs = [name for name in csv_object_names if name not in tiff_basenames]
            
            matched_count = len(matched)
            missing_count = len(missing_tiffs)

            # Get theme colors
            from gui.theme_manager import ThemeManager
            theme = ThemeManager.instance()
            colors = theme.get_current_colors()

            # Display matched info
            self.matched_label.setText(f"Matched: {matched_count} TIFF files match CSV records")
            self.matched_label.setStyleSheet(f"color: {colors.success};" if matched_count > 0 else "")

            # Display missing info
            if missing_count == 0:
                self.missing_tiff_label.setText("✓ All CSV records have matching TIFF files")
                self.missing_tiff_label.setStyleSheet(f"color: {colors.success};")
            else:
                self.missing_tiff_label.setText(f"⚠️  Missing TIFF files: {missing_count} CSV records have no matching TIFF")
                self.missing_tiff_label.setStyleSheet(f"color: {colors.warning};")

            # Overall status
            if csv_count == tiff_count == matched_count:
                self.comparison_label.setText(f"✓ Perfect match: All {csv_count} records have corresponding TIFF files")
                self.comparison_label.setStyleSheet(f"color: {colors.success};")
            elif matched_count == csv_count:
                self.comparison_label.setText(f"✓ All CSV records matched, but {tiff_count - matched_count} extra TIFF file(s) found")
                self.comparison_label.setStyleSheet(f"color: {colors.success};")  # Success color
            else:
                self.comparison_label.setText(f"⚠️  {matched_count} matched, {missing_count} CSV records missing TIFF files")
                self.comparison_label.setStyleSheet(f"color: {colors.warning};")
            
            self.log_manager.info("File analysis complete.", batch_id=self.batch_id, step=5)
            self.log_manager.info(f"CSV records: {csv_count}", batch_id=self.batch_id, step=5)
            self.log_manager.info(f"TIFF files: {tiff_count}", batch_id=self.batch_id, step=5)
            self.log_manager.info(f"Matched: {matched_count}", batch_id=self.batch_id, step=5)
            self.log_manager.info(f"Missing TIFF files: {missing_count}", batch_id=self.batch_id, step=5)
            
            if missing_count > 0:
                self.log_manager.info("CSV records without TIFF files:", batch_id=self.batch_id, step=5)
                for name in missing_tiffs[:10]:  # Show first 10
                    self.log_manager.info(f"  - {name}", batch_id=self.batch_id, step=5)
                if missing_count > 10:
                    self.log_manager.info(f"  ... and {missing_count - 10} more", batch_id=self.batch_id, step=5)

                # Store missing files for reporting
                self.missing_tiffs = missing_tiffs
            else:
                self.missing_tiffs = []
            
            self.log_manager.info("Ready to proceed with metadata embedding.", batch_id=self.batch_id, step=5)
            
            # Show report button after analysis
            self.report_btn.setVisible(True)
            self.embed_btn.setEnabled(True)
            
        except Exception as e:
            self.log_manager.error(f"Error during analysis: {str(e)}", batch_id=self.batch_id, step=5)
    
    def _start_embedding(self):
        """Start the metadata embedding process."""
        message = "Are you sure you want to proceed with metadata embedding?\n\n" \
                  "This will write IPTC metadata tags to all TIFF files listed in the CSV."
        self.log_manager.info(f"User confirmation requested for embedding: {message}", batch_id=self.batch_id, step=5)
        reply = QMessageBox.question(
            self,
            "Confirm Embedding",
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            self.log_manager.info("User cancelled metadata embedding.", batch_id=self.batch_id, step=5)
            return

        self.log_manager.step_start(5, "Metadata Embedding", batch_id=self.batch_id)

        data_directory = self.config_manager.get('project.data_directory', '')
        csv_path = Path(data_directory) / 'output' / 'csv' / 'export.csv'
        tiff_dir = Path(data_directory) / 'input' / 'tiff'
        output_dir = Path(data_directory) / 'output' / 'tiff_processed'
        report_dir = Path(data_directory) / 'reports'

        self.log_manager.debug(f"CSV: {csv_path}", batch_id=self.batch_id, step=5)
        self.log_manager.debug(f"TIFF dir: {tiff_dir}", batch_id=self.batch_id, step=5)
        self.log_manager.debug(f"Output dir: {output_dir}", batch_id=self.batch_id, step=5)

        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)

        # Disable button and show progress
        self.embed_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate

        self.log_manager.info("="*50, batch_id=self.batch_id, step=5)
        self.log_manager.info("Starting metadata embedding...", batch_id=self.batch_id, step=5)

        # Start embedding thread
        self.embedding_thread = MetadataEmbeddingThread(
            str(csv_path), str(tiff_dir), str(output_dir), str(report_dir)
        )
        self.embedding_thread.progress.connect(self._on_progress)
        self.embedding_thread.finished.connect(self._on_finished)
        self.embedding_thread.error.connect(self._on_error)
        self.embedding_thread.start()
        
    def _on_progress(self, message):
        """Handle progress messages."""
        self.output_text.append(message)
        self.log_manager.info(message, batch_id=self.batch_id, step=5)
        
    def _on_finished(self, success, stats):
        """Handle embedding completion."""
        self.progress_bar.setVisible(False)
        self.embed_btn.setEnabled(True)

        if success:
            self.log_manager.step_complete(5, "Metadata Embedding", batch_id=self.batch_id)
            self.log_manager.info(
                f"Metadata embedding complete: {stats['processed']} processed, {stats['missing']} missing",
                batch_id=self.batch_id, step=5
            )
            self.log_manager.success("Metadata embedding completed successfully!", batch_id=self.batch_id, step=5)
            self.log_manager.info("Summary:", batch_id=self.batch_id, step=5)
            self.log_manager.info(f"  Processed: {stats['processed']} images", batch_id=self.batch_id, step=5)
            self.log_manager.info(f"  Missing: {stats['missing']} images", batch_id=self.batch_id, step=5)
            
            # Show output directory
            data_directory = self.config_manager.get('project.data_directory', '')
            output_dir = Path(data_directory) / 'output' / 'tiff_processed'
            self.log_manager.info(f"Processed TIFFs saved to:\n  {output_dir}", batch_id=self.batch_id, step=5)
            
            # Copy verso TIFF files
            self._copy_verso_files()
            
            # Mark step 5 as completed
            self.config_manager.update_step_status(5, True)
            
            # Save configuration
            if self.config_manager.config_path:
                self.config_manager.save_config(
                    self.config_manager.to_dict(),
                    self.config_manager.config_path
                )
            
            data_directory = self.config_manager.get('project.data_directory', '')
            output_dir = Path(data_directory) / 'output' / 'tiff_processed'
            
            message = f"Metadata embedding completed successfully!\n\n" \
                      f"Processed: {stats['processed']} images\n" \
                      f"Missing: {stats['missing']} images\n\n" \
                      f"Processed TIFFs saved to:\n{output_dir}\n\n" \
                      f"Step 5 is now marked as complete."
            self.log_manager.success(f"Embedding Complete: {message}", batch_id=self.batch_id, step=5)
            QMessageBox.information(
                self,
                "Embedding Complete",
                message
            )
            
            self.accept()
        else:
            self.log_manager.step_error(5, "Metadata embedding failed", batch_id=self.batch_id)
            self.log_manager.error("Metadata embedding failed.", batch_id=self.batch_id, step=5)
            
    def _copy_verso_files(self):
        """Copy verso TIFF files to tiff_processed directory."""
        try:
            import shutil
            
            data_directory = self.config_manager.get('project.data_directory', '')
            tiff_dir = Path(data_directory) / 'input' / 'tiff'
            output_dir = Path(data_directory) / 'output' / 'tiff_processed'
            
            # Find all TIFF files containing '_verso' or '_Verso' in the filename
            verso_files = []
            for pattern in ['*_verso.tif', '*_Verso.tif', '*_verso.tiff', '*_Verso.tiff']:
                verso_files.extend(glob.glob(str(tiff_dir / pattern)))
            
            if verso_files:
                self.log_manager.info("--- Copying verso TIFF files ---", batch_id=self.batch_id, step=5)
                self.log_manager.info(f"Found {len(verso_files)} verso file(s) to copy...", batch_id=self.batch_id, step=5)
                
                copied_count = 0
                for src_path in verso_files:
                    src = Path(src_path)
                    dest = output_dir / src.name
                    
                    try:
                        shutil.copy2(src, dest)
                        self.log_manager.info(f"Copied: {src.name}", batch_id=self.batch_id, step=5)
                        copied_count += 1
                    except Exception as e:
                        self.log_manager.warning(f"Failed to copy {src.name}: {str(e)}", batch_id=self.batch_id, step=5)
                
                self.log_manager.success(f"Copied {copied_count} verso file(s) to tiff_processed directory", batch_id=self.batch_id, step=5)
            else:
                self.log_manager.info("No verso files found to copy", batch_id=self.batch_id, step=5)
                
        except Exception as e:
            self.log_manager.error(f"Error copying verso files: {str(e)}", batch_id=self.batch_id, step=5)
    
    def _on_error(self, error_msg):
        """Handle embedding errors."""
        self.progress_bar.setVisible(False)
        self.embed_btn.setEnabled(True)

        self.log_manager.step_error(5, error_msg, batch_id=self.batch_id, exc_info=True)
        
        message = f"Metadata embedding failed:\n\n{error_msg}"
        self.log_manager.critical(f"Embedding Error: {message}", batch_id=self.batch_id, step=5)
        QMessageBox.critical(
            self,
            "Embedding Error",
            message
        )
