# Android Toolbox GUI

A comprehensive, cross-platform graphical user interface for the most powerful and popular Android flashing and debugging command-line tools.  
This application bundles the functionality of **ADB, Fastboot, Odin, Heimdall, SP Flash Tool, Qualcomm EDL, and scrcpy** into a single, user-friendly tabbed interface, eliminating the need to memorize complex commands.

---

## Features

This application is a true *"Swiss Army knife"* for Android modification, providing a vast array of features organized by tool.

### General Application Features
- **Multi-Tool Integration**: Seamlessly switch between different flashing and debugging protocols.  
- **Theming**: Multiple themes (Light, Dark, Matrix, Synthwave, Dracula).  
- **Multi-Language Support**: Switch between English and Swedish on the fly.  
- **Persistent Settings**: Remembers tool paths, window size, and last-used theme/language.  
- **Drag & Drop**: Easily drag firmware files onto the correct input fields.  
- **Live Command Preview**: See the exact command before execution.  
- **Detailed Output Log**: Real-time, color-coded command output.  

---

## Tools Overview

### 1. ADB (Android Debug Bridge)
- File Management: Push/pull files.  
- App Management: Install/uninstall `.apk` (with options).  
- Device Control: Reboot to system/recovery/bootloader/sideload.  
- Advanced: Screenshots, screen recording, shell commands.  
- Diagnostics: Device info, battery stats, bug report.  
- Debloat Tool: Disable/enable system apps without root.  
- Networking: Connect wirelessly via TCP/IP.  

### 2. Fastboot
- Flashing: Partitions or full `.zip` updates.  
- Bootloader Control: Lock/unlock (including critical partitions).  
- A/B Slot Management: View/set active boot slot.  
- Partition Management: Erase/wipe partitions.  
- Advanced: Boot temp images, get device variables (`getvar`).  

### 3. Xiaomi Flasher
- Simplified Flashing: Flash official Xiaomi Fastboot ROMs (`.tgz`).  
- Automatic Extraction of firmware archives.  
- Scripted Options: Flash + wipe, flash + keep data, flash + relock bootloader.  

### 4. Qualcomm EDL (Emergency Download Mode)
- Rescue Tool: GUI for `edl.py` to unbrick devices.  
- QFIL Flashing: Loader (firehose), rawprogram.xml, patch.xml, image dir.  
- Basic Commands: Reboot to EDL, print partition table, reset device.  

### 5. Heimdall (Samsung)
- Open-source flashing for Samsung devices.  
- PIT Management: Detect/print/download PIT files.  
- Dynamic Partition Flashing.  
- Advanced: Repartitioning, no reboot, SD card flashing, skip checks.  

### 6. SP Flash Tool (MediaTek)
- GUI for command-line SP Flash Tool.  
- Scatter File Loading for partitions.  
- Flash Modes: Download Only, Firmware Upgrade, Format All + Download.  
- Advanced Options: Custom DA, battery mode, reboot, COM port.  

### 7. Odin (Samsung)
- GUI for `odin4` Linux tool.  
- Dedicated slots: BL, AP, CP, CSC, UMS.  
- Options: Nand Erase, Reboot, Auto Download Mode.  
- Device Detection: Scan/select device in Download Mode.  

### 8. scrcpy (Screen Mirroring)
- Live, low-latency mirroring.  
- Full keyboard/mouse control.  
- Quality Options: Bitrate & resolution.  
- Utility: Show touches, keep awake.  

### 9. Logcat
- Real-time log streaming.  
- Color-coded output for errors/warnings/info.  
- Live filtering with keywords.  

---

## Dependencies

- **Python**
- **PyQt6** (GUI)  
  ```bash
  pip install PyQt6 edl
---
Command-line tools:

ADB & Fastboot: Android SDK Platform Tools https://developer.android.com/studio/releases/platform-tools

Heimdall: Official GitLab Repository https://gitlab.com/BenjaminDobell/Heimdall

SP Flash Tool: https://spflashtool.com

Odin4 (Linux): Community-developed tool https://github.com/Adrilaw/OdinV4/releases

edl.py: pip install edl

scrcpy: Official GitHub Repository https://github.com/Genymobile/scrcpy. Can often be installed via your Linux distribution's package manager (e.g., sudo apt install scrcpy).
