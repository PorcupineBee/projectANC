import sys
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import (QApplication, QVBoxLayout, 
                             QHBoxLayout, QFrame, QLabel,
                             QWidget, QSlider, QDoubleSpinBox,
                             QSpacerItem, QSizePolicy, 
                             QPushButton,
                             QRadioButton)
from PyQt5.QtCore import Qt
from UI.play_soundbox import NoisePlayerThread , BarMovementThread
import pyaudio
from PyQt5.QtCore import QThread, pyqtSignal


def defaultPlotSettings():
    return dict(
        title='Time Series Plot',
        timelimit=10,
        x_axis_label='Time (s)',
        y_axis_label='Amplitude',
        show_grid=True,
        grid_color=(100, 100, 100),
        grid_style=Qt.DashLine,
        axis_color=(150, 150, 150),
        axis_width=2,
        tick_color=(150, 150, 150),
        tick_font_size=10,
        label_font_size=12,
        title_font_size=14,
        background_color=(30, 30, 30),
        foreground_color=(200, 200, 200),
        plot_colors=[(255, 0, 0), (0, 255, 0), (0, 0, 255)],
        signal=None,
        time=None,
        signal_info=dict(
            type='noise',
            amp_factor=1,
            offset=0
        )
    )

class TimeSeriesPlotWidget(QWidget):
    def __init__(self, 
                #  parent, 
                title,
                timelimit,
                x_axis_label,
                y_axis_label,
                show_grid,
                grid_color,
                grid_style,
                axis_color,
                axis_width,
                tick_color,
                tick_font_size,
                label_font_size,
                title_font_size,
                background_color,
                foreground_color,
                plot_colors,
                signal,
                time,
                signal_info):
        super().__init__()
        self.title = title
        self.timelimit = timelimit
        self.x_axis_label = x_axis_label
        self.y_axis_label = y_axis_label
        self.show_grid = show_grid
        self.grid_color = grid_color
        self.grid_style = grid_style
        self.axis_color = axis_color
        self.axis_width = axis_width
        self.tick_color = tick_color
        self.tick_font_size = tick_font_size
        self.label_font_size = label_font_size
        self.title_font_size = title_font_size
        self.background_color = background_color
        self.foreground_color = foreground_color
        self.plot_colors = plot_colors
        
        self.signal_info = signal_info
        self.pplay = False
        self.original_signal = signal/np.abs(signal).max() # normalizing the signal
        self.maxamp = 1
        self.time=time
        self.time_interval = time[1] - time[0]
        # self.p = pyaudio.PyAudio()
        self.stream = None
        self.chunk_size = 512
        self.pplay = True        
        self.NP_thread = NoisePlayerThread(signal=self.original_signal,
                                            time_interval=self.time_interval,
                                            chunk_size=512)
        self.NP_thread.stopProcess.connect(self.stopProcess)
        self.NP_thread.restartProcess.connect(self.restartProcess)
        self.barmoveThread = BarMovementThread(time_interval=self.time_interval, chunk_size=512)
        self.barmoveThread.movebar.connect(self.move_inf_line)
        self.initUI()
        
    def initUI(self):
        main_layout = QVBoxLayout()
        
        # Create a frame for sliders
        slider_frame = QFrame()
        slider_frame.setStyleSheet("""QDoubleSpinBox {
    background-color: #333;
    color: #fff;
    font-size: 10px;
    border: 1px solid #555;
    border-radius: 4px;
    padding: 2px 15px;
    selection-background-color: #777;
}

QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
    background-color: #444;
    border: none;
    width: 16px;
    height: 12px;
}

QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
    background-color: #666;
}

QDoubleSpinBox::up-arrow {
    image: url(UI/icons/up_arrow.png); /* Use a custom icon or remove */
    width: 5px;
    height: 5px;
}

QDoubleSpinBox::down-arrow {
    image: url(UI/icons/down_arrow.png);
    width: 5px;
    height: 5px;
}
QLabel {
    color:#f1f1f1;
}
QRadioButton {
    color:#f1f1f1;
    font-weight:bold;
}
""")
        slider_layout = QHBoxLayout()
        
        amp_label = QLabel("Amplitude:")        
        self.amp_slider = QDoubleSpinBox()
        self.amp_slider.setRange(0, 1)
        self.amp_slider.setValue(1)
        self.amp_slider.setSingleStep(0.1)
        self.amp_slider.setDecimals(2)
        self.amp_slider.valueChanged.connect(self.update_plot)
        slider_layout.addWidget(amp_label)
        slider_layout.addWidget(self.amp_slider)
        
        # Offset slider and label frame
        
        shift_label = QLabel("Offset:")
        self.shift_slider = QDoubleSpinBox()
        self.shift_slider.setRange(-self.timelimit, self.timelimit)  # Scaled to 0-10s
        self.shift_slider.setValue(self.signal_info["offset"])
        self.shift_slider.setSingleStep(1)
        self.shift_slider.setDecimals(1)
        self.shift_slider.valueChanged.connect(self.update_plot)
        slider_layout.addWidget(shift_label)
        slider_layout.addWidget(self.shift_slider)
        
        # play button
        self.play_button = QPushButton("Play")
        self.play_button.setStyleSheet("padding:5px 15px; font-size:10px;")
        self.play_button.clicked.connect(self.play_signal)
        slider_layout.addWidget(self.play_button)
        
        # show window
        window_radiobox = QRadioButton("Show Window")
        window_radiobox.toggled.connect(self.show_hide_window)
        slider_layout.addWidget(window_radiobox)
         
        spacerItem1 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        slider_layout.addItem(spacerItem1)
        
        
        slider_layout.setContentsMargins(10, 5, 0, 0)
        slider_layout.setSpacing(10)
        # Add slider frames to horizontal layout
        slider_frame.setLayout(slider_layout)
        main_layout.addWidget(slider_frame)
        
        # Create a frame for the plot
        plot_frame = QFrame()
        plot_layout = QVBoxLayout()
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.getPlotItem().showAxis('bottom', True)  # Hide bottom axis
        self.plot_widget.getPlotItem().showAxis('top', True)  # Show top axis
        self.plot_widget.getPlotItem().showAxis('right', True)  # Show top axis
        # self.plot_widget.getPlotItem().getAxis('top').setStyle(showValues=True)
        # self.plot_widget.getPlotItem().getAxis('bottom').setStyle(showValues=False)
        self.plot_widget.getPlotItem().showGrid(True)  # Hide bottom axis
        
        plot_layout.addWidget(self.plot_widget)
        plot_frame.setLayout(plot_layout)
        main_layout.addWidget(plot_frame)
        
        self.setLayout(main_layout)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.plot_widget.plot(self.time, 
                              self.signal_info["amp_factor"] * self.original_signal, pen='r')
        
        
        # Add moveable infinite line at time = 0
        self.inf_line = pg.InfiniteLine(pos=0, angle=90, movable=True, pen='b', bounds=[self.time[0], self.time[-1]])
        self.plot_widget.addItem(self.inf_line)
        
        # Add moveable rectangular region above the signal
        self.region = pg.LinearRegionItem(orientation=pg.LinearRegionItem.Vertical)
        self.region.setRegion([self.time[0], self.time[-1]])  # Default position
        self.region.setBrush(pg.mkBrush((200, 200, 255, 50)))  # Semi-transparent blue
        window_radiobox.setChecked(False)
        
    
    
    def play_signal(self):
        if self.pplay:
            self.NP_thread.start()
            self.barmoveThread.play()
            self.barmoveThread.start()
            self.play_button.setText("Pause")
            self.pplay = False
        else:
            self.NP_thread.pause()
            self.barmoveThread.pause()
            self.play_button.setText("Play")
            self.pplay = True
        
    def move_inf_line(self, dt):
        next_step = self.inf_line.value() + dt
        self.inf_line.setPos(next_step)
        
    def restartProcess(self):
        self.inf_line.setPos(0)
        
    
    def stopProcess(self):
        # if self.pplay
        self.barmoveThread.pause()
        self.play_button.setText("Play")
        self.inf_line.setPos(0)
        self.pplay = True
        
        
    def closeWidget(self):
        self.NP_thread.close()
        
    def update_plot(self):
        self.signal_info["amp_factor"] = self.amp_slider.value() 
        self.signal_info["offset"] = self.shift_slider.value()
                
        # Apply amplitude scaling and time offset shifting
        shifted_time = self.time + self.signal_info["offset"]
        
        self.plot_widget.clear()
        self.plot_widget.plot(shifted_time, 
                              self.signal_info["amp_factor"] * self.original_signal/self.maxamp, pen='r')
        
        # Re-add infinite line and region after clearing plot
        self.plot_widget.addItem(self.inf_line)
        self.plot_widget.addItem(self.region)

    def show_hide_window(self, flag):
        if flag:
            self.plot_widget.addItem(self.region)
        else:
            self.plot_widget.removeItem(self.region)
            
        

import time
class plySignalinThread(QThread):
    move_inf_line = pyqtSignal()
    def __init__(self, parent=None):
        super(plySignalinThread, self).__init__(parent)
        self._go = False
        
    @property
    def go(self):
        return self._go
    
    def run(self):
        if self._go:
            self.move_inf_line.emit()
        
    def stop(self):
        self._go = False
        
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    s = defaultPlotSettings()
    mainWin = TimeSeriesPlotWidget(**s)
    mainWin.show()
    sys.exit(app.exec_())