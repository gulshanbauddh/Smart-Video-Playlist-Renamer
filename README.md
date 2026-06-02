# Smart Video Playlist Renamer (GUI App)

A smart, user-friendly desktop application built with Python to automatically reorder and rename downloaded YouTube playlist videos in a local directory based on their official YouTube playlist sequence.

---

## 🚀 Features

* **Smart Sequence Matching:** Leverages Python's `difflib` (fuzzy string matching) to perfectly align local video filenames with live YouTube titles, even if download times or file sizes are completely mixed up.
* **Graphical User Interface (GUI):** Features a clean, intuitive Tkinter UI—no command-line interface (CLI) or coding knowledge required for end-users.
* **Asynchronous Execution:** Runs the core renaming process on a background thread to prevent the user interface from freezing or lagging.
* **Real-time Status Log:** Displays live, actionable updates on matched, renamed, or skipped files directly inside the application window.

---

## 📦 Installation & Usage Guide

You can run this application in two ways: either by downloading the pre-compiled standalone executable (Recommended) or by executing the source code via CMD.

### Method 1: Using the Standalone Executable (Fastest & Easiest)
No Python installation or coding required. Ideal for quick deployment.

1. Navigate to the **Releases** section on the right side of this repository.
2. Download the latest version of **`Playlist_Renamer_App.exe`**.
3. Once downloaded, double-click to launch the application.
4. Paste your **YouTube Playlist Link**, browse and select your local **Video Folder (HDD)**, and click **START RENAMING**!

---

### Method 2: Running via Source Code / CMD (For Developers)

If you prefer to inspect the code, modify it, or build the executable yourself, follow these steps:

#### Prerequisites
Ensure you have Python installed on your system. Open your Command Prompt (CMD) and install the necessary dependencies:
```bash
pip install yt-dlp pyinstaller