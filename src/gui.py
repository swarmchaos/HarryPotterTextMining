import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QDesktopWidget, QLabel, QScrollArea, QGridLayout, QListWidget, QListWidgetItem, QVBoxLayout, QCheckBox, QSlider
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5 import QtCore

from map import Map
from map_widget import Map_Widget

from pathlib import Path


class MainWindow(QWidget):

    map_label = None

    def __init__(self):
        super().__init__()
        self._character_list = ["Harry","Ron","Hermione","Dumbledore"]
        self.initUI()

    def initUI(self):
        self.resize(800,800)
        self.setWindowTitle("Text Mining Project")
        self.center()

        self._layout = QGridLayout()
        self.setLayout(self._layout) 

        start_button = QPushButton('Start')
        start_button.resize(start_button.sizeHint())
        start_button.clicked.connect(self.start_timeline)
        self._layout.addWidget(start_button,4,6)
  
        map_to_load = Map(Path('../resources/hogwarts.xml'))
        self.map_widget = Map_Widget(map_to_load)
        self._layout.addWidget(self.map_widget,0,0,4,6)

        self._character_scroll = QScrollArea()
        self._layout_character_scroll = QVBoxLayout()
        self._character_scroll.setLayout(self._layout_character_scroll)
        self._layout.addWidget(self._character_scroll,0,6,1,2)

        self.update_character_list()

        self._time_slider = QSlider(QtCore.Qt.Horizontal)
        self._time_slider.setMinimum(0)
        self._time_slider.setMaximum(10) # TODO Change to correct number
        self._layout.addWidget(self._time_slider,4,0,-1,6)

    def update_character_list(self):
        for character in self._character_list:
            character_checkbox = QCheckBox(character)
            self._layout_character_scroll.addWidget(character_checkbox)
    
    def start_timeline(self):
        print("Start")
        self.next_step()
    
    def next_step(self):
        slider_val = self._time_slider.value()
        self._time_slider.setValue(slider_val+1)
    def previous_step(self):
        slider_val = self._time_slider.value
        self._time_slider.setValue(slider_val-1)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())



if __name__ == "__main__":
    app = QApplication(sys.argv)
    m = MainWindow()
    m.show()
    sys.exit(app.exec())
