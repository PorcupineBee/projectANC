from src import NoiseShiled
from PyQt5.QtWidgets import QApplication

import sys
app = QApplication(sys.argv)
try:
    application = NoiseShiled()
    application.show()
    sys.exit(app.exec_())
except Exception as e:
    print( e)
    raise e