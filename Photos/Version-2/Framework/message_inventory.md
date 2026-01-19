# Message Inventory

This document catalogs the locations of success, error, warning, and informational messages within the HSTL Photo Framework.

## `hstl_framework.py`

| Line | Type    | Message                                                              |
|------|---------|----------------------------------------------------------------------|
| 37   | Error   | `f"Error importing framework modules: {e}"`                          |
| 38   | Print   | Banner printing                                                      |
| 66   | Info    | Sets logging level from config                                       |
| 76   | Info    | "HSTL Framework initialized successfully"                          |
| 77   | Info    | "HSTL Framework initialized successfully"                          |
| 81   | Error   | `f"Failed to initialize framework: {e}"`                             |
| 84   | Print   | `f"Failed to initialize framework: {e}"`                             |
| 94   | Info    | `f"Creating data directory: {data_dir}"`                             |
| 95   | Print   | `f"Creating data directory: {data_dir}"`                             |
| 114  | Warning | "Project configuration already exists..."                          |
| 117  | Print   | `f"Project configuration already exists: {config_path}"`             |
| 118  | Print   | "Use --force to overwrite existing configuration"                  |
| 133  | Info    | `f"Project '{project_name}' initialized successfully"`              |
| 134  | Print   | `f"Project '{project_name}' initialized successfully"`              |
| 135  | Print   | `f"Data directory: {data_dir}"`                                      |
| 136  | Print   | `f"Configuration: {config_path}"`                                    |
| 137  | Print   | `f"Batch registered in framework registry"`                           |
| 142  | Error   | `f"Failed to initialize project: {e}"`                               |
| 143  | Print   | `f"Failed to initialize project: {e}"`                               |
| 167  | Print   | "❌ No project initialized. Run 'hstl_framework.py init' first."  |
| 170  | Print   | "📊 HSTL Framework Status"                                        |
| 176  | Print   | `f"🔹 Project: {project_name}"`                                    |
| 177  | Print   | `f"🔹 Data Directory: {data_dir}"`                                 |
| 181  | Print   | "📋 Processing Steps:"                                           |
| 188  | Print   | `f"  Step {step_num}: {step_name} - {status}"`                      |
| 191  | Print   | "\n🔧 Configuration Details:"                                    |
| 213  | Error   | "No project initialized"                                           |
| 214  | Print   | "No project initialized. Run 'hstl_framework.py init' first."      |
| 218  | Info    | `f"{mode} steps: {steps}"`                                           |
| 219  | Print   | `f"{mode} steps: {steps}"`                                           |
| 223  | Error   | `f"Invalid step number: {step_num}"`                                 |
| 224  | Print   | `f"Invalid step number: {step_num}"`                                 |
| 229  | Info    | `f"Would run Step {step_num}: {step_name}"`                           |
| 230  | Print   | `f"Would run Step {step_num}: {step_name}"`                           |
| 233  | Print   | `f"Running Step {step_num}: {step_name}"`                             |
| 235  | Warning | `f"Step {step_num} implementation pending"`                           |
| 236  | Print   | `f"Step {step_num} implementation pending"`                           |
| 243  | Print   | "❌ No project initialized. Run 'hstl_framework.py init' first."  |
| 247  | Print   | "🔍 Running pre-flight validation..."                             |
| 249  | Print   | "✅ Pre-flight validation completed"                              |
| 253  | Print   | `f"🔍 Validating Step {step}: {self._get_step_name(step)}"`         |
| 255  | Print   | `f"✅ Step {step} validation completed"                           |
| 257  | Print   | "🔍 Validating entire project..."                                |
| 259  | Print   | "✅ Project validation completed"                                 |
| 266  | Print   | "❌ No project initialized. Run 'hstl_framework.py init' first."  |
| 269  | Print   | "⚙️  Current Configuration"                                       |
| 278  | Print   | `f"\n📄 Configuration file: {self.config_manager.config_path}"`      |
| 308  | Print   | `f"✅ Configuration updated: {key} = {converted_value}"`            |
| 315  | Print   | `f"💾 Saved to: {self.config_manager.config_path}"`                  |
| 319  | Print   | `f"❌ Failed to set configuration: {key}"`                         |
| 358  | Print   | "⚠️  No batches found"                                           |
| 360  | Print   | "Use 'batches --all' to see archived batches"                      |
| 363  | Print   | `f"📋 {title}"`                                                    |
| 383  | Print   | `f"{status_icon} {name} ({batch_id})"`                              |
| 384  | Print   | `f"Progress: {completed}/{total} steps ({percentage:.0f}%)"`         |
| 385  | Print   | `f"Status: {status}"`                                                |
| 386  | Print   | `f"Data Directory: {batch['data_directory']}"`                       |
| 387  | Print   | `f"Config: {batch['config_path']}"`                                  |
| 390  | Print   | `f"Total: {len(batches)} batch(es)"`                                 |
| 399  | Print   | `f"❌ Batch not found: {batch_id}"`                               |
| 403  | Print   | `f"✅ Batch '{batch['name']}' archived successfully"`             |
| 408  | Print   | `f"❌ Failed to archive batch: {batch_id}"`                        |
| 417  | Print   | `f"❌ Batch not found: {batch_id}"`                               |
| 421  | Print   | `f"✅ Batch '{batch['name']}' marked as completed"`                 |
| 426  | Print   | `f"❌ Failed to mark batch as completed: {batch_id}"`              |
| 435  | Print   | `f"❌ Batch not found: {batch_id}"`                               |
| 440  | Print   | `f"✅ Batch '{batch['name']}' reactivated"`                        |
| 445  | Print   | `f"❌ Failed to reactivate batch: {batch_id}"`                      |
| 454  | Print   | `f"❌ Batch not found: {batch_id}"`                               |
| 458  | Print   | `f"⚠️  Remove batch '{batch['name']}' from registry?"`            |
| 463  | Print   | "⚠️  This will remove the batch from the registry."               |
| 464  | Print   | "The data directory and all files will NOT be deleted."            |
| 466  | Print   | "Run with --confirm to proceed:"                                   |
| 471  | Print   | `f"✅ Batch '{batch['name']}' removed from registry"`             |
| 475  | Print   | `f"❌ Failed to remove batch: {batch_id}"`                         |
| 478  | Info    | "Show detailed information about a batch"                          |
| 484  | Print   | `f"❌ Batch not found: {batch_id}"`                               |
| 487  | Print   | "📋 Batch Information"                                          |
| 489  | Print   | `f"Name: {summary['name']}"`                                         |
| 490  | Print   | `f"Batch ID: {batch_id}"`                                            |
| 491  | Print   | `f"Status: {summary.get('status', 'unknown')}"`                      |
| 493  | Print   | `f"Created: {summary.get('created', 'unknown')}"`                    |
| 494  | Print   | `f"Last Accessed: {summary.get('last_accessed', 'unknown')}"`        |
| 496  | Print   | `f"Data Directory: {summary['data_directory']}"`                     |
| 497  | Print   | `f"Config File: {summary['config_path']}"`                           |
| 503  | Print   | "Step Status:"                                                     |
| 522  | Print   | `f"  {status_icon} Step {step_num}: {step_name}"`                    |
| 708  | Print   | `parser.print_help()`                                                |
| 760  | Print   | "⚠️  Continue functionality not yet implemented"                 |
| 774  | Print   | `parser.print_help()`                                                |
| 785  | Print   | `parser.print_help()`                                                |
| 801  | Print   | `parser.print_help()`                                                |
| 805  | Print   | `parser.print_help()`                                                |
| 811  | Print   | "\n⚠️  Operation cancelled by user"                              |
| 814  | Print   | `f"❌ Unexpected error: {e}"`                                     |
| 818  | Print   | `traceback.print_exc()`                                              |

## `core/pipeline.py`

| Line | Type    | Message                                                                |
|------|---------|------------------------------------------------------------------------|
| 17   | Success | `self.success = True`                                                  |
| 20   | Error   | `self.error_message = None`                                            |
| 25   | Success | `if result.success:`                                                   |
| 28   | Success | `self.success = False`                                                 |
| 29   | Error   | `if not self.error_message:`                                           |
| 30   | Error   | `self.error_message = f"Step {step_num} failed: {result.message}"`     |
| 60   | Info    | `f"🚀 {'Dry run' if dry_run else 'Starting'} pipeline: steps {start_step}-{end_step}"` |
| 64   | Warning | `f"Step {step_num} not registered, skipping"`                           |
| 70   | Info    | `f"✅ Would run {step}"`                                               |
| 77   | Success | `if not step_result.success:`                                          |
| 78   | Error   | `f"Pipeline stopped at step {step_num}"`                               |
| 82   | Error   | `error_msg = f"Pipeline failed at step {step_num}: {str(e)}"`          |
| 83   | Error   | `self.logger.error(error_msg, exc_info=True)`                          |
| 84   | Success | `result.success = False`                                                  |
| 85   | Error   | `result.error_message = error_msg`                                     |
| 88   | Success | `if result.success:`                                                   |
| 89   | Info    | "🎉 Pipeline completed successfully"                                 |
| 91   | Error   | `f"❌ Pipeline failed: {result.error_message}"`                        |

## `steps/base_step.py`

| Line | Type    | Message                                                              |
|------|---------|----------------------------------------------------------------------|
| 21   | Success | `success: bool`                                                      |
| 94   | Info    | `StepResult indicating success or failure`                           |
| 99   | Error   | `return StepResult(False, f"Failed to setup Step {self.step_number}")` |
| 101  | Info    | `f"🔄 Starting Step {self.step_number}: {self.step_name}"`          |
| 107  | Error   | `error_msg = f"Input validation failed: {'; '.join(input_validation.errors)}"` |
| 108  | Error   | `self.logger.error(error_msg)`                                       |
| 109  | Error   | `return StepResult(False, error_msg)`                                |
| 111  | Warning | `# Log any warnings`                                                 |
| 112  | Warning | `for warning in input_validation.warnings:`                          |
| 113  | Warning | `self.logger.warning(f"Input validation warning: {warning}")`         |
| 118  | Success | `if not result.success:`                                             |
| 119  | Error   | `self.logger.error(f"Step execution failed: {result.message}")`      |
| 125  | Error   | `error_msg = f"Output validation failed: {'; '.join(output_validation.errors)}"`|
| 126  | Error   | `self.logger.error(error_msg)`                                       |
| 127  | Error   | `return StepResult(False, error_msg)`                                |
| 129  | Warning | `# Log any output warnings`                                          |
| 130  | Warning | `for warning in output_validation.warnings:`                         |
| 131  | Warning | `self.logger.warning(f"Output validation warning: {warning}")`        |
| 136  | Info    | `f"✅ Step {self.step_number} completed successfully"`              |
| 140  | Error   | `error_msg = f"Step {self.step_number} failed with exception: {str(e)}"` |
| 141  | Error   | `self.logger.error(error_msg, exc_info=True)`                        |
| 142  | Error   | `return StepResult(False, error_msg)`                                |

## `gui/dialogs/step1_dialog.py`

| Line | Type    | Message                                                              |
|------|---------|----------------------------------------------------------------------|
| 144  | Warning | "Step 1: Excel file is required but was empty"                     |
| 149  | Warning | "File Required", "Please select an Excel spreadsheet file."
| 156  | Warning | `f"Step 1: Invalid file format - {source_path}"`                     |
| 161  | Warning | "Invalid File Format", "Please select an Excel file with .xlsx or .xls extension."
| 171  | Error   | "Step 1: No data directory found"
| 176  | Critical| "Configuration Error", "No project data directory found..."
| 200  | Warning | `f"Step 1: Excel validation failed - {message}"`                     |
| 207  | Critical| "Validation Error", `f"The selected Excel file is not valid..."`    |
| 220  | Error   | `if not success:`                                                    |
| 221  | Error   | `f"Step 1: File copy failed - {message}"`                            |
| 227  | Critical| "File Copy Error", `f"Failed to copy Excel file..."`                |
| 231  | Success | `Success!`                                                           |
| 234  | Info    | "Excel file successfully validated and copied!"
| 260  | Info    | "Step 1: Excel file processed successfully"
| 266  | Info    | "Step 1 Complete", `f"Excel spreadsheet processed successfully..."` 
| 277  | Error   | "Step 1: No config file path found"
| 280  | Warning | "Save Error", "Could not save configuration: No config file path found."
| 288  | Error   | `f"Failed to process Excel file:\n{str(e)}"`                         |
| 292  | Critical| "Error", `f"Failed to process Excel file:\n{str(e)}"`                |

## `gui/dialogs/step2_dialog.py`

| Line | Type    | Message                                                              |
|------|---------|----------------------------------------------------------------------|
| 27   | Success | `finished = pyqtSignal(bool)`                                        |
| 28   | Error   | `error = pyqtSignal(str)`                                            |
| 64   | Error   | `except ImportError as e:`                                           |
| 66   | Error   | `self.error.emit(f"Failed to import g2c module: {e}")`               |
| 74   | Error   | `self.error.emit("Failed to read Excel file")`                       |
| 83   | Success | `success = export_to_csv(df, self.output_path)`                      |
| 85   | Success | `if success:`                                                        |
| 86   | Info    | `self.progress.emit("✓ CSV export completed successfully")`          |
| 89   | Error   | `self.error.emit("CSV export failed")`                               |
| 92   | Error   | `self.error.emit(f"Error during conversion: {str(e)}")`              |
| 197  | Warning | "⚠️ Warning: Excel file is not set. Please complete Step 1 first."
| 212  | Warning | "Missing Excel File", "Excel file is not set. Please complete Step 1 first."
| 241  | Success | `def _on_finished(self, success):`                                   |
| 246  | Success | `if success:`                                                        |
| 256  | Info    | "\n✅ CSV conversion completed successfully!"                      |
| 283  | Error   | `f"Error adding batch title to CSV: {e}"`                            |
| 289  | Error   | `def _on_error(self, error_msg):`                                    |
| 293  | Error   | `f"\n❌ Error: {error_msg}"`                                         |
| 311  | Error   | `f"Error getting Excel paths: {e}"`                                  |

## `gui/dialogs/step3_dialog.py`

| Line | Type    | Message                                                              |
|------|---------|----------------------------------------------------------------------|
| 24   | Success | `finished = pyqtSignal(bool, list)`                                  |
| 25   | Error   | `error = pyqtSignal(str)`                                            |
| 80   | Error   | "ftfy library not found. Install with: pip install ftfy"
| 81   | Error   | `self.error.emit(...)`                                               |
| 83   | Error   | `self.error.emit(f"Error during mojibake detection: {str(e)}")`      |
| 174  | Info    | `self.record_info_label = QLabel()`                                  |
| 231  | Warning | "Error", "Project data directory not set"
| 237  | Warning | "Error", `f"CSV file not found: {csv_path}"`                         |
| 259  | Success | `def _on_scan_finished(self, success, problematic_records):`         |
| 264  | Info    | `if not success:`                                                    |
| 292  | Info    | "Step 3: No mojibake detected"
| 294  | Info    | "Scan Complete", "No mojibake detected in the CSV file.\n\nStep 3 is now marked as complete."
| 303  | Error   | `def _on_error(self, error_msg):`                                    |
| 308  | Error   | `f"\n❌ Error: {error_msg}"`                                         |
| 311  | Critical| "Scan Error", `f"Mojibake scan failed:\n\n{error_msg}"`             |
| 326  | Info    | `self.record_info_label.setText(...)`                                |
| 393  | Info    | "Suggestion Accepted", `f"Suggested fix for '{field}' in row {row_num} will be applied."` |
| 415  | Info    | "Custom Edit Saved", `f"Your custom fix for '{field}' in row {row_num} will be applied."` |
| 470  | Info    | `f"Step 3: Applied {len(self.edits)} mojibake fix(es)"`             |
| 472  | Info    | "Fixes Applied", `f"Successfully applied {len(self.edits)} fix(es) to the CSV file.\n\nStep 3 is now marked as complete."` |
| 482  | Error   | `f"Failed to apply fixes:\n\n{str(e)}"`                              |
| 485  | Critical| "Error", `f"Failed to apply fixes:\n\n{str(e)}"`                     |
| 509  | Info    | "Step 3: Skipped mojibake fixes"
| 553  | Warning | `f"\n⚠️  Failed to generate report: {str(e)}"`                        |

## `gui/dialogs/step4_dialog.py`

| Line | Type    | Message                                                              |
|------|---------|----------------------------------------------------------------------|
| 33   | Success | `finished = pyqtSignal(bool, dict)`                                  |
| 34   | Error   | `error = pyqtSignal(str)`                                            |
| 52   | Error   | `failed: 0,`                                                         |
| 53   | Error   | `failed_list: [],`                                                   |
| 67   | Error   | `self.error.emit(f"No TIFF files found in {self.tiff_dir}")`         |
| 104  | Warning | `f"Warning: Could not read metadata for {filename}: {str(e)}"`      |
| 170  | Warning | `f"⚠️  Failed: {filename} - {str(e)}"`                               |
| 171  | Error   | `stats["failed"] += 1`                                               |
| 172  | Error   | `stats["failed_list"].append(filename)`                              |
| 179  | Info    | `f"✓ Failed: {stats['failed']}"`                                     |
| 187  | Error   | `self.error.emit(f"Error during bit depth conversion: {str(e)}")`    |
| 215  | Error   | `f.write(f"Failed: {stats['failed']}\n")`                            |
| 225  | Error   | `if stats["failed_list"]:`                                           |
| 226  | Error   | `f.write("FAILED CONVERSIONS:\n")`                                   |
| 228  | Error   | `for failed in stats["failed_list"]:`                                |
| 229  | Error   | `f.write(f"  - {failed}\n")`                                         |
| 237  | Warning | `self.progress.emit(f"⚠️  Failed to generate report: {str(e)}")`      |
| 269  | Warning | "<b>Warning:</b> This will overwrite the original 16-bit TIFF files.</p>"
| 332  | Error   | "⚠️  Error: Project data directory not set"                        |
| 372  | Warning | "⚠️  Warning: Conversion will OVERWRITE the original 16-bit files!"
| 378  | Warning | `f"⚠️  Error during analysis: {str(e)}"`                              |
| 454  | Info    | "Step 4: No 16-bit TIFFs found, all files are 8-bit"
| 460  | Info    | "Step Complete", "No 16-bit TIFFs found. Step 4 marked as complete."
| 477  | Warning | "Confirm Conversion", `f"⚠️  WARNING: This will convert {bit16_count} 16-bit TIFF(s) to 8-bit and OVERWRITE the original files!\n\nThis action cannot be undone. Make sure you have backups if needed.\n\nDo you want to proceed?"` |
| 507  | Error   | `self.conversion_thread.error.connect(self._on_error)`               |
| 511  | Error   | `f"\n❌ Error: {str(e)}"`                                             |
| 519  | Critical| "Error", `f"An error occurred during analysis:\n\n{str(e)}"`         |
| 526  | Success | `def _on_finished(self, success, stats):`                            |
| 531  | Info    | `if success:`                                                        |
| 532  | Info    | "\n✅ Bit depth conversion completed successfully!"                 |
| 537  | Info    | `f"  Failed: {stats['failed']}"`                                     |
| 551  | Info    | `f"Step 4: Converted {stats['converted']} 16-bit TIFFs to 8-bit"`    |
| 557  | Info    | "Conversion Complete", `f"Bit depth conversion completed successfully!\n\nTotal files: {stats['tiff_files_found']}\n16-bit TIFFs found: {stats['bit16_found']}\nConverted to 8-bit: {stats['converted']}\nFailed: {stats['failed']}\n\nStep 4 is now marked as complete."` |
| 564  | Info    | `f"Failed: {stats['failed']}\n\n"`                                   |
| 570  | Error   | "Bit depth conversion failed"                                      |
| 571  | Error   | `4, "Bit depth conversion failed", batch_id=self.batch_id`           |
| 573  | Error   | "\n❌ Bit depth conversion failed."`                                |
| 575  | Error   | `def _on_error(self, error_msg):`                                    |
| 580  | Error   | `self.log_manager.step_error(4, error_msg, batch_id=self.batch_id)`  |
| 581  | Error   | `f"\n❌ Error: {error_msg}"`                                         |
| 584  | Critical| "Conversion Error", `f"Bit depth conversion failed:\n\n{error_msg}"` |
| 613  | Warning | "No TIFF Files", "No TIFF files found in selected directory."
| 631  | Error   | `f"❌ Copy failed: {str(e)}"`                                         |
| 632  | Critical| "Copy Error", `f"Failed to copy TIFF files:\n\n{str(e)}"`            |

## `gui/dialogs/step5_dialog.py`

| Line | Type    | Message                                                              |
|------|---------|----------------------------------------------------------------------|
| 25   | Success | `finished = pyqtSignal(bool, dict)`                                  |
| 26   | Error   | `error = pyqtSignal(str)`                                            |
| 117  | Error   | `except ValueError:`                                                 |
| 124  | Error   | `except ValueError:`                                                 |
| 131  | Error   | `except ValueError:`                                                 |
| 149  | Error   | `self.error.emit(f"Missing required CSV columns: {', '.join(missing_fields)}\n\nExpected columns: {', '.join(required_fields)}\n\nFound columns: {', '.join(reader.fieldnames)}")` |
| 183  | Error   | `except PermissionError as e:`                                       |
| 229  | Warning | `f"⚠️  Failed to embed metadata in {photo}: {str(e)}"`               |
| 230  | Info    | `if "WinError 32" in str(e) or "being used by another process" in str(e):` |
| 233  | Error   | `stats['missing_list'].append(f"{row['ObjectName']} (embed failed)")` |
| 246  | Error   | `self.error.emit(f"Error during metadata embedding: {str(e)}")`      |
| 289  | Warning | `self.progress.emit(f"⚠️  Failed to generate report: {str(e)}")`      |
| 307  | Info    | "Opened Step 5: Metadata Embedding dialog"                         |
| 398  | Warning | "No Data", "No analysis data available. Please run the analysis first."
| 479  | Critical| "Report Error", `f"Failed to generate report:\n\n{str(e)}"`         |
| 480  | Warning | `f"⚠️  Report generation failed: {str(e)}"`                          |
| 491  | Info    | `info_label = QLabel(f"<b>Report saved to:</b> {report_path}")`     |
| 522  | Warning | "⚠️  Error: Project data directory not set"                        |
| 592  | Success | `self.matched_label.setStyleSheet(f"color: {colors.success};" if matched_count > 0 else "")` |
| 597  | Success | `self.missing_tiff_label.setStyleSheet(f"color: {colors.success};")` |
| 600  | Warning | `self.missing_tiff_label.setStyleSheet(f"color: {colors.warning};")`   |
| 605  | Success | `self.comparison_label.setStyleSheet(f"color: {colors.success};")`   |
| 608  | Success | `self.comparison_label.setStyleSheet(f"color: {colors.success};")`   |
| 611  | Warning | `self.comparison_label.setStyleSheet(f"color: {colors.warning};")`   |
| 638  | Warning | `f"⚠️  Error during analysis: {str(e)}"`                              |
| 682  | Error   | `self.embedding_thread.error.connect(self._on_error)`                |
| 689  | Success | `def _on_finished(self, success, stats):`                            |
| 694  | Info    | `if success:`                                                        |
| 696  | Info    | `f"Metadata embedding complete: {stats['processed']} processed, {stats['missing']} missing"` |
| 700  | Info    | "\n Metadata embedding completed successfully!"                    |
| 726  | Info    | "Embedding Complete", `f"Metadata embedding completed successfully!\n\nProcessed: {stats['processed']} images\nMissing: {stats['missing']} images\n\nProcessed TIFFs saved to:\n{output_dir}\n\nStep 5 is now marked as complete."` |
| 729  | Info    | `f"Metadata embedding completed successfully!\n\n"`                  |
| 738  | Error   | "Metadata embedding failed"                                        |
| 739  | Error   | "\n Metadata embedding failed."`                                    |
| 769  | Warning | `f"  ⚠️  Failed to copy {src.name}: {str(e)}"`                        |
| 776  | Warning | `f"\n⚠️  Error copying verso files: {str(e)}"`                        |
| 778  | Error   | `def _on_error(self, error_msg):`                                    |
| 783  | Error   | `self.log_manager.step_error(5, error_msg, batch_id=self.batch_id, exc_info=True)` |
| 784  | Error   | `f"\n Error: {error_msg}"`                                           |
| 788  | Critical| "Embedding Error", `f"Metadata embedding failed:\n\n{error_msg}"`   |
| 789  | Critical| `f"Metadata embedding failed:\n\n{error_msg}"`                       |

## `gui/dialogs/step6_dialog.py`

| Line | Type    | Message                                                              |
|------|---------|----------------------------------------------------------------------|
| 24   | Success | `finished = pyqtSignal(bool, dict)`                                  |
| 25   | Error   | `error = pyqtSignal(str)`                                            |
| 43   | Error   | `'failed': 0,`                                                       |
| 44   | Error   | `'failed_list': []`                                                  |
| 61   | Error   | `self.error.emit(f"No TIFF files found in {self.tiff_dir}")`         |
| 96   | Info    | `if 'exif' in img.info:`                                             |
| 97   | Info    | `exif_data = img.info['exif']`                                       |
| 134  | Warning | `f"⚠️  Failed: {tiff_path.name} - {str(e)}"`                         |
| 135  | Error   | `stats['failed'] += 1`                                               |
| 136  | Error   | `stats['failed_list'].append(tiff_path.name)`                        |
| 141  | Info    | `f"✓ Failed: {stats['failed']} files"`                              |
| 151  | Error   | `self.error.emit(f"Error during JPEG conversion: {str(e)}")`         |
| 177  | Info    | `f.write(f"Successfully converted: {stats['converted']}\n")`         |
| 178  | Info    | `f.write(f"Failed: {stats['failed']}\n")`                            |
| 181  | Error   | `if stats['failed_list']:`                                           |
| 182  | Error   | `f.write("FAILED CONVERSIONS:\n")`                                   |
| 184  | Error   | `for failed in stats['failed_list']:`                                |
| 185  | Error   | `f.write(f"  - {failed}\n")`                                         |
| 193  | Warning | `self.progress.emit(f"⚠️  Failed to generate report: {str(e)}")`      |
| 306  | Warning | "⚠️  Error: Project data directory not set"                        |
| 342  | Warning | `f"⚠️  Warning: {jpeg_count} JPEG files already exist and will be overwritten"` |
| 349  | Warning | `f"⚠️  Error during analysis: {str(e)}"`                              |
| 399  | Error   | `self.conversion_thread.error.connect(self._on_error)`               |
| 406  | Success | `def _on_finished(self, success, stats):`                            |
| 411  | Info    | `if success:`                                                        |
| 412  | Info    | "\n✅ JPEG conversion completed successfully!"                     |
| 415  | Info    | `f"  Failed: {stats['failed']} files"`                               |
| 433  | Info    | `f"Step 6: Converted {stats['converted']} TIFFs to JPEG"`           |
| 438  | Info    | "Conversion Complete", `f"JPEG conversion completed successfully!\n\nConverted: {stats['converted']} files\nFailed: {stats['failed']} files\n\nJPEG files saved to:\n{jpeg_dir}\n\nStep 6 is now marked as complete."` |
| 441  | Info    | `f"JPEG conversion completed successfully!\n\n"`                     |
| 443  | Info    | `f"Failed: {stats['failed']} files\n\n"`                             |
| 450  | Error   | "JPEG conversion failed"                                           |
| 451  | Error   | "\n❌ JPEG conversion failed."`                                     |
| 453  | Error   | `def _on_error(self, error_msg):`                                    |
| 458  | Error   | `self.log_manager.step_error(6, error_msg, batch_id=self.batch_id)`  |
| 459  | Error   | `f"\n❌ Error: {error_msg}"`                                         |
| 463  | Critical| "Conversion Error", `f"JPEG conversion failed:\n\n{error_msg}"`     |
| 464  | Critical| `f"JPEG conversion failed:\n\n{error_msg}"`                         |

## `gui/dialogs/step7_dialog.py`

| Line | Type    | Message                                                              |
|------|---------|----------------------------------------------------------------------|
| 25   | Success | `finished = pyqtSignal(bool, dict)`                                  |
| 26   | Error   | `error = pyqtSignal(str)`                                            |
| 46   | Error   | `'failed': 0,`                                                       |
| 47   | Error   | `'failed_list': [],`                                                 |
| 48   | Error   | `'size_info': []`                                                    |
| 66   | Error   | `self.error.emit(f"No JPEG files found in {self.jpeg_dir}")`         |
| 92   | Info    | `if 'exif' in img.info:`                                             |
| 93   | Info    | `exif_data = img.info['exif']`                                       |
| 120  | Info    | `if 'exif' in img.info:`                                             |
| 121  | Info    | `exif_data = img.info['exif']`                                       |
| 136  | Info    | `stats['size_info'].append({`                                        |
| 157  | Warning | `f"⚠️  Failed: {jpeg_path.name} - {str(e)}"`                         |
| 158  | Error   | `stats['failed'] += 1`                                               |
| 159  | Error   | `stats['failed_list'].append(jpeg_path.name)`                        |
| 165  | Info    | `f"✓ Failed: {stats['failed']} files"`                              |
| 175  | Error   | `self.error.emit(f"Error during JPEG resizing: {str(e)}")`           |
| 204  | Info    | `f.write(f"Failed: {stats['failed']}\n")`                            |
| 207  | Info    | `if stats['size_info']:`                                             |
| 210  | Info    | `for info in stats['size_info']:`                                    |
| 211  | Info    | `f.write(f"  {info['filename']}: {info['original']} → {info['resized']}\n")` |
| 214  | Error   | `if stats['failed_list']:`                                           |
| 215  | Error   | `f.write("FAILED CONVERSIONS:\n")`                                   |
| 217  | Error   | `for failed in stats['failed_list']:`                                |
| 218  | Error   | `f.write(f"  - {failed}\n")`                                         |
| 226  | Warning | `self.progress.emit(f"⚠️  Failed to generate report: {str(e)}")`      |
| 355  | Warning | "⚠️  Error: Project data directory not set"                        |
| 391  | Warning | `f"⚠️  Warning: {resized_count} resized JPEG files already exist and will be overwritten"` |
| 398  | Warning | `f"⚠️  Error during analysis: {str(e)}"`                              |
| 451  | Error   | `self.resize_thread.error.connect(self._on_error)`                   |
| 458  | Success | `def _on_finished(self, success, stats):`                            |
| 463  | Info    | `if success:`                                                        |
| 464  | Info    | "\n✅ JPEG resizing completed successfully!"                       |
| 468  | Info    | `f"  Failed: {stats['failed']} files"`                               |
| 486  | Info    | `f"Step 7: Resized {stats['resized']} JPEGs, skipped {stats['skipped']}"` |
| 491  | Info    | "Resizing Complete", `f"JPEG resizing completed successfully!\n\nResized: {stats['resized']} files\nSkipped: {stats['skipped']} files\nFailed: {stats['failed']} files\n\nResized JPEGs saved to:\n{resized_dir}\n\nStep 7 is now marked as complete."` |
| 494  | Info    | `f"JPEG resizing completed successfully!\n\n"`                       |
| 497  | Info    | `f"Failed: {stats['failed']} files\n\n"`                             |
| 504  | Error   | "JPEG resizing failed"                                             |
| 505  | Error   | "\n❌ JPEG resizing failed."`                                       |
| 507  | Error   | `def _on_error(self, error_msg):`                                    |
| 512  | Error   | `self.log_manager.step_error(7, error_msg, batch_id=self.batch_id)`  |
| 513  | Error   | `f"\n❌ Error: {error_msg}"`                                         |
| 517  | Critical| "Resizing Error", `f"JPEG resizing failed:\n\n{error_msg}"`         |
| 518  | Critical| `f"JPEG resizing failed:\n\n{error_msg}"`                         |

## `gui/dialogs/step8_dialog.py`

| Line | Type    | Message                                                              |
|------|---------|----------------------------------------------------------------------|
| 24   | Success | `finished = pyqtSignal(bool, dict)`                                  |
| 25   | Error   | `error = pyqtSignal(str)`                                            |
| 46   | Error   | `'failed': 0,`                                                       |
| 47   | Error   | `'failed_list': [],`                                                 |
| 65   | Error   | `self.error.emit(f"Failed to load watermark image: {str(e)}")`       |
| 74   | Error   | `self.error.emit(f"No JPEG files found in {self.jpeg_dir}")`         |
| 179  | Info    | `if 'exif' in img.info:`                                             |
| 180  | Info    | `exif_data = img.info['exif']`                                       |
| 212  | Warning | `f"⚠️  Failed: {jpeg_path.name} - {str(e)}"`                         |
| 213  | Error   | `stats['failed'] += 1`                                               |
| 214  | Error   | `stats['failed_list'].append(jpeg_path.name)`                        |
| 221  | Info    | `f"✓ Failed: {stats['failed']}"`                                     |
| 231  | Error   | `self.error.emit(f"Error during watermarking: {str(e)}")`            |
| 261  | Info    | `f.write(f"Failed: {stats['failed']}\n")`                            |
| 271  | Error   | `if stats['failed_list']:`                                           |
| 272  | Error   | `f.write("FAILED PROCESSING:\n")`                                    |
| 274  | Error   | `for failed in stats['failed_list']:`                                |
| 275  | Error   | `f.write(f"  - {failed}\n")`                                         |
| 283  | Warning | `self.progress.emit(f"⚠️  Failed to generate report: {str(e)}")`      |
| 360  | Info    | `watermark_info = QLabel(f"<i>Watermark file: {watermark_path.name}</i>")` |
| 427  | Warning | "⚠️  Error: Project data directory not set"                        |
| 483  | Error   | `self.output_text.append(f"  {Path(jpeg_path).name}: Error reading metadata: {str(e)}")` |
| 507  | Warning | `f"\n⚠️  Warning: {watermarked_count} watermarked files already exist and will be overwritten"` |
| 514  | Warning | `f"⚠️  Error during analysis: {str(e)}"`                              |
| 577  | Error   | `self.watermark_thread.error.connect(self._on_error)`                |
| 584  | Success | `def _on_finished(self, success, stats):`                            |
| 589  | Info    | `if success:`                                                        |
| 590  | Info    | "\n✅ Watermarking process completed successfully!"                |
| 595  | Info    | `f"  Failed: {stats['failed']}"`                                     |
| 613  | Info    | `f"Step 8: Watermarked {stats['watermarked']} restricted, copied {stats['copied_unrestricted']}"` |
| 618  | Info    | "Watermarking Complete", `f"Watermarking process completed successfully!\n\nTotal processed: {stats['jpeg_files_found']} files\nWatermarked (restricted): {stats['watermarked']} files\nCopied (unrestricted): {stats['copied_unrestricted']} files\nFailed: {stats['failed']} files\n\nOutput saved to:\n{watermarked_dir}\n\nStep 8 is now marked as complete."` |
| 621  | Info    | `f"Watermarking process completed successfully!\n\n"`                |
| 625  | Info    | `f"Failed: {stats['failed']} files\n\n"`                             |
| 632  | Error   | "Watermarking process failed"                                      |
| 633  | Error   | "\n❌ Watermarking process failed."`                                |
| 635  | Error   | `def _on_error(self, error_msg):`                                    |
| 640  | Error   | `self.log_manager.step_error(8, error_msg, batch_id=self.batch_id)`  |
| 641  | Error   | `f"\n❌ Error: {error_msg}"`                                         |
| 645  | Critical| "Watermarking Error", `f"Watermarking process failed:\n\n{error_msg}"` |
| 646  | Critical| `f"Watermarking process failed:\n\n{error_msg}"`                     |
