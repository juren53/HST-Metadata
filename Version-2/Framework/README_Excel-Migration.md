# HPM Excel Migration - Branch Structure

## Overview

This repository now contains a fork structure for migrating HPM from Google Sheets to Excel spreadsheets.

## Branch Structure

### Main Branches

- **`master`** - Current stable version with Google Sheets integration
- **`framework-setup`** - Existing framework setup branch (preserved)

### Migration Branches

- **`feature/excel-migration`** 🚀 
  - **Active development branch** for Excel migration
  - Contains all migration implementation
  - Target for pull request when complete

- **`feature/excel-migration-backup`** 💾
  - **Backup/milestone branch** for Excel migration
  - Used to save progress milestones
  - Rollback point if needed

## Development Workflow

### 1. Active Development
```bash
git checkout feature/excel-migration
# Work on migration implementation
git add .
git commit -m "Feature implementation"
git push origin feature/excel-migration
```

### 2. Milestone Backup
```bash
# Save current progress to backup branch
git checkout feature/excel-migration-backup
git merge feature/excel-migration
git push origin feature/excel-migration-backup
git checkout feature/excel-migration
```

### 3. Merge to Master (When Complete)
```bash
git checkout master
git merge feature/excel-migration --no-ff
git push origin master
```

## Migration Plan

See: `PLAN_HPM-move-to-XLSX-spreadsheet.md` for comprehensive migration strategy.

### Implementation Phases

1. **Phase 1**: Core data access layer replacement (4-5 days)
   - Replace `g2c.py` Google Sheets integration
   - Create `file_manager.py` module
   
2. **Phase 2**: UI updates (2-3 days)
   - Update Step 1 dialog with file browser and validation
   - Update Step 2 dialog for Excel processing
   
3. **Phase 3**: Configuration updates (1 day)
   - Update requirements.txt
   - Modify settings.py
   
4. **Phase 4**: Cleanup and documentation (1-2 days)
   - Remove Google dependencies
   - Update documentation

**Total Estimated Time**: 10-14 days

## File Management Strategy

### New Directory Structure
```
data_directory/
├── input/
│   ├── tiff/              # Source TIFF files
│   └── spreadsheet/        # Excel spreadsheets (copied from user selection)
├── output/
│   ├── csv/               # export.csv
│   ├── tiff_processed/    # TIFFs with embedded metadata
│   ├── jpeg/             # Converted JPEGs
│   ├── jpeg_resized/     # Resized JPEGs
│   └── jpeg_watermarked/ # Final watermarked JPEGs
└── ...
```

### Step 1 Workflow
1. User selects Excel file via browser
2. File validation (format + structure)
3. Copy to `input/spreadsheet/` directory
4. Confirm successful copy

## Key Files to Modify

### Core Changes
- `g2c.py` - Replace Google Sheets API with Excel reading
- `gui/dialogs/step1_dialog.py` - File browser + validation
- `gui/dialogs/step2_dialog.py` - Excel processing

### New Files
- `file_manager.py` - Excel validation and copying
- `excel_validator.py` - File structure validation

### Configuration
- `requirements.txt` - Update dependencies
- `config/settings.py` - Update step descriptions

## Benefits

- **Offline Processing** - No internet dependency
- **Faster Performance** - Direct file access
- **Simplified Deployment** - No Google API setup
- **Better Security** - No OAuth tokens

## Rollback Plan

If Excel migration encounters issues:

1. **Immediate**: Switch to `master` branch
2. **Partial**: Restore from `feature/excel-migration-backup`
3. **Full**: Google Sheets version remains preserved in `master`

## Contact

For questions about the migration strategy or implementation, please refer to the migration plan document or contact the HPM development team.