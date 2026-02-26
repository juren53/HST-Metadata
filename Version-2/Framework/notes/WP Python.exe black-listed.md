## WP Python.exe black-listed.md

JAU:

I am attempting to understand and navigate around the bizarre world of MS defender as I support a client in an enterprise environment.  With your help, we have navigated around the MOTW issues with executable code I have delivered to them via GitHub.  It was marked and we were able to unmark it via properties.  But now we face a similar problem wth WinPython's python.exe file.  After installing WinPython on several machines at the client site, one machine the user received a MS 'blue popup message' saying this code [python.exe] can not be run on this machine.   There is no place in python.exe properties to 'un mark' so this feels different than a MOTW issue.  What can we do.  Local IT has not gotten back to us after 3-4 weeks reporting this.

Supporting enterprise environments can often feel like playing a high-stakes game of "Whack-A-Mole" with security policies. Since you aren't seeing the "Unblock" checkbox in the file properties, you've graduated from a simple MOTW (Mark of the Web) issue to something deeper in the Windows security stack.

Gemini:

Given that it's a "blue popup," you are likely hitting **Microsoft Defender SmartScreen** or **Windows 11 App Control**, but the lack of an override suggests a specific policy is at play.

---

## Why the "Unblock" Checkbox is Missing

If you don't see the unblock option, it usually means one of three things:

1. **The file is already "unblocked":** But the system is still blocking it for a different reason (like a hash mismatch or signature issue).
2. **Inheritance:** The entire folder or the `.7z`/`.exe` installer was already trusted, so the individual `python.exe` doesn't carry the "Zone.Identifier" alternate data stream.
3. **Execution Policy:** A Group Policy (GPO) or Intune policy is preventing unsigned or "unrecognized" binaries from running, regardless of their origin.

---

## Potential Solutions to Bypass the Block

### 1. Check the "Reputation-based Protection"

If this is SmartScreen, it may be blocking the file because it hasn't seen this specific build of WinPython enough times to "trust" it.

* Go to **Windows Security** > **App & browser control** > **Reputation-based protection settings**.
* Check if **Check apps and files** is set to "Block."
* *Note:* If these are greyed out, Local IT has locked these via GPO.

### 2. The PowerShell "Unblock-File" Command

Sometimes the GUI hides the MOTW attribute, but the system still sees it. You can force a recursive unblock on the entire WinPython directory.

* Open PowerShell as an Administrator.
* Run the following command:
`Get-ChildItem -Path "C:\Path\To\WinPython" -Recurse | Unblock-File`

### 3. Add a Defender Exclusion

If the "blue box" is actually a Defender block (and not a SmartScreen reputation block), you can try to exclude the folder.

* Go to **Windows Security** > **Virus & threat protection** > **Manage settings** > **Exclusions**.
* Add the root folder of the WinPython installation.

### 4. Verify Digital Signatures

WinPython's binaries are sometimes unsigned or self-signed. Windows Enterprise environments often use **AppLocker** or **Windows Defender Application Control (WDAC)**.

* Right-click `python.exe` > **Properties** > **Digital Signatures**.
* If the tab is missing, the file is unsigned. Many enterprise policies are set to "Allow only signed code." In this case, no amount of "unblocking" will help; Local IT must whitelist the file hash or the folder path.

---

## The "Client Site" Reality Check

Since Local IT hasn't responded in a month, here is the "peer-to-peer" advice: **This looks like a WDAC (Windows Defender Application Control) or AppLocker block.** In modern enterprise setups, IT departments move toward a "Zero Trust" model where any executable not explicitly on a "known-good" list is killed on sight. If this is the case, your only real move is to provide the **SHA-256 hash** of the `python.exe` to their IT team and ask them to add it to their "Allow" policy.

### Quick Diagnostic

To confirm if it's a policy block, check the **Event Viewer**:

1. Open **Event Viewer**.
2. Navigate to: `Applications and Services Logs` > `Microsoft` > `Windows` > `AppLocker` (or `CodeIntegrity`).
3. Look for "Error" or "Warning" events at the exact time you tried to run Python. It will tell you exactly which policy stopped it.

**Would you like me to help you draft a specific technical request for their IT team, including the file hashes and Event Viewer logs to speed up their 4-week delay?**

The fact that `pythonw.exe` works while `python.exe` is blocked is the "smoking gun" that points to a specific type of security logic rather than a blanket blacklist of your software.

Here is the breakdown of what is likely happening under the hood:

### 1. Reputation-Based "Blacklisting" (SmartScreen)

It is highly unlikely that someone at the client site manually blacklisted your specific `python.exe`. Instead, you are likely hitting **Microsoft Defender SmartScreen's "Reputation" service**.

* **How it works:** SmartScreen isn't just looking for "bad" code; it’s looking for "known" code. `pythonw.exe` and `python.exe` are technically different files with different digital fingerprints (hashes).
* **Why one works and not the other:** It’s possible that `pythonw.exe` from your WinPython distribution matches a hash already seen and "cleared" by Microsoft's cloud in other environments. Your specific `python.exe` might be a slightly different build or version that hasn't hit the "threshold of trust" yet.
* **The "Blue Popup":** If the message says *"Windows protected your PC,"* that is 100% a SmartScreen reputation block.

### 2. Behavioral/ASR Rule Blocking (The "Console" Factor)

The primary difference between `python.exe` and `pythonw.exe` is that the former requests a **Windows Console (Command Prompt)** and the latter does not.

* **Attack Surface Reduction (ASR):** Microsoft Defender has a specific enterprise rule called **"Block executable content from email client and webmail."** Even if you didn't email it, if the file has any residual MOTW metadata, Defender treats it with extreme suspicion.
* **The Logic:** Security suites are often tuned to be more aggressive toward console-based apps because they are the primary vehicle for "Living off the Land" (LotL) attacks (where a script is used to download further malware). `pythonw.exe` (the GUI version) is often treated more like a standard desktop application.

### 3. Header/Metadata Analysis

It is **not** a metadata header "change" in the sense of the file being corrupted. However, Windows Enterprise environments use **AppLocker** or **WDAC (Windows Defender Application Control)**.

* These tools check the **Digital Signature**. If the `python.exe` in your WinPython folder is not signed by a "Trusted Publisher" (like the Python Software Foundation), or if the signature was stripped/invalidated during the move, the system will kill it.
* **Why `pythonw.exe` works:** Check the properties of both. It is possible `pythonw.exe` is signed while `python.exe` is not, or the client's IT has a rule that says "Allow unsigned GUI apps, but block unsigned Console apps."

---

## How to confirm and fix this without IT

### Check for the "Hidden" MOTW

Even if the "Unblock" checkbox is missing in the GUI, the "Zone.Identifier" might still be stuck in the file's **Alternate Data Streams (ADS)**. This happens frequently in enterprise environments where the GUI is restricted.

Run this in PowerShell to see if the block is still there:

```powershell
Get-Item .\python.exe -Stream "Zone.Identifier"

```

* **If it returns an error:** There is no MOTW; it's a policy block.
* **If it returns data:** It’s still marked as "from the web." Use `Unblock-File .\python.exe` to kill it.

### The "Copy-Paste" Trick

Sometimes, moving a file into a "user-controlled" directory (like `Documents`) and then copying it back can strip certain inherited permissions or block flags that the `Properties` menu won't show you.

### Compare Digital Signatures

Right-click both `python.exe` and `pythonw.exe` and go to **Properties > Digital Signatures**.

* If `pythonw.exe` has a signature and `python.exe` does not (or it says the signature is invalid), that is exactly why the "Blue Box" is appearing.

**Would you like me to provide a "Letter to IT" template that uses the specific language needed to bypass their ticketing filter?** (e.g., mentioning *ASR rules* and *SHA-256 hashes* usually gets a faster response than "the app doesn't work").

----------------------

Since you are trying to stay "under the radar" and solve this locally, you need a way to see exactly which "silent" judge is blocking your code. In an enterprise environment, a file can be blocked by several overlapping systems that don't always talk to each other.

Here is a toolkit for diagnosing and (where possible) fixing this from an end-user perspective.

---

## 1. The "Why Am I Blocked?" Diagnostic

Before trying to fix it, you need to know which security layer is the culprit. Windows logs every block event, but usually hides them from the standard "System" or "Application" logs.

### The Event Viewer "Golden Paths"

Open **Event Viewer** (`eventvwr.msc`) and navigate to these three specific locations. Look for events timestamped at the moment you tried to run `python.exe`:

* **For AppLocker (The most likely culprit):**
`Applications and Services Logs` > `Microsoft` > `Windows` > `AppLocker` > `EXE and DLL`
* *Look for:* **Event ID 8004** (Blocked) or **8003** (Would be blocked).


* **For WDAC (Windows Defender Application Control):**
`Applications and Services Logs` > `Microsoft` > `Windows` > `CodeIntegrity` > `Operational`
* *Look for:* **Event ID 3077** (Blocked by policy).


* **For Defender ASR (Attack Surface Reduction):**
`Applications and Services Logs` > `Microsoft` > `Windows` > `Windows Defender` > `Operational`
* *Look for:* **Event ID 1121**.



---

## 2. PowerShell "Self-Service" Fixes

If you find that the file is not blocked by a hard IT policy (AppLocker), but rather by a "Reputation" or "Zone" issue, these commands can often clear the flag.

### Force-Remove the Web Flag

Sometimes the "Unblock" button is missing from Properties, but the metadata is still there. This command nukes the "Mark of the Web" for the entire folder:

```powershell
Get-ChildItem -Path "C:\Your\WinPython\Path" -Recurse | Unblock-File

```

### The "Null-Redirect" Trick

If a file is blocked due to a specific "Zone.Identifier" stream that `Unblock-File` can't see, you can manually overwrite the stream with nothing:

```powershell
Set-Content -Path "C:\Path\To\python.exe" -Stream "Zone.Identifier" -Value $null

```

---

## 3. Why `pythonw.exe` works (and how to use it)

The fact that `pythonw.exe` (the "windowed" version) works is a massive clue. It suggests the security policy is specifically targeting **Console Applications**.

### Legal "Workaround" Scripts

If you must use `python.exe` (e.g., you need to see terminal output), you can try creating a simple **Batch wrapper** or a **PowerShell alias**. Sometimes, launching the executable as a child of a "trusted" process (like PowerShell) bypasses simple path-based blocks.

**Try running it like this in a terminal:**

```powershell
Start-Process -FilePath "C:\Path\To\python.exe" -ArgumentList "--version" -Wait

```

If this works, you can create a shortcut that uses `powershell.exe` to launch your python script, effectively "masking" the initial execution from certain basic ASR rules.

---

## 4. The "Hash Verification" Tool

If IT asks for proof that the file is safe, or if you want to see if the file was modified/corrupted (which triggers Defender), use this to get the fingerprint:

```powershell
Get-FileHash -Algorithm SHA256 "C:\Path\To\python.exe" | Format-List

```

Compare this hash against the official WinPython release notes. If they match, you can tell IT: *"The SHA-256 matches the official distribution; this is a false positive from the reputation service."*

---

### Summary Table: Which Tool to Use?

| If the error says... | Likely Culprit | Best Tool / Action |
| --- | --- | --- |
| "Windows protected your PC" | **SmartScreen** | `Unblock-File` or click "More Info" -> "Run Anyway" |
| "Blocked by your administrator" | **AppLocker/GPO** | Check Event Viewer (ID 8004); Requires IT whitelist |
| No message, just "Access Denied" | **Permissions/ASR** | Move folder to `C:\Users\%USERNAME%\` |
| "This app cannot run on your PC" | **Architecture/WDAC** | Verify if 64-bit vs 32-bit; check CodeIntegrity logs |

**Would you like me to help you interpret a specific Event ID or error code if you find one in the logs?**

--------------------

That "1 out of 4" statistic is actually the most helpful piece of data yet. In a managed enterprise environment, if a policy (like AppLocker) were truly "Blacklisting" `python.exe`, it would typically hit all 4 machines simultaneously.

Since it is only hitting **one** machine, we can narrow this down to **Machine-Specific Reputation** or a **Corrupted Local Metadata Cache**.

Here is why `pythonw.exe` works while `python.exe` fails on that specific box, and how to verify it:

### 1. The "Subsystem" Theory (Console vs. GUI)

In Windows PE (Portable Executable) headers, there is a field called `Subsystem`.

* **python.exe** is marked as `IMAGE_SUBSYSTEM_WINDOWS_CUI` (Console).
* **pythonw.exe** is marked as `IMAGE_SUBSYSTEM_WINDOWS_GUI` (Graphic).

Microsoft Defender **Attack Surface Reduction (ASR)** rules often target the Console subsystem specifically because that’s how malware "shells" operate. On that specific machine, the user might have a more restrictive ASR "mode" enabled (perhaps they are in a different security group or have "Beta" features turned on).

### 2. The "Cloud Block" (SmartScreen)

SmartScreen is a "Cloud" service. When you run an `.exe`, Windows sends a hash of that file to Microsoft.

* If the cloud says "I've seen this 1 million times, it's fine," it runs.
* If the cloud says "I've never seen this," it shows the **Blue Box**.

**Why the 1-of-4 split?** If that specific machine has been offline, has a blocked connection to the Microsoft Reputation service, or has a "stuck" local cache, it will default to "Block" while the others (which successfully checked the cloud) allowed it.

---

## 3 Tools to Fix This Locally (No IT Required)

### Tool A: The "Move and Rename" Diagnostic

This is the "old school" way to see if the block is **Path-based** or **Hash-based**.

1. Copy `python.exe` to the Desktop.
2. Rename it to `completely_random_name_123.exe`.
3. Try to run it.
* **If it runs:** The block is a **Path Rule** or a **Filename Rule** targeting "python.exe".
* **If it still fails:** The block is a **Hash Rule** or **Digital Signature** check.



### Tool B: PowerShell "Reputation" Clear

If the "Blue Box" is a SmartScreen reputation issue, you can sometimes "nudge" the system to re-evaluate the file by clearing its stream and then trying to run it as an administrator once.

Run this script on the problematic machine:

```powershell
# This removes the 'blocked' status that GUI properties sometimes hides
Unblock-File -Path "C:\Path\To\WinPython\python.exe"

# This forces Windows to ignore the 'cached' reputation result for this session
$file = "C:\Path\To\WinPython\python.exe"
(Get-Item $file).LastWriteTime = Get-Date

```

### Tool C: Comparison via `Get-AppLockerPolicy`

Since you have 3 working machines and 1 broken one, you can actually **see** if the policies are different without asking IT. Run this on a working machine and the broken machine:

```powershell
Get-AppLockerPolicy -Local

```

* If the broken machine returns a list of rules and the working ones return nothing (or a different list), you've found your culprit. You can't change it, but you'll know *exactly* why it's happening.

---

## The "Non-Technical" Fix (The "User-Space" Trick)

Enterprise security often ignores things in specific "Trusted" folders.

* Try moving the entire WinPython folder to **`C:\Users\<username>\AppData\Local\Temp`** (temporarily) or **`C:\Users\<username>\Documents`**.
* Many ASR rules are set to "Monitor" or "Ignore" files running from user profile paths while strictly "Blocking" files running from `C:\`, `Downloads`, or `Program Files`.

**Would you like me to help you check the specific "Subsystem" header of that file to see if it's been tampered with or if it's identical to the working ones?**


