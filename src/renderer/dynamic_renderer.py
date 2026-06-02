import pygame
import math
import time
from config import C, RIBBON_H, RW
from src.core.geometry import get_smooth_path_coord, point_on_polyline

class DynamicRenderer:
    def __init__(self, screen, cam):
        self.screen = screen
        self.cam = cam
        self.W = screen.get_width()
        self.H = screen.get_height() - RIBBON_H
        self.car_angle = 0.0
        self.car_smooth_angle = 0.0
        self.car_target_angle = 0.0
        self.car_last_prog = 0.0
        self.car_last_x = None
        self.car_last_y = None
        self._angle_initialized = False

    def _ws(self, wx, wy):
        return self.cam.world_to_screen(wx, wy)
