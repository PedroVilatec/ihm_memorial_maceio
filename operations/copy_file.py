from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
import os
class ProgressDialog(QDialog):

	def __init__(self, parent, source, destination):
		QDialog.__init__(self, parent)
		uic.loadUi('/home/pi/CAPELA/ihm/operations/dialog.ui', self)
		flags = Qt.WindowFlags()
		flags |= Qt.X11BypassWindowManagerHint
		self.setWindowFlags(flags)		
		self.parent = parent
		self.source = source
		self.destination = destination
		# self.add_diag.setupUi(self)

		self.label.setText("Copying: %s" % (self.source))

		self.progressBar.setMinimum(0)
		self.progressBar.setMaximum(100)
		self.progressBar.setValue(0)

		self.show()
		self.copy()

	def copy(self):

		copy_thread = CopyThread(self, self.source, self.destination)
		copy_thread.procPartDone.connect(self.update_progress)
		copy_thread.procDone.connect(self.finished_copy)
		copy_thread.start()

	def update_progress(self, progress):
		self.progressBar.setValue(progress)

	def finished_copy(self, state):
		self.close()

class CopyThread(QtCore.QThread):

	procDone = QtCore.pyqtSignal(bool)
	procPartDone = QtCore.pyqtSignal(int)

	def __init__(self, parent, source, destination):
		QtCore.QThread.__init__(self, parent)
		self.source = source
		self.destination = destination

	def run(self):
		self.copy()
		self.procDone.emit(True)

	def copy(self):
		source_size = os.stat(self.source).st_size
		copied = 0
		source = open(self.source, "rb")
		target = open(self.destination, "wb")

		while True:
			chunk = source.read(1024)
			if not chunk:
				break
			target.write(chunk)
			copied += len(chunk)
			self.procPartDone.emit(copied * 100 / source_size)

		source.close()
		target.close()

class ProgressMessageBox(QMessageBox):
	def __init__(self, source, destination, parent=None):
		super(ProgressMessageBox, self).__init__(parent)
		
		self.msgBox = self
		self.texto = '''<h2><strong><span style="color: #0000ff;">{}</span></strong></h2>'''.format("Copiando...")
		self.msgBox.setText(self.texto)
		flags = Qt.WindowFlags()
		flags |= Qt.SplashScreen
		self.msgBox.setWindowFlags(flags)
		bt1   = QPushButton("Cancelar")
		
		# bt1.setStyleSheet(btnStyle.btn_style())
		bt1.setMinimumWidth(180)
		bt1.setMaximumWidth(180)
		bt1.setMinimumHeight(80)
		self.msgBox.addButton(bt1, QMessageBox.YesRole)
		self.source = source
		self.destination = destination		
		copy_thread = CopyThread(self, self.source, self.destination)
		copy_thread.procPartDone.connect(self.update_text)
		copy_thread.procDone.connect(self.finished_copy)
		copy_thread.start()		
		self.exec_()
				
	def finished_copy(self, state):
		self.close()
		
	def update_progress(self, progress):
		self.setText('''<h2><strong><span style="color: #0000ff;">Copiando {}%</span></strong></h2>'''.format(progress))