# 📡 Linux Wi-Fi Strength Analyzer (Python + Qt)

A desktop app that visualizes **Wi-Fi signal strength over time** using:

- **Sparkline graph (RSSI dBm VS time)**
- **Heatmap (Time × Wi-Fi Channel)**
- Asynchronous `nmcli` scanning (UI never freezes)

Built using **Python + PySide6 (Qt)**.  
Works on Linux (NetworkManager required).

---

## 🚀 Features

| Feature | Description |
|--------|-------------|
|  Live Wi-Fi scan (every N seconds) | Uses `nmcli` without blocking the UI |
|  Sparkline graph | Shows RSSI (signal strength in dBm) over time |
|  Heatmap visualization | Shows how signal strength varies per channel |
|  Auto-select strongest AP | Shows useful data immediately |
|  Fully asynchronous | Uses `QProcess`, so scanning never freezes UI |
|  Pure Python | No C/C++ compilation needed |

---

## What do the graphs show?

### Sparkline (RSSI dBm vs Time)
- **Higher line = better signal**
- dBm is always negative  
  `-40 dBm = excellent`  
  `-90 dBm = bad`

### Heatmap (Time × Channel)
- Rows = Wi-Fi channels (1–11, 36+, etc.)
- Columns = Time (each scan)
- Color intensity:
  - 🟢 strong
  - 🟡 medium
  - 🔴 weak

This helps diagnose:
- Where Wi-Fi is weak
- Channel congestion
- Signal drops while moving around

---
``` basht clone https://github.com/<your-username>/wifi-heatmap.git
cd wifi-heatmap
