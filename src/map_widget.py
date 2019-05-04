from pathlib import Path

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QDesktopWidget, QLabel, QScrollArea, QVBoxLayout, QPushButton
from PyQt5.QtGui import QIcon, QPixmap, QPainter

from PyQt5 import QtCore, Qt

from map import *

class Map_Widget(QWidget):

    def __init__(self, map:Map, parentWidget=None):
        super(Map_Widget,self).__init__(parentWidget)
        self._layout = QVBoxLayout()
        self.setLayout(self._layout)
        self._map = map
        self._map_widgets = [] # Widgets that are unique for a map, they need to be removed when changing the map

        self._image_label = QLabel()
        self._name_label = QLabel()
        self._layout.addWidget(self._name_label)
        
        self._image_scroll = QScrollArea()
        self._layout.addWidget(self._image_scroll)
        self._image_scroll.setWidgetResizable(True)
        self._image_scroll_container = QWidget()
        self._image_scroll.setWidget(self._image_label)

        self.load_map(self._map)
        self._image_scroll.adjustSize()

        

    def load_map(self,map:Map):
        for map_widget in self._map_widgets:
            map_widget.deleteLater()
        self._map_widgets = []
        self._map = map
        self._image_label.setPixmap(map.pixmap)
        self._image_label.adjustSize()
        self._name_label.setText(map.map_name)

        self.show_locations()
        print(len(self._map_widgets))
    
    def load_map_by_name(self,map_name:str):
        map_name = map_name.replace(" ","_")
        map_name = map_name.lower()
        map_xml_path= Path("../resources/"+map_name+".xml")
        if not (map_xml_path.exists() and map_xml_path.is_file()):
            print(str(map_xml_path) + " not found")
            return False
        map_to_load = Map(map_xml_path)
        self.load_map(map_to_load)
        return True
    
    def show_locations(self):
        location_list = self._map.locations
        for location in location_list:
            print(location.name)
            location_button = QPushButton(self._image_label)
            location_button.setText(location.name)
            print(location.x)
            print(location.y)
            location_button.move(location.x, location.y)
            location_button.clicked.connect(self.make_map_change(location.name))
            self._map_widgets.append(location_button)

    def make_map_change(self, map_name):
        def change_map_callback():
            self.load_map_by_name(map_name)
        return change_map_callback

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter()
        painter.begin(self._image_label.pixmap())
        painter.setPen(QtCore.Qt.red)
        location_list = self._map.locations
        for location in location_list:
            painter.drawEllipse(location.x, location.y, 30,30)
        painter.end()





