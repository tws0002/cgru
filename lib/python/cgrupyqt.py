QtCore = None
QtGui = 'QtGui'
QtNetwork = 'QtNetwork'
List = ['QtCore', 'QtGui', 'QtNetwork','QtWidgets']
PythonQtType = None
PySide = True

try:
	PythonQt = __import__('PySide2', globals(), locals(), List)
	PythonQtType = 'PySide2'
except ImportError:
	PythonQt = __import__('PyQt5', globals(), locals(), List)
	PythonQtType = 'PyQt5'

QtCore = PythonQt.QtCore
QtGui = PythonQt.QtGui
QtNetwork = PythonQt.QtNetwork
QtWidgets = PythonQt.QtWidgets

print(PythonQtType + ' module imported.')

if PythonQtType == 'PyQt5':
	print('You can install PySide2 if interested in LGPL license.')
	PySide = False


def GetOpenFileName(i_qwidget, i_title, i_path=None):
	if i_path is None:
		i_path = '.'
	if PySide:
		afile, filter = \
			QtWidgets.QFileDialog.getOpenFileName(i_qwidget, i_title, i_path)
		return afile
	return str(QtWidgets.QFileDialog.getOpenFileName(i_qwidget, i_title, i_path))


def GetSaveFileName(i_qwdget, i_title, i_path=None):
	if i_path is None:
		i_path = '.'
	if PySide:
		afile, filter = \
			QtWidgets.QFileDialog.getSaveFileName(i_qwdget, i_title, i_path)
		return afile
	return str(QtWidgets.QFileDialog.getSaveFileName(i_qwdget, i_title, i_path))
