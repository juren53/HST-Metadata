# Google Credentials Setup for Step 2

Step 2 (CSV Conversion) requires Google API credentials to access Google Sheets.

## Required Files

1. **`client_secret_562755451687-9rpcl9hgjpkkamhu935p5a1gqcj06ot7.apps.googleusercontent.com.json`**
   - This is your Google OAuth client secret file
   - Obtained from Google Cloud Console

2. **`token.json.backup`** or generated **`token_sheets.pickle`**
   - Contains your authenticated session token
   - Generated after first authentication

## File Locations

### When Running from Source (Development)

Place the credential files in the **Framework directory**:
```
C:\Users\jimur\Projects\HST-Metadata\Photos\Version-2\Framework\
├── client_secret_562755451687-9rpcl9hgjpkkamhu935p5a1gqcj06ot7.apps.googleusercontent.com.json
└── token.json.backup (or token_sheets.pickle)
```

Run with:
```powershell
python .\gui\hstl_gui.py
```

### When Running Compiled Executable

Place the credential files in the **same directory as the .exe file**:
```
dist\HSTL_Photo_Framework_GUI\
├── HSTL_Photo_Framework_GUI.exe
├── _internal\
├── client_secret_562755451687-9rpcl9hgjpkkamhu935p5a1gqcj06ot7.apps.googleusercontent.com.json
└── token.json.backup (or token_sheets.pickle)
```

The executable's working directory becomes the directory containing the `.exe` file.

## First-Time Authentication

If you don't have `token_sheets.pickle` yet:

1. Place only the `client_secret_*.json` file in the appropriate directory
2. Run Step 2 for the first time
3. A browser window will open asking you to authenticate
4. After authentication, `token_sheets.pickle` will be created automatically
5. Future runs will use the saved token

## Troubleshooting

### "Failed to import g2c module"
- Ensure `g2c.py` is in the Framework directory (for source) or `_internal` (for compiled)

### "Client secret file not found"
- Verify the credential file is in the **same directory** as the executable
- Check the filename exactly matches (it's very long!)

### "Authentication failed"
- Delete `token_sheets.pickle` and `token_drive_sheets.pickle`
- Run Step 2 again to re-authenticate

## Security Note

⚠️ **Do NOT commit these credential files to git!**

They are listed in `.gitignore` to prevent accidental commits. These files contain sensitive authentication data.

## Deployment Checklist

When distributing the compiled executable:

- [ ] Copy the compiled executable from `dist\HSTL_Photo_Framework_GUI\`
- [ ] Include the `_internal` folder with the executable
- [ ] Add your `client_secret_*.json` file to the same directory as the .exe
- [ ] Either include your `token_sheets.pickle` (if pre-authenticated) OR let users authenticate on first run
- [ ] Provide this README to users
