from pathlib import Path

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QDesktopWidget, QLabel, QScrollArea, QVBoxLayout, QPushButton, QSizePolicy, QListWidget
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QPalette, QPen

from PyQt5 import QtCore, Qt, QtWidgets

from map import *
from route import *

class LocationWindow(QWidget):
    def __init__(self,location:Location, parentWidget=None):
        super(LocationWindow,self).__init__(parentWidget)
        self._layout = QVBoxLayout()
        self.setLayout(self._layout)
        self._location = location
        self.initUI()
        self.setWindowTitle(location.name)
    
    def initUI(self):
        self._character_scroll = QScrollArea()
        self._layout_character_scroll = QVBoxLayout()
        self._character_scroll.setLayout(self._layout_character_scroll)
        self._layout.addWidget(self._character_scroll)
        self._character_list = QListWidget()
        self._layout_character_scroll.addWidget(self._character_list)

        self._change_to_map_button = QPushButton("Change to detail map")
        self._layout.addWidget(self._change_to_map_button)

        self.update_character_list()

    def update_character_list(self):
        self._character_list.clear()
        self._character_list.addItems(self._location.current_characters)
        self._character_list.sortItems()

    def set_change_map_action(self,callback):
        self._change_to_map_button.clicked.connect(callback)

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

        self._location_window_dict = {}
        self._active_routes = {}
        self._active_route_characters = []
        self._routes_not_mapped = {}
        self._routes_mapped = {}


        self.load_map(self._map)
        self._image_scroll.adjustSize()

        self._animation_timeline = QTimeLine(500)
        self._animation_timeline.setFrameRange(0,10)
        self._animation_timeline.valueChanged.connect(self.update_map)
        self._animation_timeline.setCurveShape(QtCore.QTimeLine.LinearCurve)

    def load_map(self,map:Map):
        for map_widget in self._map_widgets:
            map_widget.deleteLater()
        self._routes_mapped[self._map.map_name] = self._active_routes
        if map.map_name in self._routes_mapped:
            self._active_routes = self._routes_mapped[map.map_name]
        else:
            self._active_routes = {}
        self._map_widgets = []
        self._map = map
        self._image_label.setPixmap(map.pixmap)
        self._image_label.adjustSize()
        self._name_label.setText(map.map_name)
        self.show_locations()
        routes_to_be_processed = self._routes_not_mapped.copy()
        for key in routes_to_be_processed:
            routes_char = routes_to_be_processed[key].copy()
            for r in routes_char:
                self.draw_path_by_location(r[0],r[1],r[2],key)
        self.reload_map()
    
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
            #print(location.name)
            location_button = QPushButton(self._image_label)
            location_button.setText(location.name)
            #print(location.x)
            #print(location.y)
            location_button.move(location.x, location.y)
            #location_button.clicked.connect(self.make_map_change(location.name))
            location_button.clicked.connect(self.open_location_window(location.name))
            location_button.raise_()
            location_button.show()
            self._location_window_dict[location.name] = LocationWindow(self._map.get_location_by_name(location.name))
            self._location_window_dict[location.name].set_change_map_action(self.make_map_change(location.name))
            self._map_widgets.append(location_button)

    def open_location_window(self, location_name:str):
        def open_location_window_callback():
            self._location_window_dict[location_name].update_character_list()
            self._location_window_dict[location_name].show()
        return open_location_window_callback

    def make_map_change(self, map_name):
        def change_map_callback():
            self.load_map_by_name(map_name)
        return change_map_callback

    def paintPixmap(self,x,y,pixmap):
        painter = QPainter()
        painter.begin(self._image_label.pixmap())
        painter.drawPixmap(x,y,pixmap)
        painter.end()

    def is_location_on_map(self,location_name):
        return self._map.is_location_on_map(location_name)

    def draw_path_by_location(self, start_location_name, end_location_name, colour, character_name=""):
        start_location = self._map.get_location_by_name(start_location_name)
        end_location = self._map.get_location_by_name(end_location_name)
        if start_location == None or end_location == None:
            if start_location == None and not end_location == None:
                # last position on map is maybe not left
                start_location = end_location
                start_point = [start_location.x, start_location.y]
                end_point = [end_location.x, end_location.y]
                end_location.add_character_to_location(character_name)
                self.drawPath(start_point,end_point, colour, char_name=character_name)
                return
            else:
                if end_location == None and not start_location == None:
                    start_location.character_leaves(character_name)
                if not character_name in self._routes_not_mapped:
                    self._routes_not_mapped[character_name] = []
                self._routes_not_mapped[character_name].append([start_location_name, end_location_name, colour])
                return
        start_location.character_leaves(character_name)
        start_point = [start_location.x, start_location.y]
        end_point = [end_location.x, end_location.y]
        end_location.add_character_to_location(character_name)
        self.drawPath(start_point,end_point, colour, char_name=character_name)

    def drawPath(self,start_point,end_point, colour, char_name=""):
        d_route = Route()
        d_route.set_colour(colour)
        d_route.set_route(start_point,end_point,10)
        if not char_name in self._active_routes:
            self._active_routes[char_name] = []
        self._active_routes[char_name].append(d_route)
    
    def start_animation(self):
        self._animation_timeline.start()

    def update_map(self):
        self._image_label.update()
        self.paintEvent(None)
    
    def add_active_character(self, name, colour):
        self._active_route_characters.append(name)
        if name in self._active_routes:
            for route in self._active_routes[name]:
                route.set_colour(colour)
        self.reload_map()

    def remove_active_character(self, name):
        new_active = []
        for character in self._active_route_characters:
            if not character == name:
                new_active.append(character)
        self._active_route_characters = new_active
        self.reload_map()

    def reload_map(self):
        self.clear_pixmap()
        self.paintEvent(None)

    def clear_pixmap(self):
        self._image_label.setPixmap(self._map.pixmap)

    def paintEvent(self, event):
        super().paintEvent(event)
        paint_pixmap = QPixmap(self._image_label.pixmap())
        painter = QPainter()
        painter.begin(paint_pixmap)
        painter.setPen(QPen(QtCore.Qt.red,1,QtCore.Qt.SolidLine, QtCore.Qt.RoundCap))
        location_list = self._map.locations
        route_list = self._active_routes
        #for location in location_list:
        #    painter.drawEllipse(location.x, location.y, 30,30)
        for key in self._active_routes:
            if not key in self._active_route_characters:
                continue
            for route in self._active_routes[key]:
                painter.setPen(QPen(route.get_colour(),5,QtCore.Qt.SolidLine, QtCore.Qt.RoundCap))
                start_point, end_point = route.get_line_at_frame(self._animation_timeline.currentFrame())
                painter.drawLine(start_point[0],start_point[1],end_point[0],end_point[1])
        painter.setPen(QPen(QtCore.Qt.red,1,QtCore.Qt.SolidLine, QtCore.Qt.RoundCap))
        painter.end()
        self._image_label.setPixmap(paint_pixmap)

