import pygame
import math
from assets.components.terrain import TerrainSystem

class DummyEntity:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Pulau:
    viewport_offset = (0, 0)
    
    def __init__(self, x, y, rad_c=800, rad_r=400):
        self.x = x
        self.render_y = y
        self.y = y - 6000
        self.rad_c = rad_c
        self.rad_r = rad_r
        self.selected = False
        self.active_handle = None
        self.ts = TerrainSystem()
        self.regenerate()
        
    def regenerate(self):
        r_c = max(250, self.rad_c)
        target_val = max(50, r_c - 400)
        dummys = [
            DummyEntity(self.x - target_val, self.render_y),
            DummyEntity(self.x + target_val, self.render_y)
        ]
        self.ts.generate_island(dummys)
        
    def render(self, screen, offset_x=0, offset_y=0, camera_x=0, camera_y=0, zoom=1.0):
        self.ts.render(screen, offset_x, offset_y, camera_x, camera_y, zoom)
        
    def resize_with_mouse(self, mouse_pos):
        if not self.active_handle:
            return
        cx, cy = self.x, self.render_y
        dx = mouse_pos[0] - cx
        dy = mouse_pos[1] - cy
        
        if self.active_handle == 'right':
            self.rad_c = max(250, int(dx))
        elif self.active_handle == 'left':
            self.rad_c = max(250, int(-dx))
        elif self.active_handle == 'bottom':
            self.rad_r = max(125, int(dy))
            self.rad_c = self.rad_r * 2
        elif self.active_handle == 'top':
            self.rad_r = max(125, int(-dy))
            self.rad_c = self.rad_r * 2
            
        self.rad_r = int(self.rad_c * 0.5)
        self.regenerate()
        
    def check_handle_click(self, mouse_pos, camera_x, camera_y, zoom, offset_x, offset_y):
        cx, cy = self.x, self.render_y
        rad_r = self.rad_c * 0.5
        p_top = (cx, cy - rad_r)
        p_right = (cx + self.rad_c, cy)
        p_bot = (cx, cy + rad_r)
        p_left = (cx - self.rad_c, cy)
        
        handles = {'top': p_top, 'right': p_right, 'bottom': p_bot, 'left': p_left}
        for name, pt in handles.items():
            scr_x = (pt[0] - camera_x) * zoom + offset_x
            scr_y = (pt[1] - camera_y) * zoom + offset_y
            if math.hypot(mouse_pos[0] - scr_x, mouse_pos[1] - scr_y) <= 20:
                return name
        return None
        
    def is_point_inside(self, pt):
        rx = self.rad_c
        ry = self.rad_c * 0.5
        if rx == 0 or ry == 0:
            return False
        return ((pt[0] - self.x) / rx)**2 + ((pt[1] - self.render_y) / ry)**2 <= 1.0

    def get_corners(self):
        cx, cy = self.x, self.render_y
        rad_r = self.rad_c * 0.5
        p_top = (cx, cy - rad_r)
        p_right = (cx + self.rad_c, cy)
        p_bot = (cx, cy + rad_r)
        p_left = (cx - self.rad_c, cy)
        return p_top, p_right, p_bot, p_left
