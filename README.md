# Wi-Fi Strength Analyzer (Python + Qt / PySide6)

A Linux desktop application that visualizes Wi-Fi signal strength and the best place in your room to get max speed in real time using:

- Sparkline graph (RSSI dBm vs Time)
- Heatmap (Time × Wi-Fi Channel)
- Asynchronous Wi-Fi scanning (UI does not freeze)

Built using Python and PySide6 (Qt for Python). Uses `nmcli` from NetworkManager to get Wi-Fi scan data.
<img width="1848" height="1512" alt="Screenshot from 2025-11-12 17-37-38" src="https://github.com/user-attachments/assets/ed26ebe4-9cfc-414e-acd9-9779f578f52d" />
<img width="500" height="350" alt="Screenshot from 2025-11-12 15-51-56" src="https://github.com/user-attachments/assets/0139fa79-4e7b-435c-86ec-4710b4554db8" /> <img width="500" height="350" alt="Screenshot from 2025-11-12 16-35-59" src="https://github.com/user-attachments/assets/9f5e82da-1e77-4120-9023-e45637c59b88" />


---

## Features

- Live Wi-Fi scanning (automatic refresh)
- Sparkline graph showing how signal strength changes over time
- Heatmap that shows signal strength per Wi-Fi channel over time
- Uses QProcess for asynchronous system calls
- Auto-selects the strongest Wi-Fi network on launch
  

---

## Prerequisites

Operating system:
- Linux (Ubuntu / Fedora / Arch / Manjaro / Pop!_OS etc.)
- NetworkManager must be installed and running

System dependencies:
- python3 (version 3.8 or newer)
- pip
- python3-venv
- NetworkManager
- nmcli (comes with NetworkManager)

Verify that nmcli works:
nmcli dev wifi



---

## Installation

Clone the repository:
git clone https://github.com/krednie/wifi-heatmap.git
cd wifi-heatmap




Create and activate virtual environment:
python3 -m venv venv
source venv/bin/activate


Install dependencies:
pip install -r requirements.txt

or manually:
pip install PySide6


---

## Run the application

python app.py

---

## Project Structure

wifi-heatmap/
├── app.py # main application source code
├── requirements.txt # dependency list for pip
└── README.md # documentation



---

## How it works

1. A QTimer triggers Wi-Fi scanning every N seconds.
2. A QProcess runs the command:
nmcli -t -f SSID,BSSID,CHAN,SIGNAL dev wifi list


3. The program parses output into:
- SSID
- BSSID (unique identifier of each access point)
- Channel
- Signal percentage

4. Signal percentage is converted into RSSI (dBm) for accuracy.
5. Data is stored in bounded history buffers using `deque`.
6. Two custom PySide6 widgets use QPainter to draw:
- Sparkline (signal vs time)
- Heatmap (signal vs channel vs time)

Because nmcli runs asynchronously using QProcess, the UI always remains responsive.

---

## License

MIT License
