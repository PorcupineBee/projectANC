from UI.InteractiveDisplay import Ui_ANC_interface
from UI.startup import Ui_NoiseShieldPopUp
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMdiArea, QMdiSubWindow, 
                           QWidget, QVBoxLayout, QPushButton, QLabel, QToolBar,
                           QMenuBar, QStatusBar, QAction, QTableWidgetItem, QFileDialog,
                           QHBoxLayout, QSplitter, QGroupBox, 
                           QTreeWidget, QFrame, QDoubleSpinBox, QTreeWidgetItem,
                           QFontDialog, QMessageBox
                           )
from PyQt5.QtCore import Qt
import pyqtgraph as pg
import torchaudio as ta
import torch 
from torchaudio import AudioMetaData
import numpy as np
import os, json, uuid
import matplotlib.pyplot as plt
import pandas as pd
import datetime
from UI.plotsignal import defaultPlotSettings, TimeSeriesPlotWidget
from UI.play_soundbox import NoisePlayerThread
from .utiles import getAudioSignal_n_Time, signal_registry

# region Auxillary functions
def saveNewProject(parent, **kwargs):
    project_id = str(uuid.uuid4())
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    folderpath = QFileDialog.getExistingDirectory(parent, "Select a Directory") if "folderpath" not in kwargs.keys() else kwargs.pop("folderpath")
    if folderpath != '':
        lcache = os.path.join(folderpath, ".cache")
        if not os.path.exists(lcache):
            os.mkdir(lcache)
            with open(os.path.join(lcache, "project_cache.json"), "w") as f:
                json.dump({"project_id" : project_id}, f)
                f.close()
            
        with open(checkGUIcache(), "a") as f:
            f.write(f"{project_id},{folderpath},{timestamp}\n")
            f.close()
        return folderpath, project_id
    else:
        print("No folder selected")
        return None, None
            
def checkGUIcache() -> str:
    """returns the path to the cache file for the GUI
    Returns:
        str: cache file path
    """
    root = os.path.join(os.path.expanduser("~"), ".noise_shield")        
    if not os.path.exists(root):
        os.mkdir(root)
        with open(os.path.join(root, "system_cache.csv"), "w") as f:
            f.write(f"project_id,folder_location,dom\n")
            f.close()
    return os.path.join(root, "system_cache.csv")
# endregion

# region NoiseShiled INTERFACE
class NoiseShiled(Ui_ANC_interface, QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.project_registry = signal_registry()
        self.Show_residual_btn.clicked.connect(self.Show_residual_action)
        self.show_ps_btn.clicked.connect(self.show_ps_action)
        self.start_recording_btn.clicked.connect(self.start_recording_action)
        self.clean_the_audio_btn.clicked.connect(self.clean_the_audio_action)
        self.restart_btn.clicked.connect(self.restart_action)
        self.Play_pause_btn.clicked.connect(self.Play_pause_action)
        self.add_Audio_btn.clicked.connect(self.add_Audio_action)
        self.browse_noise_audio_btn.clicked.connect(self.browse_noise_audio_action)
        self.noise_type_comboBox.currentIndexChanged.connect(self.noise_type_comboaction)
        
        self.extra_ui()
        self.input_audio_spectrum()
        self.output_audio_spectrum()
        # self._temp_add_a_music()
        self.order_key = dict()
        
        
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
        self.running = not self.running
        if self.running:
            self.audioThread = NoisePlayerThread()
            self.audioThread.toggle_signal.connect(self.Play_pause_action)
            self.audioThread.moveINfLines.connect(self.move_inf_lines)
            self.audioThread.start()

    def move_inf_lines(self):
        """

        """
        ...
        
    def add_Audio_action(self):
        """

        """
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Audio File", "", 
                        "Audio Files (*.wav *.mp3 *.flac *.ogg *.aac);;All Files (*)", options=options)

        if file_path:
            signal, time = getAudioSignal_n_Time(file_path)   
            self.addASignalStremer(signal, time, "signal")
            self.showStatus(file_path, align="right")

    def browse_noise_audio_action(self):
        """

        """
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Noise Audio File", "", 
                        "Audio Files (*.wav *.mp3 *.flac *.ogg *.aac);;All Files (*)", options=options)

        if file_path:
            signal, time = getAudioSignal_n_Time(file_path)   
            self.addASignalStremer(signal, time, "Noise")
            self.showStatus(file_path, align="right")
        


    def noise_type_comboaction(self, index:int):
        """

        """
        path = "A:/NoiseShiled_noise_data"
        audio_file = os.path.join(path, self.noise_file_data[f"{index+1}"])     
        self.addASignalStremer("noise", audio_file)

    
    
    def addASignalStremer(self, stype:str, audio_file:str, ):
        """
        """
        
        signal, time, order, signal_key = self.project_registry.add_signal(fpath=audio_file, type=stype)
        
        plotsetting = defaultPlotSettings()
        plotsetting["signal"] = signal
        plotsetting["time"] = time
        plotsetting["signal_info"]["type"] = stype
        
        tspwidegt = TimeSeriesPlotWidget(**plotsetting) 
        self.spectrumViewbox.setRowCount(order+1)
        self.spectrumViewbox.setRowHeight(order, 200)
        self.spectrumViewbox.setCellWidget(order, 1, tspwidegt)
        self.order_key.update({order:
            dict(
                name=signal_key,
                widget=tspwidegt
                )
            })
        

    def showStatus(self, message:str=None, align="left",**kwargs):
        if align=="left":
            self.statusbar.showMessage(message)
            self.statusbar.setStyleSheet("color: #bbb;padding: 0px 5px; background: None;")
        elif align=="right":
            self.status_text.setText(message)
            
    def extra_ui(self):
        self.status_text = QLabel("")
        
        self.status_text.setStyleSheet("color: #bbb;padding: 0px 5px; background: None;")
        self.statusbar.addPermanentWidget(self.status_text)
        self.startupwind = StartUpInterface(self)
        self.startupwind.show()
        
        with open("src/noise_file_data.json", "r") as f:
            self.noise_file_data = json.load(f)
            f.close()
        for key, value in self.noise_file_data.items():
            self.noise_type_comboBox.addItem(value) 
    
    def load_project(self, registry:dict):
        self.project_registry.signals_df = registry
    
    def save_project(self):
        if self.working_dir is None:
            self.working_dir, _project_id = saveNewProject(self)
            try:
                self.project_registry.saveCache(working_dir=self.working_dir,
                                                project_id=_project_id)
            except Exception as e:
                print(e)
                self.showStatus("Error occurred while saving the project", align="left")
    
    def closeEvent(self, a0):
        for _ , dictobj in self.order_key.items():
            tsWidget = dictobj["widget"]
            tsWidget.closeWidget()
            
        return super().closeEvent(a0)
    
    # def _temp_add_a_music(self):
    #     audio_data_path = "A:/gitclones/EEproject/raw_data/noisy_snr0.wav"
    #     plot_widget = plot_this_audio_file(audio_data_path)
    #     self.spectrumViewbox.setRowHeight(0, 200)
    #     self.spectrumViewbox.setCellWidget(0, 1, plot_widget)

    def input_audio_spectrum(self):
        
        ...

    def output_audio_spectrum(self):
        
        ...

# endregion


# region signal plot class 
def plot_this_audio_file(file:str):
    audio_meta_data: AudioMetaData = ta.info(file)
    audio_signal, _ = ta.load(file)
    plot_widget = PlotWidget(domain="time")
    sr = audio_meta_data.sample_rate
    nf = audio_meta_data.num_frames 
    durations = nf/sr
    time = np.linspace(0, durations, nf)
    plot_widget.plot_data(data=audio_signal.contiguous().numpy().flatten(),
                           time=time) 
    return plot_widget

class PlotWidget(QWidget):
    """Custom widget that contains a PyQtGraph plot."""
    
    def __init__(self, parent=None, domain:str="time"):
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
    
    def plot_data(self, data:np.ndarray, time:np.ndarray):
        """Plot the provided data."""
        self.plot_widget.clear()
        self.plot_widget.plot(time, data, pen=pg.mkPen(color='b', width=1))
# endregion
# region STARTUP INTERFACE
class StartUpInterface(Ui_NoiseShieldPopUp, QMainWindow):
    def __init__(self, parent:NoiseShiled):
        super().__init__()
        self.setupUi(self)
        self.new_project_btn.clicked.connect(self.new_project_action)
        self.open_old_project_btn.clicked.connect(self.open_old_project_action)
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        self.parent = parent
        self.search_recent_projects()
    
    def new_project_action(self, **kwargs):
        """
        """
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnBottomHint)
        folderpath, _ = saveNewProject(self.parent, **kwargs)            
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        
        self.parent.working_dir = folderpath
        self.parent.showStatus(f"Working dir: {folderpath}", align="left")
        if folderpath is not None:
            self.close()
    
    def open_old_project_action(self, **kwargs):
        """
        """
        folderpath = QFileDialog.getExistingDirectory(self, "Select old Project directory") if "folderpath" not in kwargs.keys() else kwargs.pop("folderpath")
        registry = os.path.join(folderpath, ".cache/project_cache.json")
        if not os.path.exists(registry):
            self.oldPrjNotFound(folderpath)
            self.close()
        else:
            self.parent.working_dir = folderpath
            self.parent.showStatus(f"Working dir: {folderpath}", align="left")
            with open(registry, "r") as f:
                data = json.load(f)
                f.close()
            self.parent.load_project(data)
            self.close()

    def oldPrjNotFound(self, folderpath):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)  # Error icon
        msg_box.setWindowTitle("Error Occurred")
        msg_box.setText("This folder does not have old cache memory or may be the project was corrupted.\nDo you want to create a new project in this folder?")
        
        # Add Yes/No buttons
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        # Show the dialog and get the user's response
        response = msg_box.exec_()

        if response == QMessageBox.Yes:
            print("User chose to create a new project.")
            self.new_project_action(folderpath=folderpath)
        else:
            print("Pardon me!!")
            
    def search_recent_projects(self):
        with open(checkGUIcache(), "r") as f:
            df = pd.read_csv(f, sep=",")
            f.close()
        if not df.empty:
            df["dom"] = pd.to_datetime(df["dom"])
            df = df.sort_values(by="dom", ascending=False)
            number_of_rows = df.shape[0]
            self.recent_projects_table.setRowCount(number_of_rows)
            
            for i, row in df.iterrows():
                item = QTableWidgetItem(str(row["folder_location"]))
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.recent_projects_table.setItem(i, 0, item)
                item = QTableWidgetItem(str(row["dom"]))
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.recent_projects_table.setItem(i, 1, item)
            
            self.recent_projects_table.cellDoubleClicked.connect(self.on_cell_double_clicked)

    
    def on_cell_double_clicked(self, row, col):
        """Handles cell double-click event."""        
        project_path = self.recent_projects_table.item(row, 0).text()  # Get clicked cell value
        self.open_old_project_action(folderpath=project_path)


# endregion
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    # app.setStyle('Fusion') 
    application = NoiseShiled()
    application.show()
    sys.exit(app.exec_())

