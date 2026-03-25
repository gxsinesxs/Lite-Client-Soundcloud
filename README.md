# 🎵 LiteCloud v1.4

A lightweight, high-performance SoundCloud desktop client built with Python. LiteCloud offers a clean, modern interface for searching and streaming music directly from SoundCloud without the bloat of a web browser.

---

## ✨ Features

* **Fast Search:** Instant access to millions of tracks using SoundCloud's API.
* **Modern UI:** Built with `CustomTkinter` for a sleek, dark-themed experience.
* **Library Management:** Save your favorite tracks to a local "Liked Tracks" list.
* **Audio Precision:** Powered by the VLC media engine for high-quality playback.
* **UX Focused:** * Press **Enter** to search instantly.
    * Full **Mouse Wheel** scrolling support.
    * Real-time progress slider.
    * Auto-play next track in the queue.

---

## 🛠️ Tech Stack

* **Language:** Python 3.10+
* **GUI:** [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
* **Media Engine:** [python-vlc](https://github.com/oaubert/python-vlc) (requires VLC media player installed)
* **Networking:** `requests` for API interaction
* **Concurrency:** `threading` for lag-free UI during playback and search

---

## 🚀 Installation & Setup

### 1. Prerequisites
Ensure you have **VLC Media Player** installed on your system. LiteCloud uses the VLC engine to handle audio streams.
* Download VLC: [https://www.videolan.org/](https://www.videolan.org/)

### 2. Install Dependencies
Open your terminal (PowerShell or CMD) and run:
```bash
pip install customtkinter python-vlc requests
