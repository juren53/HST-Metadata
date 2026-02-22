# HPM Final Product Delivery Plan

**HSTL Photo Metadata (HPM) Project**
**Version:** 1.0
**Date:** 2026-02-21

---

## 1. Executive Summary

This document describes the Delivery Plan for the HSTL Photo Metadata (HPM) workflow system. The delivery feature creates a finalized package of processed TIFF and JPEG images at the completion of the 8-step workflow, organizing artifacts into delivery-ready and disposable categories.

---

## 2. Objectives

- Create separate directories for TIFF and JPEG final delivery products
- Organize workflow artifacts into retainable and disposable categories
- Provide a clean, professional delivery structure for client handoff
- Simplify cleanup of intermediate workflow files via batch-level trash

---

## 3. Data Structure

### 3.1 Final Directory Structure

```
{batch_name}/
├── input/
│   ├── tiff/                    # Original TIFF images
│   └── spreadsheet/             # Excel source file (RETAINED)
├── output/
│   ├── csv/                    # export.csv (RETAINED)
│   ├── tiff_processed/         # Metadata-embedded TIFFs
│   ├── jpeg/                   # Converted JPEGs → MOVED to trash
│   ├── jpeg_resized/           # Resized JPEGs → MOVED to trash
│   └── jpeg_watermarked/      # Final watermarked JPEGs
├── delivery/                   # NEW - Delivery package
│   ├── tiff_delivery/          # NEW - Final TIFFs for delivery
│   └── jpeg_delivery/          # NEW - Final JPEGs for delivery
├── trash/                      # NEW - Disposable artifacts
│   ├── jpeg_converted/         # From output/jpeg
│   └── jpeg_resized/          # From output/jpeg_resized
├── logs/                       # Session logs (RETAINED)
├── reports/                    # Batch reports (RETAINED)
└── config/
    └── project_config.yaml
```

### 3.2 Artifact Classification

| Artifact | Current Location | Final Location | Status |
|----------|------------------|----------------|--------|
| Excel source file | `input/spreadsheet/` | `input/spreadsheet/` | RETAINED |
| export.csv | `output/csv/` | `output/csv/` | RETAINED |
| Batch reports | `reports/` | `reports/` | RETAINED |
| Session logs | `logs/` | `logs/` | RETAINED |
| Converted JPEGs | `output/jpeg/` | `trash/jpeg_converted/` | DISPOSABLE |
| Resized JPEGs | `output/jpeg_resized/` | `trash/jpeg_resized/` | DISPOSABLE |
| Final TIFFs | `output/tiff_processed/` | `delivery/tiff_delivery/` | DELIVERY |
| Final JPEGs | `output/jpeg_watermarked/` | `delivery/jpeg_delivery/` | DELIVERY |

### 3.3 Key Design Decisions

- **Delivery directories**: Created as NEW top-level directories within the batch folder (not replacing existing output folders)
- **Trash location**: Batch-level trash folder (not system trash) for easy review before permanent deletion
- **Trigger condition**: Delivery only available after all 8 steps are completed

---

## 4. User Interface

### 4.1 Menu Structure

The delivery menu items will be added to the **existing Batch menu** (currently between View and Tools):

```
Menu Bar:
├── File
├── Edit
├── View
├── Batch          ← EXISTING MENU - ADD DELIVERY ITEMS HERE
│   ├── Refresh Batches
│   ├── Mark as Complete
│   ├── Archive
│   ├── Reactivate
│   ├── ───────────────────  ← ADD SEPARATOR
│   ├── Create Delivery Package...    ← NEW
│   ├── Open Delivery Directory      ← NEW
│   ├── Open Trash Directory         ← NEW
│   └── Empty Trash...               ← NEW
├── Tools
└── Help
```

### 4.2 New Menu Items

The following items will be added to the existing Batch menu:

| Menu Item | Description |
|-----------|-------------|
| **Create Delivery Package...** | Executes the delivery process |
| **Open Delivery Directory** | Opens `delivery/` in file explorer |
| **Open Trash Directory** | Opens `trash/` in file explorer |
| **Empty Trash...** | Permanently deletes trash contents |

### 4.3 Menu States

- **Create Delivery Package**: Enabled only when a batch is selected AND all 8 steps are completed
- **Open Delivery Directory**: Enabled when batch has a delivery directory
- **Open Trash Directory**: Enabled when batch has a trash directory
- **Empty Trash...**: Enabled when trash contains files

---

## 5. Process Flow

### 5.1 Create Delivery Package

#### Step 1: Validation
- Verify all 8 steps are completed
- Confirm source directories exist
- Check if delivery already exists (offer to overwrite)

#### Step 2: User Confirmation
Display confirmation dialog showing:
- Batch name
- File counts for TIFF delivery
- File counts for JPEG delivery
- File counts to be moved to trash

#### Step 3: Execution
Operations performed in sequence:
1. Create `delivery/tiff_delivery/` — Copy from `output/tiff_processed/`
2. Create `delivery/jpeg_delivery/` — Copy from `output/jpeg_watermarked/`
3. Create `trash/jpeg_converted/` — Move contents of `output/jpeg/`
4. Create `trash/jpeg_resized/` — Move contents of `output/jpeg_resized/`
5. Log all operations with timestamps

#### Step 4: Completion
- Display success message with delivery location
- Log completion to batch logs
- Refresh batch list

### 5.2 Empty Trash

#### Step 1: Confirmation
- Display warning: "This will permanently delete all files in the trash folder"
- Show file counts in trash

#### Step 2: Execution
- Recursively delete trash directory contents
- Log operation

---

## 6. Implementation Components

| Component | File | Description |
|-----------|------|-------------|
| Menu update | `gui/main_window.py` | Add delivery items to existing Batch menu |
| Delivery dialog | `gui/dialogs/delivery_dialog.py` | NEW — Confirmation and progress UI |
| Delivery service | `core/delivery_service.py` | NEW — Business logic for packaging |
| Path updates | `utils/path_manager.py` | Add delivery/trash path methods |
| Documentation | `docs/Standard Directory Structure.txt` | Update directory diagram |

---

## 7. Edge Cases

| Scenario | Handling |
|----------|----------|
| Incomplete steps | Show warning, disable delivery button |
| Existing delivery | Offer to overwrite or skip |
| Empty source directories | Show error, abort operation |
| Permission errors | Catch and display user-friendly error |
| Partial failure | Log incomplete state, allow retry |

---

## 8. Benefits

1. **Professional Delivery**: Clean, organized structure for client handoff
2. **Space Management**: Easy identification and removal of disposable files
3. **Audit Trail**: All workflow artifacts preserved in original locations for review
4. **User Experience**: Simple one-click delivery creation with clear feedback
5. **Reversibility**: Trash allows recovery before permanent deletion

---

## 9. Summary

The Delivery Plan provides a complete solution for packaging HPM workflow results:

- **New directories** (`delivery/`, `trash/`) added to batch structure
- **Existing Batch menu** updated with delivery and trash management options
- **Retained artifacts**: Excel file, CSV export, reports, logs
- **Delivered products**: Final TIFFs and JPEGs in dedicated delivery folders
- **Disposable artifacts**: Intermediate JPEG files moved to trash for optional cleanup

---

*Document prepared for client review*
*Implementation to follow upon approval*
