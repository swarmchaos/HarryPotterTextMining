import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QDesktopWidget, QLabel, QScrollArea, QGridLayout, QListWidget, QListWidgetItem, QVBoxLayout, QCheckBox, QSlider, QFrame
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5 import QtCore

from map import Map
from map_widget import Map_Widget

from pathlib import Path

from spacy_pipeline import *


class MainWindow(QWidget):

    map_label = None

    timeline_started = False

    _location_dict = {}

    def __init__(self):
        super().__init__()
        self._location_dict = {}
        self._orig_location_dict_list = []
        self._n_chapters = 0
        self._start_book_nr = 4
        self._end_book_nr = 4
        #for i in range(self._start_book_nr,self._end_book_nr + 1):
        #    book_n_chapters, book_location_dict = get_person_location(i)
        #    self._orig_location_dict_list.append([book_n_chapters, book_location_dict])
        #    self._n_chapters, self._location_dict = self.merge_location_dict(self._location_dict.copy(),self._n_chapters, book_location_dict, book_n_chapters)
        self._n_chapters, self._location_dict = get_person_location(self._start_book_nr)
        print(self._n_chapters)
        #self._n_chapters = 10
        #self._location_dict = {}
        self._character_list = []
        self._current_position_dict = {}
        self._colour_dict = {}
        self._available_colours_qt = [QtCore.Qt.red, QtCore.Qt.blue, QtCore.Qt.magenta, QtCore.Qt.cyan, QtCore.Qt.green]
        self._available_colours = ["red", "blue", "magenta", "cyan", "green"]
        for key in self._location_dict:
            self._current_position_dict[key] = ""
            self._colour_dict[key] = ["white", QtCore.Qt.white]
            self._character_list.append(key)
        self._active_characters = ["Harry","Ron","Hermione"]
        #self._active_characters = ["Harry"]
        for i in range(len(self._active_characters)):
            self._colour_dict[self._active_characters[i]] = [self._available_colours[i % len(self._available_colours)] , self._available_colours_qt[i % len(self._available_colours)]]

        self.initUI()

        for character in self._active_characters:
            self.map_widget.add_active_character(character, self._colour_dict[character][1])

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
  
        map_to_load = Map(Path('../resources/hogwarts_castle.xml'))
        self.map_widget = Map_Widget(map_to_load)
        self._layout.addWidget(self.map_widget,0,0,4,6)

        self._topic_graph_label = QLabel()
        self.load_topic_graph(self._start_book_nr)
        self._layout.addWidget(self._topic_graph_label,0,6,1,2)

        self._character_scroll = QScrollArea()
        self._character_scroll.setWidgetResizable(True)
        inner = QFrame(self._character_scroll)
        self._layout_character_scroll = QVBoxLayout()
        inner.setLayout(self._layout_character_scroll)
        #self._character_scroll.setLayout(self._layout_character_scroll)
        #self._character_scroll.setWidget(self._layout_character_scroll.widget())
        self._character_scroll.setWidget(inner)
        self._layout.addWidget(self._character_scroll,3,6,1,2)

        self.update_character_list()

        self._time_slider = QSlider(QtCore.Qt.Horizontal)
        self._time_slider.setMinimum(0)
        self._time_slider.setMaximum(self._n_chapters) # TODO Change to correct number
        self._layout.addWidget(self._time_slider,4,0,-1,6)

        self._timeline = QtCore.QTimeLine(10000 * (self._end_book_nr - self._start_book_nr + 1), self)
        self._timeline.setFrameRange(0,self._n_chapters)
        #self._timeline.frameChanged[int].connect(self._time_slider.setValue)
        self._timeline.frameChanged[int].connect(self.next_step)
        self._timeline.setCurveShape(QtCore.QTimeLine.LinearCurve)

    def merge_location_dict(self, location_dict_one, n_chapters_one, location_dict_two, n_chapters_two):
        location_dict_ret = location_dict_one.copy()
        chapter_offset = n_chapters_one
        for key in location_dict_two:
            for location_list in location_dict_two[key]:
                location_list[2] += chapter_offset
            if key in location_dict_one:
                location_dict_ret[key].append(location_dict_two[key])
            else:
                location_dict_ret[key] = location_dict_two[key]
        n_chapters_ret = n_chapters_two + n_chapters_one
        return [n_chapters_ret, location_dict_ret]


    def load_topic_graph(self,book_nr):
        topic_pixmap = QPixmap(f"../data/graphs/Book{book_nr}Stream.png")
        topic_pixmap = topic_pixmap.scaledToHeight(200)
        topic_pixmap = topic_pixmap.scaledToWidth(350)
        self._topic_graph_label.setPixmap(topic_pixmap)
        self._topic_graph_label.adjustSize()

    def set_character_active_func(self,name, checkbox):
        def set_character_active():
            is_active = checkbox.isChecked()
            if is_active:
                self._active_characters.append(name)
                self.set_colour_for_character(name, checkbox, len(self._active_characters) - 1)
                self.map_widget.add_active_character(name, self._colour_dict[name][1])
            if not is_active:
                new_active = []
                for character in self._active_characters:
                    if character != name:
                        new_active.append(character)
                self._active_characters = new_active
                self.map_widget.remove_active_character(name)
                self._colour_dict[name] = ["white", QtCore.Qt.white]
                checkbox.setStyleSheet("background-color: "+ self._colour_dict[name][0])
        return set_character_active

    def set_colour_for_character(self, name:str, checkbox, position:int):
        self._colour_dict[name] = [self._available_colours[position % len(self._available_colours)] , self._available_colours_qt[position % len(self._available_colours)]]
        checkbox.setStyleSheet("background-color: "+ self._colour_dict[name][0])

    def update_character_list(self):
        for character in self._character_list:
            character_checkbox = QCheckBox(character)
            character_checkbox.setStyleSheet("background-color: "+ self._colour_dict[character][0])
            character_checkbox.clicked.connect(self.set_character_active_func(character, character_checkbox))
            character_checkbox.setFixedHeight(20)
            if character in self._active_characters:
                character_checkbox.setChecked(True)
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
        location_names = self.get_location_names_for_chapter(current_chapter+1)
        for location_name in location_names:
            #if location_name[0] in self._active_characters:
            #print(location_name[0]+ " going to "+ location_name[1])
            #if not self.map_widget.is_location_on_map(location_name[1]):
           #     print(" is not on map")
            #    continue
            if self._current_position_dict[location_name[0]] == "":
                self._current_position_dict[location_name[0]] = location_name[1]    
            self.map_widget.draw_path_by_location(self._current_position_dict[location_name[0]], location_name[1], self._colour_dict[location_name[0]][1], location_name[0])
            self._current_position_dict[location_name[0]] = location_name[1]
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
        ret = []
        for key in self._location_dict:
            locations = self._location_dict[key]
            for location in locations:
                if location[2] == chapter:
                    ret_entry = [key, location[0][0]]
                    ret.append(ret_entry)
        return ret




if __name__ == "__main__":
    app = QApplication(sys.argv)
    m = MainWindow()
    m.show()
    sys.exit(app.exec())
