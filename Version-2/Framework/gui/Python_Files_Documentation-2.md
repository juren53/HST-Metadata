 # Python Files in HSTL GUI Application  
   
 ## Overview  
   
 The HSTL Photo Framework GUI consists of **18 Python files** organized into a clean modular architecture with three main components: main application files, widget components, and dialog components.  
   
 **Total Python Files:** 18  
 **Architecture:** PyQt6-based GUI with MVC pattern  
 **Purpose:** Photo metadata processing workflow management  
   
 ---  
   
 ## Main Application Files (3 files)  
   
 ### \`hstl_gui.py\`  
 - **Purpose:** Application entry point and main launcher  
 - **Key Functions:**  
   - Sets up PyQt6 application with high DPI support  
   - Creates and displays main window  
   - Handles application lifecycle  
 - **Dependencies:** PyQt6, sys, pathlib  
 - **Version:** 0.0.5  
   
 ### \`main_window.py\`  
 - **Purpose:** Main window with tab-based interface  
 - **Key Functions:**  
   - Tab management (Batches, Current Batch, Configuration, Logs)  
   - Menu bar with keyboard shortcuts  
   - Status bar with current batch indicator  
   - Window state persistence  
   - Batch selection and action handling  
 - **Dependencies:** PyQt6, HSLTFramework, BatchRegistry  
 - **Key Features:** Multi-batch management, step execution coordination  
   
 ### \`__init__.py\` (Root)  
 - **Purpose:** GUI package initialization  
 - **Exports:** MainWindow, main  
 - **Version Info:** v0.0.5, Commit: 2025-12-08 15:05  
   
 ---  
   
 ## Widget Components (4 files)  
   
 ### \`widgets/batch_list_widget.py\`  
 - **Purpose:** Batch management table widget  
 - **Key Functions:**  
   - Displays all registered batches with status and progress  
   - Color-coded status indicators (aqua=active, light blue=completed, gray=archived)  
   - Context menu for batch actions  
   - Progress bars showing completion percentage  
 - **Features:** Filter archived batches, real-time updates  
   
 ### \`widgets/step_widget.py\`  
 - **Purpose:** Step execution interface for 8 processing steps  
 - **Key Functions:**  
   - Visual interface for all 8 processing steps in 2-column grid  
   - Individual step execution with Run, Review, Revert buttons  
   - Batch operations (Run All, Run Next, Validate All)  
   - Real-time status updates and progress tracking  
   - Output/log viewer for step execution feedback  
 - **Step Names:** Google Worksheet → CSV → Unicode → TIFF → Metadata → JPEG → Resize → Watermark  
   
 ### \`widgets/config_widget.py\`  
 - **Purpose:** Configuration tree viewer  
 - **Key Functions:**  
   - Hierarchical display of YAML configuration  
   - Read-only tree view with expandable sections  
   - Refresh capability to reload configuration  
 - **Features:** Complete configuration visibility  
   
 ### \`widgets/log_widget.py\`  
 - **Purpose:** Log viewer widget  
 - **Key Functions:**  
   - Read-only text display for application logs  
   - Simple interface for log monitoring  
 - **Status:** Basic implementation, extensible  
   
 ### \`widgets/__init__.py\`  
 - **Purpose:** Widgets package initialization  
 - **Exports:** BatchListWidget, StepWidget, ConfigWidget, LogWidget  
   
 ---  
   
 ## Dialog Components (10 files)  
   
 ### \`dialogs/new_batch_dialog.py\`  
 - **Purpose:** Create new batch projects  
 - **Key Functions:**  
   - Project name input  
   - Location options (default, custom base, full custom path)  
   - Directory browsing functionality  
 - **Features:** Flexible batch creation with multiple location options  
   
 ### \`dialogs/batch_info_dialog.py\`  
 - **Purpose:** Display detailed batch information  
 - **Key Functions:**  
   - Comprehensive batch details display  
   - Status and progress information  
   - Configuration summary  
   
 ### \`dialogs/settings_dialog.py\`  
 - **Purpose:** Application settings management  
 - **Current Status:** Placeholder implementation  
 - **Future:** Extensible settings interface  
   
 ### \`dialogs/step1_dialog.py\`  
 - **Purpose:** Google Worksheet preparation  
 - **Key Functions:**  
   - Google Worksheet URL input and validation  
   - Required fields specification  
   - Step completion marking  
 - **Features:** URL validation, configuration saving  
   
 ### \`dialogs/step2_dialog.py\`  
 - **Purpose:** CSV conversion from Google Worksheet  
 - **Key Functions:**  
   - Threading for long-running conversion  
   - Progress tracking and status updates  
   - Integration with g2c functionality  
 - **Dependencies:** g2c module, threading  
   
 ### \`dialogs/step4_dialog.py\`  
 - **Purpose:** TIFF bit depth conversion  
 - **Key Functions:**  
   - Bit depth conversion processing  
   - Quality checking and validation  
   - Metadata preservation  
 - **Features:** Backup original option, quality validation  
   
 ### \`dialogs/step5_dialog.py\`  
 - **Purpose:** Metadata embedding into TIFF files  
 - **Key Functions:**  
   - Metadata embedding with ExifTool integration  
   - Progress tracking for batch processing  
   - Report generation  
 - **Dependencies:** ExifTool, threading  
   
 ### \`dialogs/step6_dialog.py\`  
 - **Purpose:** TIFF to JPEG conversion  
 - **Key Functions:**  
   - Format conversion with quality settings  
   - Transparency handling (white background)  
   - EXIF data preservation  
 - **Dependencies:** PIL/Pillow, ExifTool  
   
 ### \`dialogs/step7_dialog.py\`  
 - **Purpose:** JPEG resizing  
 - **Key Functions:**  
   - High-quality resizing with Lanczos resampling  
   - Aspect ratio maintenance  
   - Metadata preservation  
   - Progress tracking and reporting  
 - **Dependencies:** PIL/Pillow, ExifTool  
 - **Features:** Configurable dimensions, quality settings  
   
 ### \`dialogs/step8_dialog.py\`  
 - **Purpose:** Watermark application  
 - **Key Functions:**  
   - Conditional watermarking for \ Restricted\  images  
   - Opacity control and positioning  
   - Alpha compositing for watermark overlay  
   - Copyright field analysis  
 - **Dependencies:** PIL/Pillow, ExifTool  
 - **Features:** Smart watermarking, metadata preservation  
   
 ### \`dialogs/__init__.py\`  
 - **Purpose:** Dialogs package initialization  
 - **Exports:** NewBatchDialog, BatchInfoDialog, SettingsDialog, Step1Dialog, Step2Dialog, Step5Dialog  
   
 ---  
   
 ## Package Structure Files (3 files)  
   
 ### \`__init__.py\` Files  
 - **Root \`__init__.py\`**: Main GUI package initialization  
 - **\`widgets/__init__.py\`**: Widgets package exports  
 - **\`dialogs/__init__.py\`**: Dialogs package exports  
   
 ---  
   
 ## Technical Implementation Details  
   
 ### Dependencies Used  
 - **PyQt6**: GUI framework and widgets  
 - **PIL/Pillow**: Image processing (resizing, watermarking, conversion)  
 - **ExifTool**: Comprehensive metadata handling  
 - **pathlib**: Modern path operations  
 - **threading**: Background processing for long operations  
   
 ### Architecture Patterns  
 - **MVC Pattern**: Separation of UI (widgets) from logic (dialogs)  
 - **Signal/Slot**: PyQt6 event handling  
 - **Threading**: Worker threads for long-running operations  
 - **Configuration Management**: YAML-based configuration system  
   
 ### Key Features Implemented  
 - **Multi-batch Management**: Complete lifecycle tracking  
