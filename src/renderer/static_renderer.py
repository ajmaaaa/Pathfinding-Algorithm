import pygame
import math
from config import C, RIBBON_H, RW, LP

class StaticRenderer:
    def __init__(self, screen, cam):
        self.screen = screen
        self.cam = cam
        self.W = screen.get_width()
        self.H = screen.get_height() - RIBBON_H
        self.show_graph = False

    def _ws(self, wx, wy): 
        return self.cam.world_to_screen(wx, wy)

    def draw_bg(self): 
        pygame.draw.rect(self.screen, C['bg'], (0, RIBBON_H, self.W, self.H))

    def draw_edges_layer(self, edges, color, width, dash=False, hidden_edges=None):
        w = max(1, int(width)); r = max(1, w // 2); drawn_nodes = set()
        for e in edges:
            if hidden_edges and id(e) in hidden_edges: continue
            p1 = self._ws(e[0].x, e[0].y); p2 = self._ws(e[1].x, e[1].y)
            if (max(p1[0],p2[0]) < -r*2 or min(p1[0],p2[0]) > self.W + r*2 or
                max(p1[1],p2[1]) < RIBBON_H - r*2 or min(p1[1],p2[1]) > self.H+RIBBON_H + r*2): continue
            
            if dash:
                total = math.hypot(p2[0]-p1[0], p2[1]-p1[1])
                if total < 2: continue
                dx = (p2[0]-p1[0])/total; dy = (p2[1]-p1[1])/total
                pos = 0; drawing = True; dash_len = max(4, int(RW*0.4*self.cam.zoom))
                while pos < total:
                    seg = dash_len
                    if drawing:
                        x1 = p1[0]+dx*pos; y1 = p1[1]+dy*pos
                        end_p = min(pos+seg, total); x2 = p1[0]+dx*end_p; y2 = p1[1]+dy*end_p
                        pygame.draw.line(self.screen, color, (x1,y1), (x2,y2), w)
                    pos += seg; drawing = not drawing
            else:
                if id(e[0]) not in drawn_nodes: pygame.draw.circle(self.screen, color, p1, r); drawn_nodes.add(id(e[0]))
                if id(e[1]) not in drawn_nodes: pygame.draw.circle(self.screen, color, p2, r); drawn_nodes.add(id(e[1]))
                if p1 != p2:
                    angle = math.atan2(p2[1] - p1[1], p2[0] - p1[0]); dx = r * math.sin(angle); dy = r * -math.cos(angle)
                    p1_a = (p1[0] + dx, p1[1] + dy); p1_b = (p1[0] - dx, p1[1] - dy)
                    p2_a = (p2[0] + dx, p2[1] + dy); p2_b = (p2[0] - dx, p2[1] - dy)
                    pygame.draw.polygon(self.screen, color, [p1_a, p2_a, p2_b, p1_b])

    def draw_map(self, city):
        sc = self.cam.zoom
        edges = city['edges']; rbs = city['roundabouts']; hidden = city.get('hidden_edges', set())
        self.draw_edges_layer(edges, C['grass'], LP*sc, hidden_edges=hidden)
        self.draw_edges_layer(edges, C['road_outer'], RW*1.6*sc, hidden_edges=hidden)
        for rb in rbs:
            sx, sy = self._ws(rb.x, rb.y); ro = int(RW*1.5*sc)
            if ro >= 2: pygame.draw.circle(self.screen, C['road_outer'], (sx,sy), ro + max(1,int(RW*0.2*sc)))
            
        self.draw_edges_layer(edges, C['road_inner'], RW*sc, hidden_edges=hidden)
        for rb in rbs:
            sx, sy = self._ws(rb.x, rb.y); ro = int(RW*1.5*sc); ri = int(RW*0.7*sc)
            if ro >= 2:
                pygame.draw.circle(self.screen, C['road_inner'], (sx,sy), ro)
                pygame.draw.circle(self.screen, C['rb_grass'], (sx,sy), ri)
                pygame.draw.circle(self.screen, C['road_outer'], (sx,sy), ri, max(1,int(3*sc)))
            
        if sc > 0.06: self.draw_edges_layer(edges, C['road_line'], max(1, RW*0.08*sc), dash=True, hidden_edges=hidden)

    def draw_graph(self, nodes, edges):
        sc = self.cam.zoom
        for e in edges:
            p1 = self._ws(e[0].x, e[0].y); p2 = self._ws(e[1].x, e[1].y)
            if (max(p1[0],p2[0]) < 0 or min(p1[0],p2[0]) > self.W or max(p1[1],p2[1]) < RIBBON_H or min(p1[1],p2[1]) > self.H+RIBBON_H): continue
            pygame.draw.line(self.screen, (0, 255, 255), p1, p2, max(1, int(12*sc)))
            
        for n in nodes:
            sx, sy = self._ws(n.x, n.y)
            if sx < 0 or sx > self.W or sy < RIBBON_H or sy > self.H+RIBBON_H: continue
            pygame.draw.circle(self.screen, (255, 42, 42), (sx, sy), max(3, int(16*sc)))
            pygame.draw.circle(self.screen, C['white'], (sx, sy), max(3, int(16*sc)), max(1, int(4*sc)))