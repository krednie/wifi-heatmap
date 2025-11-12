#!/usr/bin/env python3


from collections import deque
from typing import Optional, Tuple, List

from PySide6.QtCore import QTimer, QProcess, Qt, QPointF
from PySide6.QtGui import QPainter, QPen, QColor, QFont
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QPushButton, QLabel, QSpinBox
)


def pct_to_dbm(pct_str: str) -> Optional[int]:
    try:
        pct = int(pct_str)
    except Exception:
        return None
    
    return int(pct * 0.7 - 95)

def band_from_channel(ch: Optional[int]) -> str:
    if ch is None:
        return "?"
    if 1 <= ch <= 14:
        return "2.4"
    if 32 <= ch <= 177:
        return "5"
    if ch >= 1 and ch <= 233:  
        return "6"
    return "?"

def rssi_to_color(dbm: Optional[int]) -> QColor:
    if dbm is None:
        return QColor(60, 60, 60)
    d = max(-95, min(-40, dbm))
    t = (d + 95) / 55.0  

    if t < 0.33:
        u = t / 0.33
        r = int(220 + 35 * u)
        g = int(0 + 255 * u)
        b = 0
    elif t < 0.66:
        r, g, b = 255, 255, 0
    else:
        u = (t - 0.66) / 0.34
        r = int(255 * (1 - u))
        g = int(255 - 55 * u)
        b = 0
    return QColor(r, g, b)



class Sparkline(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.values: deque[Optional[int]] = deque(maxlen=300)  
        self.setMinimumHeight(140)

    def set_all(self, seq):
        self.values.clear()
        self.values.extend(seq)
        self.update()

    def append(self, v: Optional[int]):
        self.values.append(v)
        self.update()

    def paintEvent(self, ev):
        p = QPainter(self)
        w, h = self.width(), self.height()
        p.fillRect(self.rect(), QColor(20, 20, 24))
        p.setPen(QPen(QColor(80, 80, 90), 1))
        p.drawRect(0, 0, w - 1, h - 1)

        def y_for(dbm):
            if dbm is None:
                return h - 10
            d = max(-95, min(-40, dbm))
            t = (d + 95) / 55.0
            return int(h - 10 - (h - 20) * t)


        for v, label in [(-55, "-55"), (-65, "-65"), (-75, "-75"), (-85, "-85")]:
            yy = y_for(v)
            p.setPen(QPen(QColor(60, 60, 70), 1))
            p.drawLine(1, yy, w - 2, yy)
            p.setPen(QPen(QColor(150, 150, 160)))
            p.setFont(QFont("Sans", 8))
            p.drawText(6, yy - 2, label)

        if len(self.values) >= 2:
            step = max(1, w // (len(self.values) - 1))
            x = 6
            p.setPen(QPen(QColor(220, 220, 230), 2))
            last = None
            for v in self.values:
                y = y_for(v)
                if last is not None:
                    p.drawLine(QPointF(last[0], last[1]), QPointF(x, y))
                last = (x, y)
                x += step

        p.setPen(QPen(QColor(180, 180, 190)))
        p.drawText(8, 14, "RSSI (dBm) — live")
        p.end()




class Heatmap(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.data: deque[Tuple[Optional[int], Optional[int]]] = deque(maxlen=300)
        self.setMinimumHeight(220)

    def set_all(self, seq: List[Tuple[Optional[int], Optional[int]]]):
        self.data.clear()
        self.data.extend(seq)
        self.update()

    def append(self, v: Tuple[Optional[int], Optional[int]]):
        self.data.append(v)
        self.update()

    def paintEvent(self, ev):
        p = QPainter(self)
        w, h = self.width(), self.height()
        p.fillRect(self.rect(), QColor(15, 15, 18))

        
        recent_ch = None
        for dbm, ch in reversed(self.data):
            if ch:
                recent_ch = ch
                break
        band = band_from_channel(recent_ch)

        if band == "2.4":
            channels = list(range(1, 14))
        elif band == "5":
            channels = [36,40,44,48,52,56,60,64,100,104,108,112,116,120,124,128,132,136,140,144,149,153,157,161,165]
        else: 
            channels = list(range(1, 234, 4))

        rows = len(channels)
        cols = max(1, len(self.data))
        cell_w = max(1, int(w / cols))
        cell_h = max(1, int((h - 20) / max(1, rows)))

        
        for c in range(cols):
            dbm, ch = self.data[c] if c < len(self.data) else (None, None)
            if ch in channels:
                r = channels.index(ch)
                x = c * cell_w
                y = 10 + r * cell_h
                p.fillRect(x, y, cell_w, cell_h, rssi_to_color(dbm))

        
        p.setPen(QPen(QColor(50, 50, 60), 1))
        p.setFont(QFont("Sans", 8))
        for r, ch in enumerate(channels):
            y = 10 + r * cell_h
            p.drawLine(0, y, w, y)
            p.setPen(QPen(QColor(150, 150, 160)))
            p.drawText(4, y + min(cell_h - 2, 12), str(ch))
            p.setPen(QPen(QColor(50, 50, 60), 1))

        p.setPen(QPen(QColor(90, 90, 100)))
        p.drawRect(0, 0, w - 1, h - 1)
        p.setPen(QPen(QColor(180, 180, 190)))
        p.drawText(8, 8, f"Heatmap (Time →)  Band {band}")
        p.end()




def main():
    app = QApplication([])

    
    win = QWidget()
    win.setWindowTitle("Wi-Fi Strength RSSI + Heatmap acm proj")
    v = QVBoxLayout(win)

    top = QHBoxLayout()
    v.addLayout(top)

    btn_scan = QPushButton("Scan now 👀")
    top.addWidget(btn_scan)

    top.addWidget(QLabel("Interval 🕰(s):"))
    spin = QSpinBox()
    spin.setRange(1, 30)
    spin.setValue(2)
    top.addWidget(spin)

    status = QLabel("Ready 👍")
    top.addWidget(status, 1, alignment=Qt.AlignRight)

    listw = QListWidget()
    v.addWidget(listw)

    spark = Sparkline()
    v.addWidget(spark)

    heat = Heatmap()
    v.addWidget(heat)

    
    proc = QProcess()
    busy = {"flag": False}
    tick = {"i": 0}
    selected_bssid = {"val": None}
    
    series: dict[str, deque[Tuple[Optional[int], Optional[int]]]] = {}

    
    def on_pick(item: Optional[QListWidgetItem]):
        if not item:
            return
        selected_bssid["val"] = item.data(Qt.UserRole)
        
        dq = series.get(selected_bssid["val"])
        if dq:
            spark.set_all([d for d, _ in dq])
            heat.set_all(list(dq))
        else:
            spark.set_all([])
            heat.set_all([])

    listw.currentItemChanged.connect(lambda cur, prev=None: on_pick(cur))

    
    def start_scan(rescan_yes=True):
        if busy["flag"]:
            return
        busy["flag"] = True
        args = ["-t", "-f", "SSID,BSSID,CHAN,SIGNAL", "dev", "wifi", "list"]
        args += ["--rescan", "yes" if rescan_yes else "no"]
        proc.setProgram("nmcli")
        proc.setArguments(args)
        status.setText("Scanning…")
        proc.start()

    def handle_finished(_exitCode, _exitStatus):
        busy["flag"] = False
        try:
            out = bytes(proc.readAllStandardOutput()).decode("utf-8", "ignore")
        except Exception:
            out = ""

        rows = []
        for line in out.splitlines():
            if not line.strip():
                continue
            parts, cur, esc = [], "", False
            for ch in line:
                if esc:
                    cur += ch; esc = False
                elif ch == "\\":
                    esc = True
                elif ch == ":":
                    parts.append(cur); cur = ""
                else:
                    cur += ch
            parts.append(cur)
            if len(parts) >= 4:
                ssid, bssid, chan, sig = parts[:4]
                rows.append((ssid or "<hidden>", bssid, chan, sig))

        
        listw.clear()
        for ssid, bssid, chan, sig in rows:
            item = QListWidgetItem(f"{ssid} | {bssid} | ch {chan} | {sig}%")
            item.setData(Qt.UserRole, bssid)
            listw.addItem(item)

        
        if selected_bssid["val"] is None and rows:
            best = None; best_pct = -1
            for ssid, bssid, chan, sig in rows:
                try:
                    p = int(sig)
                except:
                    p = -1
                if p > best_pct:
                    best_pct = p; best = bssid
            selected_bssid["val"] = best
            
            for i in range(listw.count()):
                it = listw.item(i)
                if it.data(Qt.UserRole) == best:
                    listw.setCurrentItem(it)
                    break

        
        bssid = selected_bssid["val"]
        if bssid is not None:
            seen = next((r for r in rows if r[1] == bssid), None)
            dbm = pct_to_dbm(seen[3]) if seen else None
            try:
                ch = int(seen[2]) if seen else None
            except:
                ch = None
            dq = series.setdefault(bssid, deque(maxlen=300))
            dq.append((dbm, ch))
            spark.set_all([d for d, _ in dq])
            heat.set_all(list(dq))

        status.setText("OK")

    proc.finished.connect(handle_finished)

    
    btn_scan.clicked.connect(lambda: start_scan(rescan_yes=True))

    timer = QTimer()
    def on_timer():
        tick["i"] += 1
        
        start_scan(rescan_yes=(tick["i"] % 4 == 0))
    timer.timeout.connect(on_timer)
    timer.start(spin.value() * 1000)

    
    def on_interval_change(v):
        timer.stop()
        timer.start(v * 1000)
    spin.valueChanged.connect(on_interval_change)

    
    start_scan(rescan_yes=True)

    win.resize(900, 700)
    win.show()
    app.exec()


if __name__ == "__main__":
    main()
