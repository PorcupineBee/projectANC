from UI.InteractiveDisplay import Ui_ANC_interface
from UI.startup import Ui_NoiseShieldPopUp
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMdiArea, QMdiSubWindow, 
                           QWidget, QVBoxLayout, QPushButton, QLabel, QToolBar,
                           QMenuBar, QStatusBar, QAction, QTableWidgetItem, QFileDialog,
                           QHBoxLayout, QSplitter, QGroupBox, 
                           QTreeWidget, QFrame, QDoubleSpinBox, QTreeWidgetItem,
                           QFontDialog, QMessageBox, QCheckBox, QSizePolicy,
                           QToolButton
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
from .utiles import (getAudioSignal_n_Time, signal_registry, getDefultSpectrumWidget, getRotatedLabel)
from functools import partial 
from UI.plot_tf_spectrum_static import TimeFrequencyWidget 


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
        
        self.start_recording_btn.clicked.connect(self.start_recording_action)
        self.add_Audio_btn.clicked.connect(self.add_Audio_action)
        self.browse_noise_audio_btn.clicked.connect(self.browse_noise_audio_action)
        self.noise_type_comboBox.currentIndexChanged.connect(self.noise_type_comboaction)
        
        self.extra_ui()
        self.spectrumViewbox.setRowCount(2) # 1: inp signal spec, 2: op signal spec
        self.init_spectrum_widgets()
        # self._temp_add_a_music()
        self.order_key = dict()
        
    

    def start_recording_action(self, flag):
        """
        start live audio recording
        """
        if flag:
            ...
            # pyaudio functionalities for recording audio
            # as well as update input spectrum frame
        else:
            # stop that pyaudio functionalities
            ...

    def add_Audio_action(self):
        """
        Add main Audio file this audio can be clear or noisy
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
        Add Noise file if available
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
        selecte a nose audio from available noise files
        """
        path = "A:/NoiseShiled_noise_data"  # FIXME different path for different project
        audio_file = os.path.join(path, self.noise_file_data[f"{index+1}"])     
        self.addASignalStremer("noise", audio_file)

    
    
    def addASignalStremer(self, stype:str, audio_file:str, ):
        """
        Adds a signal streamer to the project registry and updates the UI with a new plot widget.

        Args:
            stype (str): The type of the signal (e.g., "signal", "Noise").
            audio_file (str): The file path of the audio file to be added.

        Functionality:
            - Loads the audio signal and its corresponding time data from the provided file.
            - Registers the signal in the project registry.
            - Configures the plot settings for the signal and creates a time-series plot widget.
            - Updates the spectrum view box in the UI with the new plot widget.
            - Maintains an order-key mapping for the signal and its associated widget.
        """
        
        signal, time, order, signal_key = self.project_registry.add_signal(fpath=audio_file, type=stype)
        
        plotsetting = defaultPlotSettings()
        plotsetting["signal"] = signal
        plotsetting["time"] = time
        plotsetting["signal_info"]["type"] = stype
        
        tspwidegt = TimeSeriesPlotWidget(**plotsetting) 
        self.spectrumViewbox.setRowCount(order+3)
        self.spectrumViewbox.setRowHeight(order+2, 200)
        self.spectrumViewbox.setCellWidget(order+2, 1, tspwidegt)
        # label adding 
        _label = getRotatedLabel(name=os.path.basename(audio_file), font_size=6, height=200)
        self.spectrumViewbox.setCellWidget(order+2, 0, _label)
        self.order_key.update({order:
            dict(
                name=signal_key,
                widget=tspwidegt
                )
            })
        
        # add item in signalList_treeWidget
        basename = os.path.basename(audio_file)
        self.addSignalItem(basename, order)
        

    def showStatus(self, message:str=None, align="left",**kwargs):
        """
        Displays a status message on the status bar with optional alignment.
        Args:
            message (str, optional): The message to display. Defaults to None.
            align (str, optional): The alignment of the message. Can be "left" or "right". Defaults to "left".
            **kwargs: Additional keyword arguments for future extensions.
        Behavior:
            - If `align` is "left", the message is shown on the status bar with a specific style.
            - If `align` is "right", the message is set to a status text widget.
        """
        if align=="left":
            self.statusbar.showMessage(message)
            self.statusbar.setStyleSheet("color: #bbb;padding: 0px 5px; background: None;")
        elif align=="right":
            self.status_text.setText(message)
            
    def extra_ui(self):
        """
        UI for Right side status 
        """
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
            
        # two more colums in self.signalList_treeWidget 
        # for checkbox and delete options
        self.signalList_treeWidget.setColumnCount(2)
        self.signalList_treeWidget.setColumnWidth(0, 150)
        self.signalList_treeWidget.setColumnWidth(1, 50)
    
    def load_project(self, registry:dict):
        """
        load save denoising project
        Args:
            registry (dict): _description_
        """
        self.project_registry.signals_df = registry
    
    def save_project(self):
        """
        Save this project
        """
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

    def init_spectrum_widgets(self):
        """
        Static input audio time frequency spectrum 
        """
        if not hasattr(self, "static_input_spect_widget"):
            # create default static_input_spect_widget attribute
            self.static_input_spect_widget: TimeFrequencyWidget = getDefultSpectrumWidget()
            _label = getRotatedLabel("Input signal", height=300)
            self.spectrumViewbox.setCellWidget(0, 0, _label)

            self.spectrumViewbox.setRowHeight(0, 300)
            self.spectrumViewbox.setCellWidget(0, 1, self.static_input_spect_widget)
            
            self.addSignalItem("Input Signal", 0, parmanent=True)
        
        if not hasattr(self, "static_output_spect_widget"):
            # create default static_input_spect_widget attribute
            self.static_output_spect_widget: TimeFrequencyWidget = getDefultSpectrumWidget()
            
            _label = getRotatedLabel("Enhanced signal", height=300)
            self.spectrumViewbox.setCellWidget(1, 0, _label)
            self.spectrumViewbox.setRowHeight(1, 300)
            self.spectrumViewbox.setCellWidget(1, 1, self.static_output_spect_widget)
        
            self.addSignalItem("Enhanced Signal", 1, parmanent=True)
        
# endregion

        
    def addSignalItem(self, name:str, 
                      order, 
                      checked:bool=True, 
                      parmanent:bool=False):
        treeItem = QTreeWidgetItem()
        treeItem.setText(0, name)
        if parmanent : order -= 2 
        self.signalList_treeWidget.insertTopLevelItem(order+2, treeItem)
        if not parmanent:
            # other audio streams
            opWidget = QWidget()
            layout = QHBoxLayout(opWidget)
            signal_check = QCheckBox(self)
            signal_check.setChecked(checked)
            layout.addWidget(signal_check)
            
            rem_sgnal = QPushButton(text="x", flat=True)
            rem_sgnal.clicked.connect(lambda _, key=self.order_key[order]["name"]: self.removeSignal(key))
            rem_sgnal.setStyleSheet("color:red; background:Transparent;font-weight:bold; font-size:15px;padding:0px 2px;")
            layout.addWidget(rem_sgnal)
            layout.setContentsMargins(1, 1, 1, 1)  
            opWidget.setLayout(layout)
            self.signalList_treeWidget.setItemWidget(treeItem, 1, opWidget)
        
            self.order_key[order].update(treeItem=treeItem)
        
        
        
        
    def removeSignal(self, signal_key):
        prev_order = self.project_registry.signals_df[signal_key]["order"]
        self.project_registry.signals_df.pop(signal_key)
        
        row_id = prev_order + 2
        self.spectrumViewbox.removeRow(row_id)      
        self.signalList_treeWidget.takeTopLevelItem(row_id)
        
        for o in range(prev_order, len(self.order_key) - 1):
            self.order_key[o] = self.order_key[o+1]
            name = self.order_key[o]["name"]
            self.project_registry.signals_df[name]["order"] = o
            
        self.order_key.pop(len(self.order_key) - 1)
        
        
        # self.updateInputAudio()
        
    def updateInputAudio(self):
        self.project_registry.signals_df
        self.static_input_spect_widget.updateAudio()
        
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

