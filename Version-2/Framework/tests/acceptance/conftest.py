"""
Shared fixtures for HPM EXE acceptance tests.

These tests treat HPM.exe as a black box and verify:
  - The compiled artifact is valid and correctly sized
  - The EXE launches without crashing
  - Core processing algorithms (watermark, resize) produce correct outputs
  - All source assets required for bundling are present

pywinauto is intentionally NOT used - GUI interaction is kept out of scope
for this suite. Output-file verification is the primary testing strategy.
"""

import tempfile
import shutil
import time
from datetime import datetime
from pathlib import Path

import pytest
from PIL import Image


# ---------------------------------------------------------------------------
# Report generation hooks
# ---------------------------------------------------------------------------

def pytest_configure(config):
    """Initialise report-collection state on the config object."""
    config._acceptance_results = []
    config._acceptance_start   = time.monotonic()


def pytest_runtest_logreport(report):
    """Collect per-test outcomes for acceptance tests only."""
    if report.when != "call":
        return
    # Only track tests that carry the 'acceptance' marker
    if not hasattr(report, "keywords") or "acceptance" not in report.keywords:
        return

    config = report.config if hasattr(report, "config") else None
    # Access via the pytest plugin manager's config
    import _pytest.config as _cfg
    cfg = _cfg.get_plugin_manager().get_plugin("config") if False else None
    # Simpler: stash on the global pytest config via the worker hook
    # We'll collect via a session-scoped list instead (see below).


@pytest.fixture(scope="session", autouse=True)
def _acceptance_report_collector(request):
    """
    Session-scoped fixture that hooks into the test run and writes a
    timestamped markdown report to tests/acceptance/ when it tears down.
    """
    results   = []          # list of (nodeid, outcome, duration_s, longrepr)
    timings   = {}          # nodeid → start time

    # ---- collect results ----
    class _Plugin:
        @staticmethod
        def pytest_runtest_logreport(report):
            if report.when == "setup" and report.outcome != "skipped":
                timings[report.nodeid] = time.monotonic()
            if report.when != "call":
                return
            if "acceptance" not in report.keywords:
                return
            duration = time.monotonic() - timings.get(report.nodeid, time.monotonic())
            longrepr = ""
            if report.failed and report.longrepr:
                longrepr = str(report.longrepr)
            results.append({
                "nodeid":   report.nodeid,
                "outcome":  report.outcome,  # "passed" / "failed" / "skipped"
                "duration": duration,
                "longrepr": longrepr,
            })

    plugin = _Plugin()
    request.config.pluginmanager.register(plugin, "_acceptance_collector")

    suite_start = time.monotonic()
    yield                   # ← tests run here

    request.config.pluginmanager.unregister(plugin)

    if not results:
        return              # nothing to report (no acceptance tests were run)

    _write_report(results, suite_start)


def _write_report(results: list, suite_start: float) -> None:
    """Write a timestamped markdown report to tests/acceptance/."""
    report_dir  = Path(__file__).parent
    version_str = _read_version()
    now         = datetime.now()
    date_str    = now.strftime("%Y-%m-%d")
    time_str    = now.strftime("%H:%M:%S")
    elapsed     = time.monotonic() - suite_start

    passed  = [r for r in results if r["outcome"] == "passed"]
    failed  = [r for r in results if r["outcome"] == "failed"]
    skipped = [r for r in results if r["outcome"] == "skipped"]
    total   = len(results)
    status  = "ALL PASSING" if not failed else f"{len(failed)} FAILING"

    filename = report_dir / f"REPORT_HPM-Acceptance-Test-v{version_str}-{date_str}.md"

    lines = [
        f"# HPM Acceptance Test Report — v{version_str}",
        "",
        f"**Date:** {date_str}  ",
        f"**Time:** {time_str}  ",
        f"**Status:** {status}  ",
        f"**Total Tests:** {total} ({len(passed)} passed, {len(failed)} failed,"
        f" {len(skipped)} skipped)  ",
        f"**Execution Time:** {elapsed:.1f}s  ",
        "",
        "---",
        "",
        "## Results by Module",
        "",
    ]

    # Group by module
    modules: dict[str, list] = {}
    for r in results:
        # nodeid format: tests/acceptance/test_foo.py::Class::method
        parts  = r["nodeid"].split("::")
        module = parts[0].replace("\\", "/").split("/")[-1]  # test_foo.py
        modules.setdefault(module, []).append(r)

    for module, mod_results in sorted(modules.items()):
        mod_passed  = sum(1 for r in mod_results if r["outcome"] == "passed")
        mod_failed  = sum(1 for r in mod_results if r["outcome"] == "failed")
        mod_skipped = sum(1 for r in mod_results if r["outcome"] == "skipped")
        lines += [
            f"### `{module}` — {len(mod_results)} tests"
            f"  ({mod_passed} passed, {mod_failed} failed, {mod_skipped} skipped)",
            "",
            "| Result | Test | Duration |",
            "|--------|------|----------|",
        ]
        for r in mod_results:
            icon = {"passed": "PASS", "failed": "FAIL", "skipped": "SKIP"}.get(
                r["outcome"], r["outcome"].upper()
            )
            short_id = "::".join(r["nodeid"].split("::")[1:])  # strip module path
            lines.append(
                f"| {icon} | `{short_id}` | {r['duration']:.2f}s |"
            )
        lines.append("")

    # Failures detail
    if failed:
        lines += [
            "---",
            "",
            "## Failure Details",
            "",
        ]
        for r in failed:
            lines += [
                f"### `{r['nodeid']}`",
                "",
                "```",
                r["longrepr"][:2000],   # cap at 2 000 chars to keep file tidy
                "```",
                "",
            ]

    lines += [
        "---",
        "",
        f"*Generated automatically by `tests/acceptance/conftest.py` on {date_str} at {time_str}.*",
        "",
    ]

    filename.write_text("\n".join(lines), encoding="utf-8")
    # Print path so it's visible in the pytest summary
    print(f"\n[acceptance] Report saved → {filename}")


def _read_version() -> str:
    """Read __version__ from the top-level __init__.py."""
    init_py = Path(__file__).parent.parent.parent / "__init__.py"
    if not init_py.exists():
        return "unknown"
    for line in init_py.read_text(encoding="utf-8").splitlines():
        if line.startswith("__version__"):
            # __version__ = "1.9.3"
            return line.split("=")[1].strip().strip('"').strip("'")
    return "unknown"

# ---------------------------------------------------------------------------
# Repository paths
# ---------------------------------------------------------------------------

FRAMEWORK_DIR = Path(__file__).parent.parent.parent
DIST_EXE      = FRAMEWORK_DIR / "dist" / "HPM.exe"
WATERMARK_PNG = FRAMEWORK_DIR / "gui" / "Copyright_Watermark.png"
EXIFTOOL_EXE  = FRAMEWORK_DIR / "tools" / "exiftool.exe"
APP_ICON      = FRAMEWORK_DIR / "icons" / "app.ico"
LAUNCHER_ICON = FRAMEWORK_DIR / "launcher" / "HPM_icon.png"
HPM_SPEC      = FRAMEWORK_DIR / "HPM.spec"
INIT_PY       = FRAMEWORK_DIR / "__init__.py"
CHANGELOG_MD  = FRAMEWORK_DIR / "CHANGELOG.md"


# ---------------------------------------------------------------------------
# Path fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def exe_path() -> Path:
    """Path to the compiled HPM.exe in dist/."""
    return DIST_EXE


@pytest.fixture(scope="session")
def watermark_path() -> Path:
    """Path to the Copyright_Watermark.png source asset."""
    return WATERMARK_PNG


@pytest.fixture(scope="session")
def exiftool_path() -> Path:
    """Path to the bundled exiftool.exe."""
    return EXIFTOOL_EXE


@pytest.fixture
def temp_output_dir():
    """Temporary directory, cleaned up after each test."""
    tmp = tempfile.mkdtemp(prefix="hpm_accept_")
    yield Path(tmp)
    shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------------------
# Image factory helpers
# ---------------------------------------------------------------------------

@pytest.fixture
def make_jpeg(temp_output_dir):
    """
    Factory fixture: create a JPEG file of a given size and colour.

    Usage::
        img_path = make_jpeg(800, 533, colour='white', name='landscape.jpg')
    """
    created = []

    def _make(width: int, height: int, colour: str = "white",
               name: str = "test.jpg") -> Path:
        path = temp_output_dir / name
        img = Image.new("RGB", (width, height), colour)
        img.save(path, "JPEG", quality=95)
        created.append(path)
        return path

    return _make


# ---------------------------------------------------------------------------
# Algorithm mirrors
#
# These functions replicate the exact logic frozen inside HPM.exe so that
# acceptance tests can run without launching the GUI.  If the source
# algorithms in step7_dialog.py or step8_dialog.py change, update here too.
# ---------------------------------------------------------------------------

def apply_watermark(img: Image.Image,
                    watermark: Image.Image,
                    opacity: float = 0.30) -> Image.Image:
    """
    Mirror of the watermark scaling algorithm in step8_dialog.py.

    Scales the watermark proportionally to cover the image's larger
    dimension, crops to exact image size, applies opacity, then
    composites onto the image.  Returns an RGB Image.
    """
    if img.mode != "RGBA":
        img = img.convert("RGBA")

    img_width, img_height = img.size
    wm_w, wm_h = watermark.size

    # Proportional scale-to-fill + crop (the aspect-ratio fix for issue #49)
    scale = max(img_width, img_height) / max(wm_w, wm_h)
    scaled_wm = watermark.resize(
        (max(img_width, int(wm_w * scale)),
         max(img_height, int(wm_h * scale))),
        Image.Resampling.LANCZOS,
    )
    watermark_resized = scaled_wm.crop((0, 0, img_width, img_height))

    # Apply opacity
    wm_with_opacity = watermark_resized.copy()
    alpha = wm_with_opacity.split()[3]
    alpha = alpha.point(lambda p: int(p * opacity))
    wm_with_opacity.putalpha(alpha)

    # Composite and return as RGB
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    layer.paste(wm_with_opacity, (0, 0), wm_with_opacity)
    result = Image.alpha_composite(img, layer)
    return result.convert("RGB")


def resize_jpeg(img: Image.Image, max_dimension: int = 800) -> Image.Image:
    """
    Mirror of the resize algorithm in step7_dialog.py.

    If the image fits within max_dimension x max_dimension it is returned
    unchanged.  Otherwise it is downscaled proportionally so the longer
    edge equals max_dimension.
    """
    width, height = img.size

    if width <= max_dimension and height <= max_dimension:
        return img.copy()

    if width > height:
        new_width  = max_dimension
        new_height = int((height / width) * max_dimension)
    else:
        new_height = max_dimension
        new_width  = int((width / height) * max_dimension)

    return img.resize((new_width, new_height), Image.Resampling.LANCZOS)


def is_restricted(copyright_notice: str) -> bool:
    """
    Mirror of the copyright-detection logic in step8_dialog.py.

    Returns True only when 'restricted' is present (case-insensitive)
    and 'unrestricted' is NOT present.
    """
    if not copyright_notice:
        return False
    lower = copyright_notice.lower()
    return "restricted" in lower and "unrestricted" not in lower


# ---------------------------------------------------------------------------
# Step 3 — Mojibake detection algorithm mirror
#
# Mirrors the logic in MojibakeDetectionThread.run() (step3_dialog.py).
# The six text fields checked, the ftfy call, and the row-numbering scheme
# are reproduced here exactly so tests run without launching the GUI.
# ---------------------------------------------------------------------------

#: Fields that Step 3 scans for mojibake (matches step3_dialog.py exactly)
MOJIBAKE_TEXT_FIELDS = [
    "Headline",
    "Caption-Abstract",
    "Source",
    "By-line",
    "By-lineTitle",
    "CopyrightNotice",
]


def scan_for_mojibake(rows: list[dict]) -> list[dict]:
    """
    Mirror of MojibakeDetectionThread.run() in step3_dialog.py.

    Args:
        rows: list of dicts as returned by csv.DictReader (header row excluded).

    Returns:
        List of problematic-record dicts, each with keys:
            row_num     – 1-based CSV row number (2 = first data row)
            object_name – value of the ObjectName field
            issues      – {field: {'original': str, 'suggested': str}}
    """
    import ftfy

    problematic_records = []

    for row_num, row in enumerate(rows, start=2):  # row 1 is the header
        issues = {}
        for field in MOJIBAKE_TEXT_FIELDS:
            if field in row and row[field]:
                original = row[field]
                fixed = ftfy.fix_text(original)
                if fixed != original:
                    issues[field] = {"original": original, "suggested": fixed}

        if issues:
            problematic_records.append(
                {
                    "row_num": row_num,
                    "object_name": row.get("ObjectName", "Unknown"),
                    "issues": issues,
                }
            )

    return problematic_records


# ---------------------------------------------------------------------------
# Step 1 — Excel validation algorithm mirrors
# (mirrors tools/file_manager.py FileManager.validate_hpm_excel_structure)
# ---------------------------------------------------------------------------

#: Required labels that must appear in the mapping row
REQUIRED_MAPPING_HEADERS = [
    "Title",
    "Accession Number",
    "Restrictions",
    "Scopenote",
    "Related Collection",
    "Source Photographer",
    "Institutional Creator",
]


def find_mapping_row(df) -> "int | None":
    """
    Mirror of the dynamic mapping-row search in file_manager.py and g2c.py.

    Scans rows 0-4 for a row whose first cell contains 'HST - DRUPAL FIELDS'.
    Returns the 0-based index of that row, or None if not found.
    """
    import pandas as pd

    for i in range(min(5, len(df))):
        first_cell = str(df.iloc[i, 0]).strip() if pd.notna(df.iloc[i, 0]) else ""
        if "HST - DRUPAL FIELDS" in first_cell:
            return i
    return None


def missing_mapping_headers(df, mapping_row_idx: int) -> list:
    """
    Mirror of the required-header check in file_manager.py.

    Returns a list of required headers absent from the mapping row
    (case-insensitive comparison).
    """
    headers = df.iloc[mapping_row_idx].fillna("").astype(str).str.strip().tolist()
    return [
        h for h in REQUIRED_MAPPING_HEADERS
        if not any(h.lower() == x.lower() for x in headers)
    ]


# ---------------------------------------------------------------------------
# Step 2 — g2c.py date-building algorithm mirror
# (mirrors get_date_from_columns closure inside export_to_csv in g2c.py)
# ---------------------------------------------------------------------------

def build_date_from_parts(month_str: str, day_str: str, year_str: str) -> tuple:
    """
    Mirror of get_date_from_columns() in g2c.py.

    Takes raw string values for month, day, year (as they come from the
    spreadsheet) and returns (iso_date, is_partial, reject_reason).

    is_partial is True when any component is 0/missing (partial date).
    reject_reason is "" on success, or a description if the date is invalid/absent.
    """

    def _safe_int(s: str) -> "int | None":
        """Convert string to int, handling float strings like '1975.0'."""
        if not s:
            return 0
        try:
            return int(s)
        except ValueError:
            try:
                return int(float(s))
            except (ValueError, TypeError):
                return None

    # Normalise nan/None strings
    def _clean(s: str) -> str:
        s = str(s).strip()
        return "" if s.lower() in ("nan", "none", "null") else s

    month_str = _clean(month_str)
    day_str   = _clean(day_str)
    year_str  = _clean(year_str)

    def _raw() -> str:
        return f"M={month_str or ''} D={day_str or ''} Y={year_str or ''}"

    year_int  = _safe_int(year_str)
    month_int = _safe_int(month_str)
    day_int   = _safe_int(day_str)

    if year_int is None:
        return ("", False, f"invalid date ({_raw()})")
    if month_int is None:
        return ("", False, f"invalid date ({_raw()})")
    if day_int is None:
        return ("", False, f"invalid date ({_raw()})")

    if year_int == 0 and month_int == 0 and day_int == 0:
        return ("", False, "no date data")

    if year_int  != 0 and year_int  <= 0:
        return ("", False, f"invalid date ({_raw()})")
    if month_int != 0 and not (1 <= month_int <= 12):
        return ("", False, f"invalid date ({_raw()})")
    if day_int   != 0 and not (1 <= day_int   <= 31):
        return ("", False, f"invalid date ({_raw()})")

    is_partial = (year_int == 0 or month_int == 0 or day_int == 0)
    return (f"{year_int:04d}-{month_int:02d}-{day_int:02d}", is_partial, "")


#: IPTC column mapping used by g2c.py (mapping-row label → CSV column name)
IPTC_COLUMN_MAP = {
    "Title":                "Headline",
    "Accession Number":     "ObjectName",
    "Restrictions":         "CopyrightNotice",
    "Scopenote":            "Caption-Abstract",
    "Related Collection":   "Source",
    "Source Photographer":  "By-line",
    "Institutional Creator":"By-lineTitle",
}


# ---------------------------------------------------------------------------
# Step 4 — TIFF bit depth conversion algorithm mirrors
# (mirrors BitDepthConversionThread logic in step4_dialog.py)
# ---------------------------------------------------------------------------

def is_16bit_tiff(bits_per_sample: str) -> bool:
    """
    Mirror of the 16-bit detection check in step4_dialog.py.

    Returns True when BitsPerSample contains '16' and does NOT contain '8'.
    """
    return "16" in bits_per_sample and "8" not in bits_per_sample


def scale_16bit_to_8bit(img_array) -> "np.ndarray":
    """
    Mirror of the pixel-scaling step in step4_dialog.py.

    Scales a numpy array from 16-bit range (0-65535) to 8-bit (0-255)
    by integer division by 256, then casts to uint8.
    """
    import numpy as np
    return (img_array / 256).astype(np.uint8)


def detect_converted_mode(arr) -> str:
    """
    Mirror of the image-mode selection logic in step4_dialog.py.

    Returns 'L' (grayscale), 'RGB', 'RGBA', or 'unknown' based on array shape.
    """
    if len(arr.shape) == 2:
        return "L"
    if len(arr.shape) == 3 and arr.shape[2] == 3:
        return "RGB"
    if len(arr.shape) == 3 and arr.shape[2] == 4:
        return "RGBA"
    return "unknown"


# ---------------------------------------------------------------------------
# Step 5 — Metadata embedding algorithm mirrors
# (mirrors MetadataEmbeddingThread logic in step5_dialog.py)
# ---------------------------------------------------------------------------

#: ObjectName values that indicate a header/artifact row rather than real data
ARTIFACT_PATTERNS = {
    "ObjectName", "Accession Number", "Local Identifier",
    "record.localIdentifier", "Headline", "Caption-Abstract",
    "Source", "By-line", "By-lineTitle", "CopyrightNotice",
    "DateCreated", "Credit", "SpecialInstructions",
}


def is_artifact_record(obj_name: str) -> bool:
    """
    Mirror of the artifact-pattern filter in step5_dialog.py.

    Returns True when obj_name is empty or matches a known header/artifact value.
    """
    return not obj_name.strip() or obj_name.strip() in ARTIFACT_PATTERNS


def convert_date_step5(date_str: str) -> str:
    """
    Mirror of the convert_date() closure in step5_dialog.py.

    Converts a raw date string from the CSV to ISO YYYY-MM-DD (or partial).
    Handles 8 distinct input patterns.
    """
    import re
    import datetime as dt

    if date_str == "None":
        return "0000-00-00"

    if re.match(r"\d{4}-\d{4}", date_str):
        year_range = date_str.split("-")
        return f"{year_range[1]}-00-00"

    if re.match(r"\d{1,2}/\d{1,2}/\d{2}$", date_str):
        parts = date_str.split("/")
        return f"20{parts[2]}-{parts[0]:0>2}-{parts[1]:0>2}"

    if re.match(r"c\. ?\d{4}", date_str):
        year = re.findall(r"\d{4}", date_str)[0]
        return f"{year}-00-00"

    if re.match(r"ca\. ?\d{4}", date_str):
        year = date_str.split(".")[1].strip()
        return f"{year}-00-00"

    if re.match(r"Ca\. ?\d{4}", date_str):
        year = date_str.split(".")[1].strip()
        return f"{year}-00-00"

    if re.match(r"\d{4}$", date_str):
        return f"{date_str}-00-00"

    if re.match(r"[A-Za-z]+, \d{2}/\d{2}/\d{4}", date_str):
        try:
            return dt.datetime.strptime(date_str, "%A, %m/%d/%Y").strftime("%Y-%m-%d")
        except ValueError:
            return date_str

    if re.match(r"[A-Za-z]+ \d{4}$", date_str):
        try:
            return dt.datetime.strptime(date_str, "%B %Y").strftime("%Y-%m-00")
        except ValueError:
            return date_str

    m = re.match(r"([A-Za-z]+) (\d{1,2}), (\d{4})", date_str)
    if m:
        try:
            return dt.datetime.strptime(date_str, "%B %d, %Y").strftime("%Y-%m-%d")
        except ValueError:
            return date_str

    return date_str


def is_verso_filename(filename: str) -> bool:
    """
    Mirror of the verso-file glob patterns in step5_dialog.py.

    Returns True when the filename stem contains '_verso' or '_Verso'
    and the extension is .tif or .tiff.
    """
    from pathlib import Path
    p = Path(filename)
    stem = p.stem
    ext  = p.suffix.lower()
    return ext in (".tif", ".tiff") and ("_verso" in stem or "_Verso" in stem)


# ---------------------------------------------------------------------------
# Step 6 — JPEG conversion mode-handling mirror
# (mirrors JpegConversionThread._convert_mode in step6_dialog.py)
# ---------------------------------------------------------------------------

def convert_mode_for_jpeg(img: "Image.Image") -> "Image.Image":
    """
    Mirror of the image-mode conversion logic in step6_dialog.py.

    Converts any PIL Image to RGB suitable for JPEG output:
      RGBA → RGB (white background composite)
      LA   → RGB (white background composite)
      P    → RGBA → RGB (white background composite)
      other → RGB (direct convert)
    """
    from PIL import Image

    if img.mode == "RGBA":
        background = Image.new("RGB", img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3])
        return background

    if img.mode == "LA":
        background = Image.new("RGB", img.size, (255, 255, 255))
        background.paste(img.convert("RGBA"), mask=img.split()[1])
        return background

    if img.mode == "P":
        rgba = img.convert("RGBA")
        background = Image.new("RGB", img.size, (255, 255, 255))
        background.paste(rgba, mask=rgba.split()[3])
        return background

    return img.convert("RGB")


def apply_mojibake_fixes(rows: list[dict], edits: dict[int, dict]) -> list[dict]:
    """
    Mirror of Step3Dialog._apply_fixes() write-back logic.

    Args:
        rows:  list of row dicts (header excluded), as read by csv.DictReader.
        edits: {row_num: {field: new_value}} — same structure as self.edits.

    Returns:
        New list of row dicts with edits applied.
    """
    import copy

    result = copy.deepcopy(rows)
    for row_num, field_edits in edits.items():
        data_index = row_num - 2          # row_num 2 → index 0
        if 0 <= data_index < len(result):
            for field, new_value in field_edits.items():
                result[data_index][field] = new_value
    return result
