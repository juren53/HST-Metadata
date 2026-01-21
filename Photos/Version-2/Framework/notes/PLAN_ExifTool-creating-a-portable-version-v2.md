# PLAN v2: Creating a Portable Single-File ExifTool Executable

## Executive Summary

ExifTool recently changed from a single-file distribution to a multi-file format requiring an `exiftool_files\` directory. This creates compatibility issues with Windows security (Mark-of-the-Web) and complicates distribution within the HPM framework.

**HPM-Specific Context**: HPM uses ExifTool exclusively for applying IPTC metadata tags to scanned historical TIFFs and JPEGs. New camera RAW format support is not required. This significantly simplifies our options.

**Recommendation**: Use ExifTool v12.60 (last standalone version) as the primary solution. The IPTC functionality required by HPM is unchanged in newer versions.

---

## Background

### Current Situation
- **Modern ExifTool** (v12.60+): Uses `exiftool.exe` + `exiftool_files\` directory
- **Windows Security Issues**: MOTW (Mark-of-the-Web) blocks dynamic loading of companion files
- **Distribution Complexity**: Requires maintaining directory structure and dependencies
- **HPM Impact**: Complicates automated setup and portable deployment

### HPM Requirements (Clarified)
- Apply IPTC metadata to scanned TIFF images
- Apply IPTC metadata to JPEG images
- Batch processing capability
- Portable deployment (no installation required)
- **NOT Required**: Camera RAW support, video metadata, new format support

### Why v12.60 Is Sufficient for HPM

Analysis of ExifTool changelog (v12.60 through v13.42) reveals:

| Change Category | Versions Affected | HPM Impact |
|-----------------|-------------------|------------|
| New camera RAW formats | 12.61-13.42 | **None** - not using RAW files |
| IPTC Video Metadata | 12.45, 12.48 | **None** - not using video |
| AI metadata properties | 2025.1 standard | **None** - historical photos |
| CharsetFileName UTF-8 | 13.01 | **Low** - only affects non-ASCII filenames |
| Core IPTC tag support | Unchanged | **Full compatibility** |
| TIFF/JPEG write support | Unchanged | **Full compatibility** |

---

## Recommended Approach

### Primary Solution: ExifTool v12.60 Standalone

**Overview**: Deploy ExifTool v12.60—the last truly portable single-file version—as HPM's standard ExifTool distribution.

**Rationale**:
- All IPTC metadata operations required by HPM work identically
- True portability (single file, drag-and-drop anywhere)
- No MOTW issues with companion files
- Proven reliability
- Minimal maintenance overhead

**Implementation Steps**:
1. Download ExifTool v12.60 standalone executable
2. Verify SHA256 checksum against official release
3. Test all HPM metadata operations (see Test Plan below)
4. Replace current version in HPM framework
5. Update setup scripts to remove directory dependency
6. Document the version lock decision

---

## Fallback Options

### Fallback A: Smart Installer for Modern ExifTool

**When to Use**: If a critical bug is discovered in v12.60 that affects HPM operations, or if future IPTC standard changes require newer ExifTool.

**Implementation**:
```powershell
# Automatic MOTW removal after extraction
Get-ChildItem $installDir -Recurse | Unblock-File

# Verify critical files
$requiredFiles = @("exiftool.exe", "exiftool_files")
foreach ($file in $requiredFiles) {
    $fullPath = Join-Path $installDir $file
    if (-not (Test-Path $fullPath)) {
        throw "Required file missing: $file"
    }
}
```

**Package Structure**:
```
exiftool_portable/
├── exiftool.exe
├── exiftool_files/
│   └── (all required files)
├── setup.ps1
└── install.bat
```

### Fallback B: Strawberry Perl Portable + ExifTool Script

**When to Use**: If Windows security changes block all packed executables, or if custom ExifTool modifications become necessary.

**Implementation**:
1. Bundle Strawberry Perl Portable (~100MB)
2. Include ExifTool Perl script (not compiled)
3. Create wrapper batch file:
```batch
@echo off
"%~dp0perl\perl\bin\perl.exe" "%~dp0exiftool\exiftool" %*
```

**Benefits**:
- Always runs latest ExifTool version
- No compilation/packing issues
- Full Perl flexibility for customization

**Drawbacks**:
- Larger distribution size (~100MB vs ~8MB)
- More complex directory structure

### Fallback C: Custom PAR::Packer Build

**When to Use**: Only if specific customizations to ExifTool are required that can't be achieved otherwise.

**Prerequisites**:
- StrawberryPerl installation
- PAR::Packer module
- ExifTool source distribution

**Build Command** (Windows-compatible):
```cmd
pp -o exiftool_hpm.exe ^
   --compress=6 ^
   --scan ^
   --lib=lib ^
   --module=Image::ExifTool ^
   --module=Image::ExifTool::IPTC ^
   --module=Image::ExifTool::EXIF ^
   --module=Image::ExifTool::XMP ^
   --module=Encode ^
   --module=Encode::UTF8 ^
   exiftool
```

**Note**: This approach has higher maintenance overhead and should only be pursued if simpler options fail.

---

## Implementation Plan

### Phase 1: Deploy v12.60 Standalone

**Objectives**:
- Deploy portable ExifTool v12.60
- Validate all HPM operations
- Update documentation

**Tasks**:
- [ ] Download ExifTool v12.60 from official archive
- [ ] Verify file integrity (SHA256)
- [ ] Run HPM IPTC test suite (see below)
- [ ] Update `Setup-ExifTool.ps1` for single-file operation
- [ ] Update `EXIFTOOL_SETUP_README.md`
- [ ] Deploy to test users

**Test Plan for IPTC Operations**:
```cmd
REM Test 1: Write IPTC tags to TIFF
exiftool -IPTC:Headline="Test" -IPTC:Caption-Abstract="Description" test.tif

REM Test 2: Write IPTC tags to JPEG
exiftool -IPTC:Headline="Test" -IPTC:Keywords="keyword1;keyword2" test.jpg

REM Test 3: Read IPTC tags
exiftool -IPTC:all test.tif

REM Test 4: Batch operation
exiftool -IPTC:Credit="Archive" *.tif

REM Test 5: UTF-8 content with proper encoding
exiftool -charset iptc=UTF8 -codedcharacterset=UTF8 -IPTC:Caption-Abstract="Test with accents: café, niño, über" test.tif

REM Test 6: Preserve existing metadata
exiftool -IPTC:Headline="New" -overwrite_original test.tif

REM Test 7: Read with explicit encoding (mojibake fix)
exiftool -charset iptc=UTF8 test_legacy.tif

REM Test 8: Verify CodedCharacterSet is written
exiftool -CodedCharacterSet test.tif

REM Test 9: Read file with known mojibake and verify fix
exiftool -charset iptc=Latin test_mojibake_sample.tif
```

**Success Criteria**:
- All nine test operations complete without error
- Metadata is correctly written and readable
- UTF-8 characters display correctly (Test 5)
- CodedCharacterSet shows "UTF8" after write (Test 8)
- Mojibake samples render correctly with appropriate -charset flag (Test 7, 9)
- No file corruption
- Batch operations process all files

### Phase 2: Establish Maintenance Protocol

**Objectives**:
- Monitor for security issues
- Document version lock rationale
- Plan periodic review

**Tasks**:
- [ ] Document version lock decision and rationale
- [ ] Subscribe to ExifTool security announcements
- [ ] Create annual review checklist
- [ ] Document fallback activation triggers

**Annual Review Checklist**:
1. Check ExifTool security advisories since last review
2. Review IPTC standard changes
3. Test current HPM operations still work
4. Evaluate if upgrade is warranted
5. Document review findings

**Triggers for Fallback Activation**:
- Critical security vulnerability in v12.60
- IPTC standard change requiring newer ExifTool
- Bug affecting HPM operations with no workaround
- Windows security change blocking v12.60

---

## Technical Considerations

### Security

1. **Version Lock Risk**: Using an older version means missing security patches
   - **Mitigation**: Monitor ExifTool security announcements; ExifTool processes trusted local files only, reducing attack surface

2. **File Integrity**: Ensure downloaded executable is authentic
   - **Mitigation**: Verify SHA256 checksum against official release

3. **MOTW**: Single-file executable avoids companion file blocking
   - **Mitigation**: Built into the solution

### Compatibility

1. **IPTC Standard**: Core IPTC-IIM tags unchanged for decades
   - Future changes likely additive, not breaking

2. **File Formats**: TIFF and JPEG handling is mature, stable code
   - Extremely unlikely to have breaking changes

3. **Windows Versions**: v12.60 supports Windows 7 through 11
   - No compatibility concerns for modern systems

### Character Encoding and Mojibake

**Important**: Historical photos may contain metadata with character encoding issues (mojibake). This is **not a version-specific issue**—ExifTool's IPTC encoding support has been stable since v6.86 (over a decade ago). The v13.01 `CharsetFileName` change only affects filenames, not metadata content.

#### How IPTC Encoding Works

IPTC metadata has an inherent encoding ambiguity:

| Scenario | ExifTool Assumption | Result |
|----------|---------------------|--------|
| No `CodedCharacterSet` tag | Windows Latin1 (cp1252) | Mojibake if actually UTF-8 |
| `CodedCharacterSet=UTF8` | UTF-8 | Correct display |
| `CodedCharacterSet=ESC % G` | UTF-8 (escape sequence) | Correct display |

#### Common Mojibake Causes in Historical Photos

1. **Missing CodedCharacterSet** - Original software didn't set encoding indicator
2. **Wrong CodedCharacterSet** - Tag says Latin1 but content is UTF-8 (or vice versa)
3. **Double-encoding** - UTF-8 bytes interpreted as Latin1, then re-encoded as UTF-8

#### v12.60 Encoding Commands (Fully Supported)

```cmd
REM Read IPTC assuming UTF-8 (fixes mojibake when UTF-8 stored without CodedCharacterSet)
exiftool -charset iptc=UTF8 photo.tif

REM Read IPTC assuming Latin1
exiftool -charset iptc=Latin photo.tif

REM Write with proper UTF-8 encoding (recommended for all new metadata)
exiftool -charset iptc=UTF8 -codedcharacterset=UTF8 -IPTC:Caption="Café" photo.tif

REM Check current encoding setting
exiftool -CodedCharacterSet photo.tif

REM Diagnose encoding by viewing raw bytes
exiftool -b -IPTC:Caption-Abstract photo.tif > caption_bytes.bin
```

#### HPM Encoding Recommendations

1. **Document original encoding** - Determine what encoding the original scanning/cataloging software used
2. **Detect missing CodedCharacterSet** - Create a script to identify photos without encoding tags
3. **Standardize on UTF-8** - Always set `-codedcharacterset=UTF8` when writing new metadata
4. **Test with known mojibake samples** - Include encoding edge cases in validation testing

#### Encoding Detection Script

```cmd
REM Find files missing CodedCharacterSet (potential encoding issues)
exiftool -if "not defined $CodedCharacterSet" -filename -r /path/to/photos

REM Find files with non-UTF8 CodedCharacterSet
exiftool -if "$CodedCharacterSet and $CodedCharacterSet ne 'UTF8'" -filename -CodedCharacterSet -r /path/to/photos
```

**Conclusion**: v12.60 has complete encoding support. Mojibake issues stem from metadata creation practices, not ExifTool version.

---

## Risk Assessment

### Low Risks (Acceptable)
- **Missing new camera RAW support**: Not applicable to HPM use case
- **Missing video metadata features**: Not applicable to HPM use case
- **Older version perception**: Justified by stability requirements

### Medium Risks (Monitored)
- **Security vulnerabilities**: Monitor announcements, fallback plan ready
- **IPTC standard changes**: Annual review, unlikely to be breaking

### Mitigated Risks
- **MOTW blocking**: Eliminated by single-file approach
- **Distribution complexity**: Eliminated by single-file approach
- **Setup failures**: Reduced by simpler deployment

---

## Success Criteria

### Functional Requirements
- ExifTool runs from any directory without installation
- All HPM IPTC metadata operations work correctly
- No Windows security warnings or blocks
- Simple deployment (single file copy)

### Operational Requirements
- Clear documentation of version lock decision
- Defined triggers for fallback activation
- Annual review process established
- Fallback options documented and tested

---

## Appendix: Version Information

### ExifTool v12.60 Details
- **Release Date**: March 2024 (verify against official records)
- **Distribution**: Single standalone executable
- **Size**: ~8MB
- **Official Source**: https://exiftool.org/

### IPTC Tags Used by HPM
| Tag | Field Name | Usage |
|-----|------------|-------|
| 2:05 | ObjectName | Image title |
| 2:55 | DateCreated | Original date |
| 2:80 | By-line | Creator/photographer |
| 2:85 | By-lineTitle | Creator title |
| 2:90 | City | Location city |
| 2:95 | Province-State | Location state |
| 2:101 | Country | Location country |
| 2:105 | Headline | Brief synopsis |
| 2:110 | Credit | Provider credit |
| 2:115 | Source | Original source |
| 2:116 | CopyrightNotice | Copyright |
| 2:120 | Caption-Abstract | Description |
| 2:25 | Keywords | Subject keywords |

All tags above are fully supported in ExifTool v12.60.

---

**Document Created**: January 21, 2026
**Version**: 2.1
**Last Updated**: January 21, 2026
**Author**: HPM Development Team
**Status**: Ready for Implementation
**Supersedes**: PLAN_ExifTool-creating-a-portable-version.md (v1)

### Revision History
| Version | Date | Changes |
|---------|------|---------|
| 2.0 | 2026-01-21 | Initial v2 based on HPM-specific requirements analysis |
| 2.1 | 2026-01-21 | Added Character Encoding and Mojibake section; expanded test plan with encoding tests |
