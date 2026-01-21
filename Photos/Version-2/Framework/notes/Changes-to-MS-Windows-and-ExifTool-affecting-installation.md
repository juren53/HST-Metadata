## Recent Changes to MS Windows and ExifTool affecting installations

The bizarre problems we encountered with ExifTool installs is due to a change in **recent Windows builds and how recent ExifTool Windows packages interact**.

Short version:
**Modern ExifTool Windows builds rely on companion files that Windows may block or fail to locate once the package is moved**, whereas older builds were effectively single-file and location-agnostic.

Here’s the full breakdown.

---

## 1. Old ExifTool Windows builds were effectively “portable”

Older Windows releases of ExifTool behaved like this:

* `exiftool.exe` was:

  * A **self-contained Perl executable** (packed with PAR / pp)
  * Or used **relative paths** to locate support files
* The `exiftool_files\` directory was optional or loosely coupled
* Windows did **not** aggressively block downloaded executables or DLL-like files

Result:

> You could unzip → move anywhere → run, and it “just worked”.

---

## 2. New ExifTool Windows packages are no longer fully self-contained

Recent ExifTool Windows distributions changed in important ways:

### A. The executable now depends on external files

* `exiftool.exe` dynamically loads modules and resources from:

  * `exiftool_files\`
* These files are expected to be:

  * In a **specific relative directory**
  * With **unchanged filenames and structure**

If that relationship breaks, ExifTool silently fails or exits immediately.

---

### B. Windows now enforces **Mark of the Web (MOTW)**

When you download the ZIP:

* Windows adds a hidden `Zone.Identifier` stream to:

  * `exiftool.exe`
  * **every file in `exiftool_files\`**
* When you extract:

  * Those marks are **inherited**
* When you move the files:

  * Windows may block dynamic loading of marked files

Symptoms:

* Runs only from the original extraction folder
* Fails when moved
* No error message

This did **not exist** (or was much looser) years ago.

---

## 3. Why it runs only from the original extract location

Common reasons it works *only there*:

### 1️⃣ Relative-path assumptions

ExifTool now expects:

```
exiftool.exe
exiftool_files\
```

to exist **exactly as extracted**, not relocated arbitrarily.

### 2️⃣ Blocked companion files

Even if `exiftool.exe` is unblocked:

* DLL-like `.pm` or resource files remain blocked
* Windows refuses to load them after relocation

### 3️⃣ SmartScreen / Application Reputation

Moving an unsigned executable:

* Changes how Windows evaluates trust
* Can cause silent execution failures

---

## 4. How to make it portable again (reliably)

### ✅ Option A: Unblock before extracting

1. Right-click the ZIP
2. Properties → **Unblock**
3. Extract
4. Move anywhere you like

This removes MOTW from *all* files.

---

### ✅ Option B: Unblock recursively after extraction

From PowerShell:

```powershell
Get-ChildItem exiftool -Recurse | Unblock-File
```

Then move the folder.

---

### ✅ Option C: Install via PATH (recommended)

Put it somewhere stable:

```
C:\Tools\ExifTool\
```

Add that directory to `PATH`.

This avoids relocation entirely.

---

### ✅ Option D: Use the standalone older build

If portability matters more than features:

* Older ExifTool Windows executables (pre–12.60-ish) are truly portable
* They do not depend on external directories

---

## 5. This is a general Windows trend (not ExifTool-specific)

You’re seeing a broader shift:

* Tighter execution controls
* More dynamic loading restrictions
* Less tolerance for “loose” binaries

Other tools affected:

* ffmpeg builds
* ImageMagick
* Perl-packed executables
* Python embeddables

---

## Bottom line

You’re not imagining it.

**ExifTool didn’t “break” — Windows and ExifTool packaging both changed.**
Modern builds are:

* More modular
* More security-restricted
* Less location-agnostic




