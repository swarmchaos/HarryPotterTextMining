from pathlib import Path

from PyQt5.QtGui import QPixmap
import xml.etree.ElementTree as ET

class Location:
    def __init__(self, name,x:int,y:int):
        self._name = name
        self._x = x
        self._y = y
    @property
    def x(self):
        return self._x
    @property
    def y(self):
        return self._y
    @property
    def name(self):
        return self._name

class Map:
    def __init__(self,map_name, image_path):
        self._pixmap = QPixmap(image_path)
        self._map_name = map_name
        self._location_list = []
        self._location_dict = {}

    def __init__(self,xml_path:Path):
        self._location_list = []
        self._location_dict = {}
        self.load_map_from_xml(xml_path)

    def load_map_from_xml(self, xml_path:Path):
        xml_tree = ET.parse(str(xml_path))
        xml_root = xml_tree.getroot()
        map_name_node = xml_root.find("./Name")
        self._map_name = map_name_node.text
        map_path_node = xml_root.find("./Image")
        image_path = xml_path.parent / (map_path_node.text)
        print(image_path)
        self._pixmap = QPixmap(str(image_path))
        location_node_list = xml_root.findall("./Location")
        for location_node in location_node_list:
            self.process_location_node(location_node)

    def process_location_node(self,location_node):
        name_node = location_node.find('Name')
        x_node = location_node.find("X")
        y_node = location_node.find("Y")

        location = Location(name_node.text,int(x_node.text),int(y_node.text))
        self._location_list.append(location)
        self._location_dict[name_node.text] = len(self._location_list ) -1

    def get_location_by_name(self, location_name):
        if(location_name in self._location_dict):
            return self._location_list[self._location_dict.get(location_name)]
        else:
            return None

    @property
    def pixmap(self):
        return self._pixmap
    @property
    def map_name(self):
        return self._map_name
    @property
    def height(self):
        return self._pixmap.height()
    @property
    def width(self):
        return self._pixmap.width()
    @property
    def locations(self):
        return self._location_list