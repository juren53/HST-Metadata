# HSTL Photo Framework - Screen Capture Video Production Plan

## Project Overview
This plan outlines the creation of comprehensive screen capture videos for the HSTL Photo Metadata GUI application (also known as HSTL Photo Framework System). The goal is to create user walkthrough videos without audio, starting with simple screen captures and adding annotations in a second phase.

## Phase 1: Preparation & Setup

### Technical Requirements
- **Recording Software Options:**
  - **OBS Studio** (Free, professional, supports annotations)
  - **Camtasia** (Paid, excellent annotation features)
  - **ScreenToGif** (Free, good for short sequences)
  - **Loom** (Free tier available, cloud-based)

- **Recommended Settings:**
  - Resolution: 1920x1080 minimum (4K if possible for clarity)
  - Frame rate: 30fps for smooth UI interactions
  - Format: MP4 with H.264 encoding
  - Audio: Disabled (as requested)

### Environment Preparation
- Clean desktop with minimal distractions
- Set application to 100% zoom for initial recording
- Prepare sample data (small set of TIFFs, sample Google Sheet)
- Test all steps work correctly before recording

## Phase 2: Content Strategy - Modular Video Series

### Video Series Structure
1. **Introduction & Overview** (2-3 minutes)
2. **Setup & Configuration** (3-4 minutes)  
3. **Creating Your First Batch** (2-3 minutes)
4. **The 8-Step Processing Pipeline** (8-10 minutes total)
5. **Advanced Features** (3-4 minutes)
6. **Troubleshooting & Tips** (2-3 minutes)

## Phase 3: Scene-by-Scene Recording Plan

### Video 1: Introduction & Application Overview
- **Scene 1:** Application launch & main window tour
- **Scene 2:** Theme switching demonstration (Light → Dark → System)
- **Scene 3:** Zoom controls & window management
- **Scene 4:** Main tabs overview (Batches, Current Batch, Config, Logs)

### Video 2: Setup & First Batch Creation
- **Scene 1:** Settings menu exploration
- **Scene 2:** New Batch dialog with all three location options
- **Scene 3:** Directory structure creation demo
- **Scene 4:** File preparation (showing input folders)

### Video 3: Step-by-Step Processing (Core Tutorial)
- **Scene 1:** Step 1 - Google Worksheet setup
- **Scene 2:** Step 2 - CSV conversion (with authentication demo)
- **Scene 3:** Step 3 - Unicode filtering
- **Scene 4:** Step 4 - TIFF conversion
- **Scene 5:** Step 5 - Metadata embedding
- **Scene 6:** Step 6 - JPEG conversion
- **Scene 7:** Step 7 - Resizing
- **Scene 8:** Step 8 - Watermarking

### Video 4: Advanced Features & Batch Management
- **Scene 1:** Batch operations (Complete, Archive, Reactivate)
- **Scene 2:** Review features (opening directories, TagWriter)
- **Scene 3:** Configuration viewer exploration
- **Scene 4:** Validation and reporting

## Phase 4: Recording Best Practices

### Recording Guidelines
- **Pacing:** Allow 3-5 seconds for UI elements to load
- **Mouse Movement:** Slow, deliberate cursor movements
- **Window Positioning:** Keep main window centered
- **Dialog Focus:** Ensure dialogs don't obscure important content
- **Status Indicators:** Wait for progress bars and status updates

### Content Optimization
- Use consistent sample data across all videos
- Demonstrate both "Run Individual Step" and "Run All Steps"
- Show error handling and recovery scenarios
- Highlight keyboard shortcuts (Ctrl+N, F5, etc.)

## Phase 5: Annotation Strategy (Future Enhancement)

### Annotation Types to Add Later
- **Callouts:** Highlight important buttons and menu items
- **Text Overlays:** Step numbers and key information
- **Zoom-ins:** Focus on specific UI elements during complex operations
- **Progress Indicators:** Show which step in the workflow
- **Arrows:** Guide attention to specific areas

### Annotation Timing
- Add annotations after base recordings are complete
- Time annotations to match UI interactions
- Keep text concise and readable
- Use consistent color scheme

## Phase 6: Post-Production

### Editing Requirements
- Trim dead time between actions
- Add title cards and transitions
- Ensure consistent pacing across videos
- Add chapter markers for long videos

### Export Settings
- 1080p resolution for compatibility
- Moderate file size for easy sharing
- Compatible format for hosting platforms
- Consider creating both full-length and short clip versions

## Application Overview for Recording

### Main Application Screens
- **Main Window**: 1200x800 pixels default, tab-based interface
- **Four Main Tabs**: Batches, Current Batch, Configuration, Logs
- **Menu Bar**: File, Edit, View, Batch, Tools, Help menus

### Key Dialogs to Record
- New Batch Dialog
- Step Dialogs (8 total)
- Theme Dialog (Light/Dark/System)
- Settings Dialog
- Batch Info Dialog

### User Workflow Steps
1. Application Launch (`python gui/hstl_gui.py`)
2. Theme Selection
3. Create New Batch (File → New Batch or Ctrl+N)
4. File Preparation (TIFFs to input/tiff/, Google Sheets to input/spreadsheet/)
5. 8-Step Processing Pipeline Execution
6. Review & Validation
7. Batch Completion

### Critical Features to Demonstrate
- Multi-batch tracking with status indicators
- Individual vs. "Run All Steps" execution
- Real-time status updates (⭕ Pending, 🔄 Running, ✅ Completed, ❌ Failed)
- Theme management (Light/Dark/System)
- Zoom control (75% to 200% scaling)
- Directory integration (File Explorer launching)
- External tool integration (TagWriter)

## Technical Considerations for Recording

### Screen Resolution Recommendations
- Record at 1080p or higher for clarity
- Ensure UI text remains readable after compression
- Consider zoom levels for visibility in recordings

### UI Responsiveness
- Show smooth transitions and theme changes
- Capture real-time status updates during processing
- Demonstrate window resizing and scrolling

### File Preparation
- Small set of sample TIFF images (3-5 files)
- Sample Google Worksheet with required metadata fields
- Google API credentials setup for Step 2 demonstration

## Next Steps & Questions

### Immediate Actions Required
1. Choose recording software
2. Prepare sample data environment
3. Set up clean recording workspace
4. Test application workflow with sample data

### Decision Points
- Which recording software to use?
- Video length preference - short clips (2-3 min) or comprehensive tutorials (8-10 min)?
- Target audience - new users or experienced users?
- Hosting platform for final videos?
- Timeline for completion?

### Success Metrics
- Clear visibility of all UI elements
- Smooth workflow demonstration
- Comprehensive coverage of all major features
- User-friendly pacing and transitions

---

*This plan provides a structured approach for creating professional screen capture videos of the HSTL Photo Framework application, designed for incremental execution from basic recordings to annotated tutorials.*