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
    
    def _curve_until(self, curve, p):
        if not curve:
            return []
        p = max(0.0, min(1.0, p))
        if p <= 0:
            return [curve[0]]
        if p >= 1.0:
            return curve[:]
            
        total_len = 0.0
        for i in range(1, len(curve)):
            p0 = curve[i - 1]
            p1 = curve[i]
            total_len += math.hypot(p1[0] - p0[0], p1[1] - p0[1])
            
        target = total_len * p
        walked = 0.0
        pts = [curve[0]]
        
        for i in range(1, len(curve)):
            p0 = curve[i - 1]
            p1 = curve[i]
            seg = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
            if walked + seg >= target:
                local_t = (target - walked) / max(0.0001, seg)
                end = (
                    p0[0] + (p1[0] - p0[0]) * local_t,
                    p0[1] + (p1[1] - p0[1]) * local_t
                )
                if end != pts[-1]:
                    pts.append(end)
                break
            else:
                if p1 != pts[-1]:
                    pts.append(p1)
                walked += seg
                
        return pts    
