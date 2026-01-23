# Fix: Google Sheets Permission Issues

## Problem
When running Step 2 (CSV Conversion), you receive this error:
```
HTTP Error: <HttpError 403 when requesting https://sheets.googleapis.com/v4/spreadsheets/...
returned "The caller does not have permission">
```

This means your Google API credentials don't have permission to access the specific spreadsheet.

## Solutions

### Option 1: Share the Spreadsheet (Recommended)

The easiest fix is to share the spreadsheet with the Google account you're using for authentication.

1. Open the Google Sheet in your browser:
   - Use the spreadsheet ID from the error message
   - URL format: `https://docs.google.com/spreadsheets/d/[SPREADSHEET_ID]/edit`
   - Example: `https://docs.google.com/spreadsheets/d/10SikKPjHj0zJJlZs1q8gjKPOrTrHwFURikcYonZyNxI/edit`

2. Click the **Share** button (top-right corner)

3. Add the email address of the Google account you authenticated with

4. Set permissions to at least **Viewer** (or **Editor** if you need write access)

5. Click **Send**

6. Try running Step 2 again

---

### Option 2: Re-authenticate with Correct Account

If you authenticated with the wrong Google account, delete the token files and re-authenticate.

**Step 1: Delete existing token files**

In PowerShell, run:
```powershell
Remove-Item "C:\Users\juren\Projects\HST-Metadata\Photos\Version-2\Framework\token_sheets.pickle" -ErrorAction SilentlyContinue
Remove-Item "C:\Users\juren\Projects\HST-Metadata\Photos\Version-2\Framework\token_drive_sheets.pickle" -ErrorAction SilentlyContinue
```

**Step 2: Run the GUI again**

```powershell
C:\Users\juren\winpython\WPy64-31201b5\python-3.12.0.amd64\python.exe C:\Users\juren\Projects\HST-Metadata\Photos\Version-2\Framework\gui\hstl_gui.py
```

**Step 3: Authenticate when prompted**

- A browser window will open
- **Sign in with the Google account that has access to the spreadsheet**
- Grant the requested permissions
- The token files will be recreated automatically

**Step 4: Try Step 2 again**

---

### Option 3: Verify Spreadsheet ID

Make sure you're using the correct spreadsheet ID.

1. Open the Google Sheet you want to access

2. Check the URL in your browser:
   ```
   https://docs.google.com/spreadsheets/d/[THIS_IS_THE_ID]/edit
   ```

3. Copy the ID from the URL

4. Verify this matches the ID shown in the error message

5. If different, update your batch configuration with the correct spreadsheet ID

---

## Prevention

To avoid this issue in the future:

1. **Always authenticate with the Google account that owns the spreadsheet**
   - Or an account that has been granted access

2. **Share spreadsheets before processing**
   - Share with the account you'll use for authentication
   - At minimum, grant **Viewer** permissions

3. **Keep token files backed up**
   - Once authenticated successfully, the `token_sheets.pickle` file contains your session
   - Back it up to avoid re-authenticating frequently

---

## Still Having Issues?

### Check Your Credentials File

Verify that this file exists in the Framework directory:
```
client_secret_562755451687-9rpcl9hgjpkkamhu935p5a1gqcj06ot7.apps.googleusercontent.com.json
```

### Check Token Files After Authentication

After successful authentication, these files should exist:
```
token_sheets.pickle
```
Or:
```
token_drive_sheets.pickle
```

### Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| "The caller does not have permission" | Account doesn't have access to spreadsheet | Share the spreadsheet (Option 1) |
| "Invalid authentication credentials" | Token expired or corrupted | Re-authenticate (Option 2) |
| "Requested entity was not found" | Wrong spreadsheet ID or it's an Excel file | Verify spreadsheet ID (Option 3) |
| "Client secret file not found" | Missing credentials file | Place client_secret file in Framework directory |

---

## Quick Fix Summary

**Most common solution:**

1. Delete token files: `Remove-Item *token*.pickle`
2. Run the GUI
3. Sign in with the correct Google account (one that has access to the spreadsheet)
4. Try Step 2 again

If that doesn't work, share the spreadsheet with your authenticated Google account.
