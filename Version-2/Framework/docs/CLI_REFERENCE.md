# HPM Command-Line Interface Reference

The `hstl_framework.py` CLI provides batch initialization and management functions. The GUI (`gui\hstl_gui.py`) is the primary interface for day-to-day use; the CLI is most useful for scripting and batch setup.

## Global Options

```
python hstl_framework.py [--config PATH] [--verbose] <command>
```

| Option | Description |
|--------|-------------|
| `--config PATH` | Path to a `project_config.yaml` file |
| `--verbose`, `-v` | Enable verbose output |
| `--version` | Show framework version and exit |

---

## Commands

### `init` — Initialize a New Batch

```powershell
# Simple — uses default base directory (C:\Data\HSTL_Batches)
python hstl_framework.py init "January 2025 Batch"

# Custom base directory
python hstl_framework.py init "January 2025" --base-dir "D:\MyBatches"

# Full custom path
python hstl_framework.py init "January 2025" --data-dir "C:\Custom\Path"

# Overwrite existing configuration
python hstl_framework.py init "January 2025" --force
```

Creates the batch directory structure, generates `project_config.yaml`, and registers the batch in the framework registry.

---

### `status` — Show Project Status

```powershell
python hstl_framework.py --config "path\to\project_config.yaml" status
python hstl_framework.py --config "path\to\project_config.yaml" status --verbose
```

---

### `run` — Run Processing Steps

```powershell
# Run all steps
python hstl_framework.py --config "path\to\project_config.yaml" run --all

# Run a single step
python hstl_framework.py --config "path\to\project_config.yaml" run --step 2

# Run a range of steps
python hstl_framework.py --config "path\to\project_config.yaml" run --steps 2-5

# Dry run (validate without executing)
python hstl_framework.py --config "path\to\project_config.yaml" run --all --dry-run
```

---

### `config` — View or Update Configuration

```powershell
# List all configuration values
python hstl_framework.py --config "path\to\project_config.yaml" config --list

# Set a configuration value (dot notation)
python hstl_framework.py --config "path\to\project_config.yaml" config --set project.data_directory "C:\new\path"
python hstl_framework.py --config "path\to\project_config.yaml" config --set step_configurations.step7.max_dimension 1024
python hstl_framework.py --config "path\to\project_config.yaml" config --set validation.strict_mode false
```

---

### `batches` — List Batch Projects

```powershell
# List active batches
python hstl_framework.py batches

# List all batches (including completed and archived)
python hstl_framework.py batches --all
```

---

### `batch` — Manage an Individual Batch

```powershell
# Show detailed information
python hstl_framework.py batch info <batch_id>

# Mark as completed (removes from active list)
python hstl_framework.py batch complete <batch_id>

# Archive for long-term storage
python hstl_framework.py batch archive <batch_id>

# Reactivate a completed or archived batch
python hstl_framework.py batch reactivate <batch_id>

# Remove from registry (files are NOT deleted)
python hstl_framework.py batch remove <batch_id>           # shows confirmation prompt
python hstl_framework.py batch remove <batch_id> --confirm  # executes removal
```

### Batch Status States

| Status | Description |
|--------|-------------|
| `active` | Currently being processed |
| `completed` | All processing finished |
| `archived` | Long-term storage |

Status changes never delete files. Data is preserved until you manually delete the directory.

---

### `gui` — Launch the GUI

```powershell
python hstl_framework.py gui
```

Equivalent to running `python gui\hstl_gui.py` directly.

---

## Common Configuration Keys

| Key | Description |
|-----|-------------|
| `project.name` | Batch/project name |
| `project.data_directory` | Root path to the data directory |
| `steps_completed.stepN` | Boolean completion flag for each step (1–8) |
| `step_configurations.step6.quality` | JPEG quality (Step 6) |
| `step_configurations.step7.max_dimension` | Max pixel dimension for resize (Step 7) |
| `step_configurations.step8.watermark_opacity` | Watermark opacity (Step 8) |
| `validation.strict_mode` | Enable/disable strict validation |

---

## See Also

- [`README.md`](../README.md) — Project overview and getting started
- [`docs/QUICKSTART.md`](QUICKSTART.md) — Quick start reference
- [`docs/USER_GUIDE.md`](USER_GUIDE.md) — GUI user guide
