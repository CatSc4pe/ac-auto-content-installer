# AC Auto-Content Installer Pro 🏎️

An intelligent, zero-click open-source mod installer for **Assetto Corsa** built entirely in Python. 

Drop any compressed archive directly into the application. The program scans the internal directory structure, automatically solves game directory mappings by matching internal 3D assets to prevent `LODs list is missing` crashes, and deploys files directly into the target game directories.

## 🛡️ Antivirus False Positives / Safety Notice
Because this application is **completely open-source**, the entire code is hosted publicly right here for anyone to inspect, audit, or review. It contains absolutely **zero** malicious tracking logic or malware.

### Why is it getting flagged?
- **No Digital Certificate:** As an independent developer project, the compiled `.exe` does not have an expensive corporate digital signature. Windows security protocols automatically flag unsigned executables as suspicious by default.
- **PyInstaller Bundling:** The executable is compiled automatically in the cloud using PyInstaller. Antivirus heuristic AI engines frequently flag automated PyInstaller templates because real malware authors unfortunately use them to compress code.

**If Windows Defender or SmartScreen blocks the app:**
1. Click **"More Info"** on the Windows blue popup window.
2. Select **"Run Anyway"**.
3. Alternatively, right-click `AC auto-content.exe` ➔ **Properties** ➔ Check **"Unblock"** at the bottom of the General tab ➔ Click Apply.

---

## Features
- 🔍 **Deep Archive Inspection:** Automatically handles chaotic folder structures, nested paths, or loose asset layouts.
- 🛠️ **Smart Matching Engine:** Resolves tracking name configurations directly from internal `lods.ini` structures to prevent asset alignment game crashes.
- 🗺️ **Auto-Detection:** Automatically scans the Windows Registry to pinpoint your Assetto Corsa Steam installation paths.
- 📦 **Universal Unpacker Engine:** Native background extraction handling for `.zip`, `.rar`, and `.7z` extensions.

## Running From Source (Alternative)
If you prefer not to use the pre-compiled executable, you can run the raw, transparent script directly via your local terminal setup:
1. Install Python 3.x on your computer.
2. Install the necessary extraction module: `pip install patool`
3. Launch the script directly: `python "AC auto-content.py"`
