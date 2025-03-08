from UI.InteractiveDisplay import Ui_MainWindow
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMdiArea, QMdiSubWindow, 
                           QWidget, QVBoxLayout, QPushButton, QLabel, QToolBar,
                           QMenuBar, QStatusBar, QAction, QTableWidgetItem, QFileDialog,
                           QHBoxLayout, QSplitter, QGroupBox, 
                           QTreeWidget, QFrame, QDoubleSpinBox, QTreeWidgetItem
                           )
import pyqtgraph as pg
import torchaudio as ta
import torch 
from torchaudio.backend.common import AudioMetaData

class ANC_interface(Ui_MainWindow, QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.spectrumViewbox
        self.Show_residual_btn.clicked.connect(self.Show_residual_action)
        self.show_ps_btn.clicked.connect(self.show_ps_action)
        self.start_recording_btn.clicked.connect(self.start_recording_action)
        self.clean_the_audio_btn.clicked.connect(self.clean_the_audio_action)
        self.restart_btn.clicked.connect(self.restart_action)
        self.Play_pause_btn.clicked.connect(self.Play_pause_action)
        self.add_Audio_btn.clicked.connect(self.add_Audio_action)
        self.browse_noise_audio_btn.clicked.connect(self.browse_noise_audio_action)
        self.noise_type_comboBox.currentIndexChanged.connect(self.noise_type_comboaction)

        self._temp_add_a_music()
    
    def Show_residual_action(self):
        """
        shows differences b/w original and processed audio
        """
        ...


    def show_ps_action(self):
        """

        """
        ...


    def start_recording_action(self):
        """

        """
        ...


    def clean_the_audio_action(self):
        """

        """
        ...


    def restart_action(self):
        """

        """
        ...


    def Play_pause_action(self):
        """

        """
        ...


    def add_Audio_action(self):
        """

        """
        ...


    def browse_noise_audio_action(self):
        """

        """
        ...


    def noise_type_comboaction(self):
        """

        """
        ...


    def _temp_add_a_music(self):
        audio_data_path = "A:/gitclones/EEproject/src/noisy_snr0.wav"
        audio_meta_data: AudioMetaData = ta.info(audio_data_path)
        audio_signal, _ = ta.load(audio_data_path)
        
        #
        self.spectrumViewbox.setRowHeight(0, 200)
        plot_widget = PlotWidget(data=audio_signal.contiguous().numpy().flatten(), domain="time")
        self.spectrumViewbox.setCellWidget(0, 1, plot_widget)
        

class PlotWidget(QWidget):
    """Custom widget that contains a PyQtGraph plot."""
    
    def __init__(self, data=None, parent=None, domain:str="time"):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)  # Reduce margins to fit better in the cell
        
        # Create a PyQtGraph plot
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('k')  # White background
        self.plot_widget.setMinimumHeight(100)
        self.plot_widget.setMinimumWidth(200)
        self._domain=domain
        
        # Add the plot widget to the layout
        self.layout.addWidget(self.plot_widget)
        
        # If data is provided, plot it
        if data is not None:
            self.plot_data(data)
    
    def plot_data(self, data):
        """Plot the provided data."""
        # self.plot_widget.clear()
        self.plot_widget.plot(data, pen=pg.mkPen(color='b', width=1))
    

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    # app.setStyle('Fusion') 
    application = ANC_interface()
    application.show()
    sys.exit(app.exec_())

