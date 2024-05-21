import sys
import serial
from PyQt5.QtWidgets import QApplication, QGraphicsView, QVBoxLayout
from PyQt5.QtCore import QTimer
import pyqtgraph as pg
from collections import deque

# Initialize serial port - replace 'COM_PORT' with your Arduino's port
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)

# Set up the PyQtGraph window
app = QApplication([])
win = QGraphicsView()
win.setWindowTitle('Real-time Quaternion')
layout = QVBoxLayout()
win.setLayout(layout)

qw_plot = pg.PlotWidget(title="Qw")
qw_curve = qw_plot.plot(pen='m')
qw_data = deque(maxlen=100)

qx_plot = pg.PlotWidget(title="Qx")
qx_curve = qx_plot.plot(pen='r')
qx_data = deque(maxlen=100)

qy_plot = pg.PlotWidget(title="Qy")
qy_curve = qy_plot.plot(pen='g')
qy_data = deque(maxlen=100)

qz_plot = pg.PlotWidget(title="Qz")
qz_curve = qz_plot.plot(pen='b')
qz_data = deque(maxlen=100)


layout.addWidget(qw_plot)
layout.addWidget(qx_plot)
layout.addWidget(qy_plot)
layout.addWidget(qz_plot)


def update():
    line = ""
    while not line.startswith("Quaternion:"):
        line = ser.readline().decode('utf-8').rstrip()
    if line:
        line = line.replace("Quaternion: ", "")
        data = list(map(float, line.split(',')))
        qw_data.append(data[0])
        qx_data.append(data[1])
        qy_data.append(data[2])
        qz_data.append(data[3])

        qw_curve.setData(qw_data)
        qx_curve.setData(qx_data)
        qy_curve.setData(qy_data)
        qz_curve.setData(qz_data)


timer = QTimer()
timer.timeout.connect(update)
timer.start(0)

win.show()

if __name__ == '__main__':
    if not sys.flags.interactive:
        app.exec_()
