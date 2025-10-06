# HSTL Photo Framework

A comprehensive Python framework for managing the complete HSTL Photo Metadata Project workflow.

## Quick Start

```bash
# Initialize a new project
python hstl_framework.py init --data-dir "C:\path\to\images" --project-name "MyProject"

# Run the complete workflow
python hstl_framework.py run --all

# Run specific steps
python hstl_framework.py run --step 2
python hstl_framework.py run --steps 2-5

# Check project status
python hstl_framework.py status
```

## Project Structure

This framework orchestrates 8 steps of photo metadata processing:

1. **Google Spreadsheet Preparation** - Collaborative spreadsheet setup
2. **CSV Conversion** - Google Worksheet to CSV conversion  
3. **Unicode Filtering** - Text encoding cleanup and validation
4. **TIFF Conversion** - 16-bit to 8-bit TIFF conversion
5. **Metadata Embedding** - Embed metadata into TIFF images
6. **JPEG Conversion** - Convert TIFFs to JPEGs
7. **JPEG Resizing** - Resize JPEGs to 800x800 pixel constraint
8. **Watermarking** - Add watermarks to restricted images

## Development Status

🚧 **Currently in Development** - CLI Phase

- ✅ Development plan created
- ⏳ Core framework implementation (in progress)
- ⏳ Step module integration
- 📋 GUI implementation (planned for Phase 2)

## Documentation

- [`DEVELOPMENT_PLAN.md`](DEVELOPMENT_PLAN.md) - Comprehensive development roadmap
- Requirements and dependencies listed in development plan
- Integration strategy for existing Version-2 applications

## Environment

- **Platform**: Windows (PowerShell)
- **Python**: 3.8+
- **Framework Location**: `C:\Users\jimur\Projects\HST-Metadata\Photo\Version-2\Framework\`
- **Data Directories**: Configurable, separate from framework location

---

*This project integrates and orchestrates existing HSTL photo processing applications into a unified workflow management system.*