import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QDesktopWidget, QLabel, QScrollArea, QGridLayout, QListWidget, QListWidgetItem, QVBoxLayout, QCheckBox, QSlider
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5 import QtCore

from map import Map
from map_widget import Map_Widget

from pathlib import Path


class MainWindow(QWidget):

    map_label = None

    timeline_started = False

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

        self._start_button = QPushButton('Start')
        self._start_button.resize(self._start_button.sizeHint())
        self._start_button.clicked.connect(self.start_timeline)
        self._layout.addWidget(self._start_button,4,6)
  
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

        self._timeline = QtCore.QTimeLine(10000, self)
        self._timeline.setFrameRange(0,10)
        #self._timeline.frameChanged[int].connect(self._time_slider.setValue)
        self._timeline.frameChanged[int].connect(self.next_step)
        self._timeline.setCurveShape(QtCore.QTimeLine.LinearCurve)



    def update_character_list(self):
        for character in self._character_list:
            character_checkbox = QCheckBox(character)
            self._layout_character_scroll.addWidget(character_checkbox)
    
    def start_timeline(self):
        current_state = self._timeline.state()
        if(current_state == QtCore.QTimeLine.NotRunning):
            self._timeline.start()
            self._start_button.setText("Start")
        elif(current_state == QtCore.QTimeLine.Paused):
            self._timeline.resume()
            self._start_button.setText("Pause")
        elif(current_state == QtCore.QTimeLine.Running):
            self._timeline.setPaused(True)
            self._start_button.setText("Resume")
    
    def next_step(self):
        current_chapter = self._timeline.currentFrame()
        self._time_slider.setValue(current_chapter)
        location_names = self.get_location_names_for_chapter(current_chapter)
        self.map_widget.draw_path_by_location(location_names[0], location_names[1])
        self.map_widget.update_map()
        self.map_widget.start_animation()


    def previous_step(self):
        slider_val = self._time_slider.value
        self._time_slider.setValue(slider_val-1)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def get_location_names_for_chapter(self,chapter:int):
        ret = ["",""]
        if(chapter==0):
            ret[0] = "Hogsmeade Station"
            ret[1] = "Hogsmeade Station"
        if chapter == 1:
            ret[0] = "Hogsmeade Station"
            ret[1] = "Whomping Willow"
        if chapter == 2:
            ret[0] = "Whomping Willow"
            ret[1] = "Forbidden Forest"
        return ret




if __name__ == "__main__":
    app = QApplication(sys.argv)
    m = MainWindow()
    m.show()
    sys.exit(app.exec())
