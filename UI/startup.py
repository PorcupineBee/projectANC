# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'startup.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_NoiseShieldPopUp(object):
    def setupUi(self, NoiseShieldPopUp):
        NoiseShieldPopUp.setObjectName("NoiseShieldPopUp")
        NoiseShieldPopUp.resize(520, 371)
        NoiseShieldPopUp.setStyleSheet("QWidget {\n"
"    background-color: rgb(50, 50, 50);\n"
"    font: 8pt \"Comic Sans MS\";\n"
"}\n"
"QGroupBox {\n"
"    border: 2px solid #777; /*rgb(255, 255, 127);*/ /* Slightly lighter border */\n"
"    border-radius: 8px;\n"
"    margin-top: 30px; /* Space for title */\n"
"    font-size: 14px;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"/* GroupBox Title */\n"
"QGroupBox::title {\n"
"    subcontrol-origin: margin;\n"
"    subcontrol-position: top left; /* Center the title */\n"
"    background-color: transparent; /* No background for title */\n"
"    padding: 5px 10px;\n"
"    color: rgb(214, 211, 230) /*rgb(255, 255, 127); /* Blue title color */\n"
"}\n"
"\n"
"/* GroupBox When Disabled */\n"
"QGroupBox:disabled {\n"
"    color: #7f8c8d; /* Faded text color */\n"
"    border-color: #3a4f5c;\n"
"}")
        self.centralwidget = QtWidgets.QWidget(NoiseShieldPopUp)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.frame = QtWidgets.QFrame(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.groupBox = QtWidgets.QGroupBox(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setStyleSheet("QPushButton {\n"
"    background-color: rgb(191, 200, 187);\n"
"    color: #555; /* */\n"
"    border:None;\n"
"  /*  border-bottom: 3px solid rgb(160, 160, 0); \n"
"    border-right: 3px solid rgb(160, 160, 0);*/\n"
"    border-radius: 5px;\n"
"    padding: 8px 20px;\n"
"    font-size: 14px;\n"
"font-weight: bold;\n"
"}")
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.new_project_btn = QtWidgets.QPushButton(self.groupBox)
        self.new_project_btn.setObjectName("new_project_btn")
        self.verticalLayout.addWidget(self.new_project_btn)
        self.open_old_project_btn = QtWidgets.QPushButton(self.groupBox)
        self.open_old_project_btn.setObjectName("open_old_project_btn")
        self.verticalLayout.addWidget(self.open_old_project_btn)
        self.horizontalLayout.addWidget(self.groupBox)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout_3.addWidget(self.frame)
        self.groupBox_2 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.recent_projects_table = QtWidgets.QTableWidget(self.groupBox_2)
        self.recent_projects_table.setStyleSheet("QTableWidget {\n"
"    background-color: #2b2b2b;\n"
"    color: #ffffff;\n"
"    gridline-color: #444;\n"
"    selection-background-color: #44475a;\n"
"    selection-color: #ffffff;\n"
"    border: 1px solid #555;\n"
"}\n"
"\n"
"QHeaderView::section {\n"
"    background-color: #3c3f41;\n"
"    color: #ffffff;\n"
"    padding: 0px;\n"
"    border: 1px solid #555;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"QTableWidget QTableCornerButton::section {\n"
"    background-color: #3c3f41;\n"
"    border: 1px solid #555;\n"
"}\n"
"\n"
"QTableWidget QTableView::item {\n"
"    border: 1px solid #555;\n"
"}\n"
"\n"
"QTableWidget QTableView::item:selected {\n"
"    background-color: #6272a4;\n"
"    color: #ffffff;\n"
"}\n"
"\n"
"QScrollBar:vertical {\n"
"    border: none;\n"
"    background: #2b2b2b;\n"
"    width: 10px;\n"
"    margin: 0px 0px 0px 0px;\n"
"}\n"
"\n"
"QScrollBar::handle:vertical {\n"
"    background: #555;\n"
"    min-height: 20px;\n"
"    border-radius: 5px;\n"
"}\n"
"\n"
"QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {\n"
"    background: none;\n"
"    border: none;\n"
"}\n"
"\n"
"QScrollBar:horizontal {\n"
"    border: none;\n"
"    background: #2b2b2b;\n"
"    height: 10px;\n"
"    margin: 0px 0px 0px 0px;\n"
"}\n"
"\n"
"QScrollBar::handle:horizontal {\n"
"    background: #555;\n"
"    min-width: 20px;\n"
"    border-radius: 5px;\n"
"}\n"
"\n"
"QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {\n"
"    background: none;\n"
"    border: none;\n"
"}\n"
"")
        self.recent_projects_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.recent_projects_table.setObjectName("recent_projects_table")
        self.recent_projects_table.setColumnCount(2)
        self.recent_projects_table.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.recent_projects_table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.recent_projects_table.setHorizontalHeaderItem(1, item)
        self.recent_projects_table.horizontalHeader().setCascadingSectionResizes(True)
        self.recent_projects_table.horizontalHeader().setDefaultSectionSize(220)
        self.recent_projects_table.horizontalHeader().setMinimumSectionSize(20)
        self.recent_projects_table.horizontalHeader().setStretchLastSection(False)
        self.verticalLayout_2.addWidget(self.recent_projects_table)
        self.verticalLayout_3.addWidget(self.groupBox_2)
        NoiseShieldPopUp.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(NoiseShieldPopUp)
        self.statusbar.setObjectName("statusbar")
        NoiseShieldPopUp.setStatusBar(self.statusbar)

        self.retranslateUi(NoiseShieldPopUp)
        QtCore.QMetaObject.connectSlotsByName(NoiseShieldPopUp)

    def retranslateUi(self, NoiseShieldPopUp):
        _translate = QtCore.QCoreApplication.translate
        NoiseShieldPopUp.setWindowTitle(_translate("NoiseShieldPopUp", "NoiseShield"))
        self.groupBox.setTitle(_translate("NoiseShieldPopUp", "Start"))
        self.new_project_btn.setText(_translate("NoiseShieldPopUp", "Select a folder for new project"))
        self.open_old_project_btn.setText(_translate("NoiseShieldPopUp", "Open an old project folder"))
        self.groupBox_2.setTitle(_translate("NoiseShieldPopUp", "Recent"))
        item = self.recent_projects_table.horizontalHeaderItem(0)
        item.setText(_translate("NoiseShieldPopUp", "project locations"))
        item = self.recent_projects_table.horizontalHeaderItem(1)
        item.setText(_translate("NoiseShieldPopUp", "d.o.m."))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    NoiseShieldPopUp = QtWidgets.QMainWindow()
    ui = Ui_NoiseShieldPopUp()
    ui.setupUi(NoiseShieldPopUp)
    NoiseShieldPopUp.show()
    sys.exit(app.exec_())
