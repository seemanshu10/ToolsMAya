
import sys
from PySide import QtGui,QtCore


app = QtGui.QGuiApplication(sys.argv)
mainWindow= QtGui.QWidget()
mainWindow.resize(550,400)
mainWindow.setWindowTitle("Pyside Test")
mainWindow.show()
app.exec_()