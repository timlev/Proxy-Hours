#!/usr/bin/python

import Proxy_Hours, proxyhours_gather_all_data
from PySide import QtCore, QtGui

def selectFile():
	name = QtGui.QFileDialog.getOpenFileName()
	ui.FilelineEdit.setText(name)
	nametxt = str(ui.FilelineEdit.text())
	write_out_0, write_out_1, write_out_2, write_out_3 = proxyhours_gather_all_data.proxy_hours(nametxt)
	ui.log_lineEdit.setText(write_out_1)
	ui.all_data_lineEdit.setText(write_out_2)
	ui.time_lineEdit.setText(write_out_3)
	ui.tableWidget.setRowCount(len(write_out_0))
	for pos, row in enumerate(write_out_0):
		add_row(pos,row)

def add_row(pos,row):
	r = pos
	for c, t in enumerate(row):
		ui.tableWidget.setItem(r,c,QtGui.QTableWidgetItem(str(t)))

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MainWindow = Proxy_Hours.QtGui.QMainWindow()
    ui = Proxy_Hours.Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    ui.OpenpushButton.clicked.connect(selectFile)
    ui.actionOpen.triggered.connect(selectFile)
    ui.actionQuit.triggered.connect(QtCore.QCoreApplication.instance().quit)
    sys.exit(app.exec_())
