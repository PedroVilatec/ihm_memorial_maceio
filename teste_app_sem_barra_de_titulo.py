# importing the required libraries
  
from PyQt5.QtWidgets import * 
from PyQt5.QtGui import * 
from PyQt5.QtCore import Qt
import sys
  
  
class Window(QMainWindow):
    def __init__(self):
        super().__init__()
  
        # this will hide the title bar
        self.setWindowFlag(Qt.FramelessWindowHint)
  
        # set the title
        self.setWindowTitle("no title")
  
        # setting  the geometry of window
        self.setGeometry(100, 100, 400, 300)
  
        # creating a label widget
        # by default label will display at top left corner
        self.label_1 = QLabel('no title bar', self)
  
        # moving position
        self.label_1.move(100, 100)
  
        # setting up border and background color
        self.label_1.setStyleSheet("background-color: lightgreen;"
                                    "border: 3px solid green")
  
        # show all the widgets
        self.show()
  
  
# create pyqt5 app
App = QApplication(sys.argv)
  
# create the instance of our Window
window = Window()
# start the app
sys.exit(App.exec())