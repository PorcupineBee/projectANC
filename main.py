from src import NoiseShiled
from PyQt5.QtWidgets import QApplication

import sys
app = QApplication(sys.argv)
application = NoiseShiled()
application.show()
sys.exit(app.exec_())