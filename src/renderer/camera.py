from config import RIBBON_H

class Camera:
    def __init__(self, sw, sh):
        self.sw = sw; self.sh = sh
        self.cam_x = 0.0; self.cam_y = 0.0
        self.zoom  = 0.8
        self.MIN   = 0.07; self.MAX = 6.0

    def do_zoom(self, f): 
        self.zoom = max(self.MIN, min(self.MAX, self.zoom*f))

    def world_to_screen(self, wx, wy):
        sx = (wx - self.cam_x)*self.zoom + self.sw/2
        sy = (wy - self.cam_y)*self.zoom + self.sh/2 + RIBBON_H
        return sx, sy

    def screen_to_world(self, sx, sy):
        wx = (sx - self.sw/2)/self.zoom + self.cam_x
        wy = (sy - self.sh/2 - RIBBON_H)/self.zoom + self.cam_y
        return wx, wy

    def pan(self, dx, dy):
        self.cam_x -= dx/self.zoom; self.cam_y -= dy/self.zoom