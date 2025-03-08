from src import ANC_interface
from PyQt5.QtWidgets import QApplication

import sys
app = QApplication(sys.argv)
application = ANC_interface()
application.show()
sys.exit(app.exec_())