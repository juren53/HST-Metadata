# Plan: Sigstore Integration with GitHub Actions for PyInstaller .exe Signing

## Overview

This plan outlines integrating Sigstore into an existing GitHub Actions workflow to cryptographically sign PyInstaller-compiled Windows executables released via GitHub Releases. Sigstore provides free, keyless code signing using GitHub's OIDC (OpenID Connect) identity.

## Goals

1. Sign Windows `.exe` files automatically on each release
2. Provide cryptographic verification that releases are authentic
3. Generate Sigstore bundles attached to GitHub Releases
4. Enable users to verify downloads using cosign or sigstore-python

---

## Phase 1: Prerequisites

### 1.1 Repository Requirements
- GitHub repository (public or private with paid GitHub Actions)
- Existing GitHub Actions workflow for building releases
- PyInstaller or similar toolchain producing Windows executables

### 1.2 No External Dependencies Required
- No certificate purchase needed
- No secrets or keys to manage
- GitHub OIDC provides identity verification automatically

---

## Phase 2: GitHub Actions Workflow Setup

### 2.1 Add Required Permissions

In the workflow YAML file, add these permissions:

```yaml
permissions:
  contents: read
  id-token: write  # Required for OIDC keyless signing
```

### 2.2 Install Sigstore Tool

Add a step to install sigstore-python or cosign in the workflow:

**Option A: sigstore-python (Recommended for files)**
```yaml
- name: Install sigstore-python
  uses: sigstore/gh-action-sigstore-python@v3.2.0
```

**Option B: cosign (For cross-platform)**
```yaml
- name: Install cosign
  uses: sigstore/cosign-installer@v4.0.0
```

### 2.3 Sign the Executable

After PyInstaller builds the `.exe`, add the signing step:

**Using sigstore-python:**
```yaml
- name: Sign executable with Sigstore
  uses: sigstore/gh-action-sigstore-python@v3.2.0
  with:
    inputs: dist/your-app.exe
    release-signing-artifacts: true
```

**Using cosign:**
```yaml
- name: Sign with cosign (keyless)
  run: |
    cosign sign --keyless dist/your-app.exe
  env:
    COSIGN_EXPERIMENTAL: "true"
```

---

## Phase 3: Release Automation

### 3.1 Trigger on Release

Modify the workflow to trigger on release events:

```yaml
on:
  release:
    types: [published]
```

### 3.2 Upload Artifacts to Release

The signing step generates:
- `.sig` (signature file)
- `.crt` (signing certificate)
- `.bundle` (Sigstore bundle - optional)

Upload these as release assets:

```yaml
- name: Upload Sigstore artifacts to Release
  if: github.event_name == 'release'
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    gh release upload "${{ github.event.release.tag_name }}" \
      dist/your-app.exe.sig \
      dist/your-app.exe.crt \
      --repo ${{ github.repository }}
```

---

## Phase 4: User Verification Process

### 4.1 For Users (Documentation)

Users can verify the authenticity of downloaded files using cosign:

```bash
# Install cosign
brew install cosign  # macOS
# or: choco install cosign -y  # Windows

# Verify the executable
cosign verify-blob \
  --signature your-app.exe.sig \
  --certificate your-app.exe.crt \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com \
  --certificate-identity "https://github.com/your-org/your-repo/.github/workflows/release.yml@refs/tags/v1.0.0" \
  your-app.exe
```

### 4.2 Simplified Verification (Optional)

Provide a verification script in the release:

```powershell
# verify.ps1
$exe = "your-app.exe"
$sig = "$exe.sig"
$crt = "$exe.crt"

cosign verify-blob --signature $sig --certificate $crt $exe
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Signature verified - file is authentic"
} else {
    Write-Host "✗ Verification failed - file may be tampered"
    exit 1
}
```

---

## Phase 5: Sample Complete Workflow

```yaml
name: Build and Sign Release

on:
  release:
    types: [published]

permissions:
  contents: read
  id-token: write

jobs:
  build-and-sign:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v5
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install pyinstaller
      
      - name: Build executable
        run: |
          pyinstaller --onefile --name your-app your_app.py
        env:
          PYINSTALLER_EXTRA: ...
      
      - name: Install sigstore-python
        uses: sigstore/gh-action-sigstore-python@v3.2.0
      
      - name: Sign the executable
        uses: sigstore/gh-action-sigstore-python@v3.2.0
        with:
          inputs: dist/your-app.exe
          release-signing-artifacts: true
      
      - name: Upload to Release
        if: github.event_name == 'release'
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          gh release upload "${{ github.event.release.tag_name }}" \
            dist/your-app.exe \
            dist/your-app.exe.sig \
            dist/your-app.exe.crt \
            --repo ${{ github.repository }}
```

---

## Phase 6: Documentation for Users

### 6.1 Update README.md

Add a verification section:

```markdown
## Verifying Downloads

This project uses Sigstore for cryptographic signing. To verify the authenticity of your download:

1. Install [cosign](https://docs.sigstore.dev/cosign/installation/)
2. Download the `.exe`, `.sig`, and `.crt` files from the release
3. Run verification:

   ```bash
   cosign verify-blob \
     --signature your-app.exe.sig \
     --certificate your-app.exe.crt \
     --certificate-oidc-issuer https://token.actions.githubusercontent.com \
     --certificate-identity "https://github.com/your-org/your-repo/.github/workflows/release.yml@refs/tags/v1.0.0" \
     your-app.exe
   ```

For Windows, use the provided `verify.ps1` script or install cosign via Chocolatey.
```

---

## Limitations and Trade-offs

| Aspect | Sigstore | Traditional Certificate |
|--------|----------|------------------------|
| Cost | Free | $200-400/year |
| SmartScreen | Still shows warning | EV: instant, OV: builds over time |
| Verification | Cryptographic proof | Certificate chain |
| User effort | Requires cosign install | Built-in Windows trust |

---

## Estimated Implementation Time

- **Setup**: 30-60 minutes
- **Testing**: 1 release cycle
- **User verification docs**: 15 minutes

---

## Alternative: Build Provenance Attestation

For additional security, consider adding build provenance attestation using `actions/attest-build-provenance`:

```yaml
- uses: actions/attest-build-provenance@v1
  with:
    subject-path: 'dist/your-app.exe'
```

This proves the artifact was built from your specific source code in GitHub.

---

## Next Steps

1. Review existing GitHub Actions workflow
2. Decide on sigstore-python vs cosign
3. Implement the workflow changes
4. Test with a pre-release
5. Add verification instructions to README
