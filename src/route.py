from PyQt5.QtCore import QTimeLine, Qt
from PyQt5.QtGui import QPainter

class Route:
    def __init__(self):
        self._start_point = [0,0]
        self._end_point = [0,0]
        self._colour = Qt.red

    def set_colour(self,col):
        self._colour = col
    def get_colour(self):
        return self._colour

    def set_route(self,start_point, end_point, number_of_steps):
        self._start_point = start_point
        self._end_point = end_point
        self._number_of_steps = number_of_steps
        self._step_vec = [ (end_point[0] - start_point[0]) / number_of_steps, (end_point[1] - start_point[1]) / number_of_steps]


    def get_line_at_frame(self, frame_number):
        if (frame_number == self._number_of_steps):
            return (self._start_point,self._end_point)
        start_p_x = self._start_point[0] + frame_number * self._step_vec[0]
        start_p_y = self._start_point[1] + frame_number * self._step_vec[1]
        end_p_x = self._start_point[0] + (frame_number+1) * self._step_vec[0]
        end_p_y = self._start_point[1] + (frame_number+1) * self._step_vec[1]
        return ([start_p_x,start_p_y],[end_p_x,end_p_y])

    def get_end_point(self):
        return self._end_point
        

        