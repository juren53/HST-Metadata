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
            import exiftool
            import re
            import datetime as dt
            import shutil
            
            stats = {
                'csv_records': 0,
                'tiff_files_found': 0,
                'processed': 0,
                'missing': 0,
                'missing_list': []
            }
            
            self.progress.emit("Starting metadata embedding...")
            self.progress.emit(f"CSV file: {self.csv_path}")
            self.progress.emit(f"TIFF directory: {self.tiff_dir}")
            
            # Count CSV records
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                stats['csv_records'] = sum(1 for row in reader) - 1  # Exclude header
            
            self.progress.emit(f"✓ CSV records: {stats['csv_records']}")
            
            # Count TIFF files
            tiff_files = glob.glob(str(Path(self.tiff_dir) / '*.tif')) + \
                        glob.glob(str(Path(self.tiff_dir) / '*.tiff'))
            stats['tiff_files_found'] = len(tiff_files)
            
            self.progress.emit(f"✓ TIFF files in directory: {stats['tiff_files_found']}")
            
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
                
                with exiftool.ExifTool() as et:
                    for row in reader:
                        photo = f"{row['ObjectName']}.tif"
                        file_path = Path(self.tiff_dir) / photo
                        
                        if not file_path.exists():
                            # Try .tiff extension
                            photo = f"{row['ObjectName']}.tiff"
                            file_path = Path(self.tiff_dir) / photo
                            
                            if not file_path.exists():
                                self.progress.emit(f"⚠️  Missing: {row['ObjectName']}")
                                stats['missing'] += 1
                                stats['missing_list'].append(row['ObjectName'])
                                continue
                        
                        # Convert date
                        date_str = row.get("SpecialInstructions", "")
                        converted_date = convert_date(date_str)
                        
                        # Write metadata tags
                        file_path_str = str(file_path)
                        et.execute(b"-Headline=" + row["Headline"].encode('utf-8'), file_path_str.encode('utf-8'))
                        et.execute(b"-Credit=" + row["Credit"].encode('utf-8'), file_path_str.encode('utf-8'))
                        et.execute(b"-By-line=" + row["By-line"].encode('utf-8'), file_path_str.encode('utf-8'))
                        et.execute(b"-SpecialInstructions=" + row["SpecialInstructions"].encode('utf-8'), file_path_str.encode('utf-8'))
                        et.execute(b"-ObjectName=" + row["ObjectName"].encode('utf-8'), file_path_str.encode('utf-8'))
                        et.execute(b"-Source=" + row["Source"].encode('utf-8'), file_path_str.encode('utf-8'))
                        et.execute(b"-Caption-Abstract=" + row["Caption-Abstract"].encode('utf-8'), file_path_str.encode('utf-8'))
                        et.execute(b"-DateCreated=" + converted_date.encode('utf-8'), file_path_str.encode('utf-8'))
                        et.execute(b"-CopyrightNotice=" + row["CopyrightNotice"].encode('utf-8'), file_path_str.encode('utf-8'))
                        et.execute(b"-By-lineTitle=" + row["By-lineTitle"].encode('utf-8'), file_path_str.encode('utf-8'))
                        
                        # Remove ExifTool backup files
                        for backup_file in glob.glob(str(file_path.parent / "*_original")):
                            os.remove(backup_file)
                        
                        stats['processed'] += 1
                        
                        if stats['processed'] % 10 == 0:
                            self.progress.emit(f"Processed: {stats['processed']}")
            
            self.progress.emit(f"\n✓ Embedding complete!")
            self.progress.emit(f"✓ Processed: {stats['processed']} images")
            self.progress.emit(f"✓ Missing: {stats['missing']} images")
            
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
                f.write(f"TIFF directory: {self.tiff_dir}\n")
                f.write("\n")
                f.write("SUMMARY:\n")
                f.write("-" * 70 + "\n")
                f.write(f"Records in CSV: {stats['csv_records']}\n")
                f.write(f"TIFF files found: {stats['tiff_files_found']}\n")
                f.write(f"Images processed: {stats['processed']}\n")
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
    
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        
        self.config_manager = config_manager
        self.embedding_thread = None
        
        self.setWindowTitle("Step 5: Metadata Embedding")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
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
        self.comparison_label = QLabel("Comparison: Analyzing...")
        
        analysis_layout.addWidget(self.csv_count_label)
        analysis_layout.addWidget(self.tiff_count_label)
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
        
    def _analyze_files(self):
        """Analyze CSV and TIFF files before processing."""
        try:
            data_directory = self.config_manager.get('project.data_directory', '')
            if not data_directory:
                self.output_text.append("⚠️  Error: Project data directory not set")
                return
            
            # CSV file path
            csv_dir = Path(data_directory) / 'output' / 'csv'
            csv_path = csv_dir / 'export.csv'
            
            # TIFF directory
            tiff_dir = Path(data_directory) / 'input' / 'tiff'
            
            if not csv_path.exists():
                self.output_text.append(f"⚠️  CSV file not found: {csv_path}")
                self.csv_count_label.setText("CSV records: Not found")
                return
            
            if not tiff_dir.exists():
                self.output_text.append(f"⚠️  TIFF directory not found: {tiff_dir}")
                self.tiff_count_label.setText("TIFF files: Directory not found")
                return
            
            # Count CSV records
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                csv_count = sum(1 for row in reader) - 1  # Exclude header
            
            self.csv_count_label.setText(f"CSV records: {csv_count}")
            
            # Count TIFF files
            tiff_files = glob.glob(str(tiff_dir / '*.tif')) + glob.glob(str(tiff_dir / '*.tiff'))
            tiff_count = len(tiff_files)
            
            self.tiff_count_label.setText(f"TIFF files: {tiff_count}")
            
            # Comparison
            if csv_count == tiff_count:
                self.comparison_label.setText(f"✓ Match: {csv_count} records = {tiff_count} files")
                self.comparison_label.setStyleSheet("color: green;")
            elif tiff_count > csv_count:
                self.comparison_label.setText(f"⚠️  More TIFF files ({tiff_count}) than CSV records ({csv_count})")
                self.comparison_label.setStyleSheet("color: orange;")
            else:
                self.comparison_label.setText(f"⚠️  Fewer TIFF files ({tiff_count}) than CSV records ({csv_count})")
                self.comparison_label.setStyleSheet("color: orange;")
            
            self.output_text.append("File analysis complete.")
            self.output_text.append(f"CSV: {csv_count} records")
            self.output_text.append(f"TIFF: {tiff_count} files")
            self.output_text.append("\nReady to proceed with metadata embedding.")
            
            self.embed_btn.setEnabled(True)
            
        except Exception as e:
            self.output_text.append(f"⚠️  Error during analysis: {str(e)}")
    
    def _start_embedding(self):
        """Start the metadata embedding process."""
        reply = QMessageBox.question(
            self,
            "Confirm Embedding",
            "Are you sure you want to proceed with metadata embedding?\n\n"
            "This will write IPTC metadata tags to all TIFF files listed in the CSV.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        data_directory = self.config_manager.get('project.data_directory', '')
        csv_path = Path(data_directory) / 'output' / 'csv' / 'export.csv'
        tiff_dir = Path(data_directory) / 'input' / 'tiff'
        output_dir = Path(data_directory) / 'output' / 'tiff_processed'
        report_dir = Path(data_directory) / 'reports'
        
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Disable button and show progress
        self.embed_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        
        self.output_text.append("\n" + "="*50)
        self.output_text.append("Starting metadata embedding...")
        
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
        
    def _on_finished(self, success, stats):
        """Handle embedding completion."""
        self.progress_bar.setVisible(False)
        self.embed_btn.setEnabled(True)
        
        if success:
            self.output_text.append("\n✅ Metadata embedding completed successfully!")
            self.output_text.append(f"\nSummary:")
            self.output_text.append(f"  Processed: {stats['processed']} images")
            self.output_text.append(f"  Missing: {stats['missing']} images")
            
            # Mark step 5 as completed
            self.config_manager.update_step_status(5, True)
            
            # Save configuration
            if self.config_manager.config_path:
                self.config_manager.save_config(
                    self.config_manager.to_dict(),
                    self.config_manager.config_path
                )
            
            QMessageBox.information(
                self,
                "Embedding Complete",
                f"Metadata embedding completed successfully!\n\n"
                f"Processed: {stats['processed']} images\n"
                f"Missing: {stats['missing']} images\n\n"
                f"Step 5 is now marked as complete."
            )
            
            self.accept()
        else:
            self.output_text.append("\n❌ Metadata embedding failed.")
            
    def _on_error(self, error_msg):
        """Handle embedding errors."""
        self.progress_bar.setVisible(False)
        self.embed_btn.setEnabled(True)
        
        self.output_text.append(f"\n❌ Error: {error_msg}")
        
        QMessageBox.critical(
            self,
            "Embedding Error",
            f"Metadata embedding failed:\n\n{error_msg}"
        )
