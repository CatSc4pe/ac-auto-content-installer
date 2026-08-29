# AC Auto-Content Installer Pro 🏎️

An intelligent, zero-click open-source mod installer for **Assetto Corsa** built entirely in Python. 

Drop any compressed archive directly into the application. The program scans the internal directory structure, automatically solves game directory mappings by matching internal 3D assets to prevent `LODs list is missing` crashes, and deploys files directly into the target directories.

## Features
- 🔍 **Deep Archive Inspection:** Automatically handles chaotic folder structures, nested paths, or loose asset layouts.
- 🛠️ **Smart Matching Engine:** Resolves tracking name configurations to prevent game alignment crashes.
- 🗺️ **Auto-Detection:** Automatically scans the Windows Registry to pinpoint your Assetto Corsa Steam installation paths.
- 📦 **Universal Unpacker Engine:** Native backend extraction for `.zip`, `.rar`, and `.7z` extensions.

## Installation / Run From Source
1. Install Python 3.x
2. Install dependencies: `pip install patool`
3. Launch the file: `python "AC auto-content.py"`
