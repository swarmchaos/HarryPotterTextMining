from pathlib import Path

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QDesktopWidget, QLabel, QScrollArea, QVBoxLayout, QPushButton, QSizePolicy
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QPalette, QPen

from PyQt5 import QtCore, Qt, QtWidgets

from map import *
from route import *

class Map_Widget(QWidget):

    def __init__(self, map:Map, parentWidget=None):
        super(Map_Widget,self).__init__(parentWidget)
        self._layout = QVBoxLayout()
        self.setLayout(self._layout)
        self._map = map
        self._map_widgets = [] # Widgets that are unique for a map, they need to be removed when changing the map

        self._image_label = QLabel()
        self._image_label.setBackgroundRole(QPalette.Base)
        self._image_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self._image_label.setScaledContents(True)
        self._name_label = QLabel()
        self._layout.addWidget(self._name_label)
        
        self._image_scroll = QScrollArea()
        self._layout.addWidget(self._image_scroll)
        self._image_scroll.setWidgetResizable(True)
        self._image_scroll_container = QWidget()
        self._image_scroll.setBackgroundRole(QPalette.Dark)
        self._image_scroll.setWidget(self._image_label)
        self._image_scroll.setVisible(True)

        self.load_map(self._map)
        self._image_scroll.adjustSize()

        self._active_routes = []

        self._animation_timeline = QTimeLine(500)
        self._animation_timeline.setFrameRange(0,10)
        self._animation_timeline.valueChanged.connect(self.update_map)
        self._animation_timeline.setCurveShape(QtCore.QTimeLine.LinearCurve)

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
            location_button.raise_()
            location_button.show()
            self._map_widgets.append(location_button)

    def make_map_change(self, map_name):
        def change_map_callback():
            self.load_map_by_name(map_name)
        return change_map_callback

    def paintPixmap(self,x,y,pixmap):
        painter = QPainter()
        painter.begin(self._image_label.pixmap())
        painter.drawPixmap(x,y,pixmap)
        painter.end()

    def draw_path_by_location(self, start_location_name, end_location_name):
        start_location = self._map.get_location_by_name(start_location_name)
        end_location = self._map.get_location_by_name(end_location_name)
        if start_location == None or end_location == None:
            print("One of the locations "+start_location_name+", "+end_location_name+" is not found on map")
            return
        start_point = [start_location.x, start_location.y]
        end_point = [end_location.x, end_location.y]
        self.drawPath(start_point,end_point)

    def drawPath(self,start_point,end_point):
        print("Draw path")
        d_route = Route()
        d_route.set_route(start_point,end_point,10)
        self._active_routes.append(d_route)
    
    def start_animation(self):
        self._animation_timeline.start()

    def update_map(self):
        print("Update")
        self._image_label.update()
        self.paintEvent(None)

    def paintEvent(self, event):
        super().paintEvent(event)
        paint_pixmap = QPixmap(self._image_label.pixmap())
        painter = QPainter()
        painter.begin(paint_pixmap)
        painter.setPen(QPen(QtCore.Qt.red,1,QtCore.Qt.SolidLine, QtCore.Qt.RoundCap))
        location_list = self._map.locations
        route_list = self._active_routes
        for location in location_list:
            painter.drawEllipse(location.x, location.y, 30,30)
        for route in self._active_routes:
            start_point, end_point = route.get_line_at_frame(self._animation_timeline.currentFrame())
            print(str(self._animation_timeline.currentFrame()) + " " + str(start_point) + " " + str(end_point))
            painter.drawLine(start_point[0],start_point[1],end_point[0],end_point[1])
        painter.end()
        self._image_label.setPixmap(paint_pixmap)





