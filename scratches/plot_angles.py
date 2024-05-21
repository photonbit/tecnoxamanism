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
win.setWindowTitle('Real-time Euler Angles')
layout = QVBoxLayout()
win.setLayout(layout)

roll_plot = pg.PlotWidget(title="Roll")
roll_curve = roll_plot.plot(pen='r')
roll_data = deque(maxlen=100)

pitch_plot = pg.PlotWidget(title="Pitch")
pitch_curve = pitch_plot.plot(pen='g')
pitch_data = deque(maxlen=100)

yaw_plot = pg.PlotWidget(title="Yaw")
yaw_curve = yaw_plot.plot(pen='b')
yaw_data = deque(maxlen=100)

layout.addWidget(roll_plot)
layout.addWidget(pitch_plot)
layout.addWidget(yaw_plot)


def update():
    line = ""
    while not line.startswith("Orientation:"):
        line = ser.readline().decode('utf-8').rstrip()
    if line:
        line = line.replace("Orientation: ", "")
        data = list(map(float, line.split(',')))
        roll_data.append(data[0])
        pitch_data.append(data[1])
        yaw_data.append(data[2])

        roll_curve.setData(roll_data)
        pitch_curve.setData(pitch_data)
        yaw_curve.setData(yaw_data)


timer = QTimer()
timer.timeout.connect(update)
timer.start(0)

win.show()

if __name__ == '__main__':
    if not sys.flags.interactive:
        app.exec_()