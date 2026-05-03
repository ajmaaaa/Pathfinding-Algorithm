import pygame
import math
import random
from config import SCREEN_W, SCREEN_H, RIBBON_H, FPS, ANIM_SPEED
from src.renderer.camera import Camera
from src.renderer.static_renderer import StaticRenderer
from src.renderer.dynamic_renderer import DynamicRenderer
from src.mapgen.building_renderer import BuildingRenderer
from src.mapgen.else_renderer import ElseRenderer
from src.ui.ribbon import Ribbon, ZoomControls
from src.ui.hud import draw_badge, draw_tooltip
from src.ui.loading import show_loading_screen
from src.core.city_gen import MapGen
from src.algorithm.pathfinder import run_astar_anim
from src.core.geometry import get_smooth_path_coord

class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.RESIZABLE)
        pygame.display.set_caption('Map Pathfinding — A* Visualizer')
        self.clock  = pygame.time.Clock()

        W, H = self.screen.get_size()
        self.cam = Camera(W, H-RIBBON_H)
        
        self.static_ren = StaticRenderer(self.screen, self.cam)
        self.dynamic_ren = DynamicRenderer(self.screen, self.cam)
        self.building_ren = BuildingRenderer(self.screen, self.cam)
        self.else_ren = ElseRenderer(self.screen, self.cam)
        
        self.ribbon = Ribbon(W)
        self.zoom_c = ZoomControls(W, H)

        self.city        = None; self.mode = None
        self.start_node  = None; self.end_node = None
        self.is_playing  = False; self.anim_progress = 0.0; self.total_anim_steps = 0.0
        self.search_edges_anim = []; self.final_path_anim = []
        
        self.auto_cam    = 'free' 
        self.dragging    = False; self.drag_last = (0,0)
        self.mouse_pos   = (-1000, -1000); self.hovered_building = None

        self._do_generate()

    def _do_generate(self):
        show_loading_screen(self.screen)
        gen = MapGen()
        self.city = gen.generate()
        self.else_ren.generate_decorations(self.city)  # ---- ini tambahan auriel ---
        self._reset_path()
        self.ribbon.set_disabled(False)
        self.cam.cam_x = 0; self.cam.cam_y = 0

    def _reset_path(self):
        self.start_node = None; self.end_node = None; self.mode = None
        self.is_playing = False; self.anim_progress = 0.0; self.total_anim_steps = 0.0
        self.search_edges_anim = []; self.final_path_anim = []; self.auto_cam = 'free'
        
        if self.city:
            for n in self.city['nodes']: n.eval_step = float('inf'); n.disc_step = float('inf')

        rb = self.ribbon
        rb.btns['play'].icon_name = 'play'; rb.btns['play'].label = 'Mulai'; rb.btns['play'].active = False
        rb.set_stat('Jarak Rute','—'); rb.set_stat('Waktu Cari','—')
        rb.set_stat('Dikunjungi','0'); rb.set_stat('Node Jalur','0'); rb.set_stat('Edge Jalur','0')
        rb.slider.disabled = True; rb.slider.val = 0; rb.slider.max_val = 100
        rb.btn_prev.disabled = True; rb.btn_next.disabled = True

    def _sync_stats(self):
        if not self.city: return
        v_count = sum(1 for n in self.city['nodes'] if n.eval_step <= self.anim_progress)
        e_count = sum(1 for e in self.final_path_anim if self.anim_progress >= e['end'])
        self.ribbon.set_stat('Dikunjungi', str(v_count)); self.ribbon.set_stat('Edge Jalur', str(e_count))
        self.ribbon.set_stat('Node Jalur', str(e_count + 1) if e_count > 0 else '0')

    def _run_astar(self):
        if not self.start_node or not self.end_node: return
        se, pe, dist, ms, steps = run_astar_anim(self.start_node, self.end_node, self.city['nodes'])
        self.search_edges_anim = se; self.final_path_anim = pe; self.total_anim_steps = steps
        km = dist/100
        self.ribbon.set_stat('Waktu Cari', f'{ms:.2f} ms'); self.ribbon.set_stat('Jarak Rute', f'{km:.1f} km')
        self.ribbon.slider.max_val = steps; self.ribbon.slider.disabled = False
        self.ribbon.btn_prev.disabled = False; self.ribbon.btn_next.disabled = False
        self.anim_progress = 0.0; self.is_playing = True; self.auto_cam = 'follow'
        self._update_play_ui()

    def _update_play_ui(self):
        b = self.ribbon.btns['play']
        b.icon_name = 'pause' if self.is_playing else 'play'
        b.label = 'Pause' if self.is_playing else 'Lanjut'
        b.active = self.is_playing

    def _toggle_play(self):
        if not self.start_node or not self.end_node: self._handle_action('acak')
        if self.is_playing: self.is_playing = False
        else:
            if self.total_anim_steps == 0: self._run_astar()
            elif self.anim_progress < self.total_anim_steps: self.is_playing = True; self.auto_cam = 'follow'
        self._update_play_ui()

    def _step_anim(self, dir_val):
        self.is_playing = False; self._update_play_ui()
        target = round(self.anim_progress) + dir_val
        self.anim_progress = max(0.0, min(self.total_anim_steps, float(target)))
        self.ribbon.slider.val = self.anim_progress; self._sync_stats()

    def run(self):
        running = True
        while running:
            dt_ms = self.clock.tick(FPS); W, H = self.screen.get_size()
            if W <= 0 or H <= 0: pygame.event.pump(); continue
                
            self.cam.sw = W; self.cam.sh = H-RIBBON_H
            
            # Sync sizes to renderers
            self.static_ren.W = W; self.static_ren.H = H-RIBBON_H
            self.dynamic_ren.W = W; self.dynamic_ren.H = H-RIBBON_H
            self.building_ren.W = W; self.building_ren.H = H-RIBBON_H
            
            self.ribbon.W = W; self.zoom_c = ZoomControls(W, H)
            mx, my = pygame.mouse.get_pos(); self.mouse_pos = (mx, my)

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT: running = False
                elif ev.type == pygame.VIDEORESIZE: self.screen = pygame.display.set_mode(ev.size, pygame.RESIZABLE)
                elif ev.type == pygame.MOUSEWHEEL:
                    if my > RIBBON_H:
                        zoom_factor = 1.0 + (ev.y * 0.05); self.cam.do_zoom(zoom_factor); self.auto_cam = 'free' 
                elif ev.type == pygame.MULTIGESTURE:
                    if my > RIBBON_H:
                        zoom_factor = 1.0 + (ev.dists * 2.5); self.cam.do_zoom(zoom_factor); self.auto_cam = 'free'
                elif ev.type == pygame.MOUSEBUTTONDOWN:
                    if ev.button == 1:
                        if my <= RIBBON_H:
                            if self.ribbon.slider.handle_mouse(mx, my, 'down'): self.is_playing = False; self._update_play_ui()
                            else:
                                action = self.ribbon.check_click(mx, my)
                                if action: self._handle_action(action)
                        else:
                            zc = self.zoom_c.click(mx, my)
                            if zc == 'in': self.cam.do_zoom(1.3); self.auto_cam = 'free'
                            elif zc == 'out': self.cam.do_zoom(0.77); self.auto_cam = 'free'
                            elif self.mode and self.city:
                                wx, wy = self.cam.screen_to_world(mx, my)
                                n = min(self.city['nodes'], key=lambda nd: (nd.x-wx)**2+(nd.y-wy)**2)
                                if self.mode == 'start': self.start_node = n
                                else: self.end_node = n
                                self.mode = None
                            else: self.dragging = True; self.drag_last = (mx, my); self.auto_cam = 'free' 
                elif ev.type == pygame.MOUSEBUTTONUP:
                    if ev.button == 1:
                        self.dragging = False
                        if self.ribbon.slider.dragging:
                            self.ribbon.slider.handle_mouse(mx, my, 'up'); self.anim_progress = self.ribbon.slider.val; self._sync_stats()
                elif ev.type == pygame.MOUSEMOTION:
                    if self.ribbon.slider.dragging:
                        self.ribbon.slider.handle_mouse(mx, my, 'move'); self.anim_progress = self.ribbon.slider.val; self._sync_stats()
                    elif self.dragging and my > RIBBON_H:
                        dx = mx - self.drag_last[0]; dy = my - self.drag_last[1]; self.cam.pan(dx, dy); self.drag_last = (mx, my)

            if self.is_playing:
                old_prog = self.anim_progress
                self.anim_progress += dt_ms * ANIM_SPEED
                if self.final_path_anim:
                    car_start = self.final_path_anim[0]['start']
                    if old_prog < car_start and self.anim_progress >= car_start: self.auto_cam = 'follow'

                if self.anim_progress >= self.total_anim_steps:
                    self.anim_progress = self.total_anim_steps; self.is_playing = False
                    self.ribbon.btns['play'].label = 'Selesai'; self.ribbon.btns['play'].icon_name = 'play'
                    self._update_play_ui(); self.auto_cam = 'overview' 
                self.ribbon.slider.val = self.anim_progress; self._sync_stats()
                
            if self.auto_cam == 'follow' and self.final_path_anim:
                car_start_time = self.final_path_anim[0]['start']
                if self.anim_progress >= car_start_time:
                    cx, cy = get_smooth_path_coord(self.final_path_anim, self.anim_progress)
                    if cx is not None:
                        target_zoom = 2.5 
                        self.cam.zoom += (target_zoom - self.cam.zoom) * 0.08
                        self.cam.cam_x += (cx - self.cam.cam_x) * 0.25
                        self.cam.cam_y += (cy - self.cam.cam_y) * 0.25
            elif self.auto_cam == 'overview' and self.start_node and self.end_node:
                dx = abs(self.end_node.x - self.start_node.x) + 1600; dy = abs(self.end_node.y - self.start_node.y) + 1200
                target_zoom = min(1.0, self.cam.sw / max(1, dx), self.cam.sh / max(1, dy))
                target_zoom = max(self.cam.MIN, min(self.cam.MAX, target_zoom))
                cx = (self.start_node.x + self.end_node.x) / 2; cy = (self.start_node.y + self.end_node.y) / 2
                self.cam.zoom += (target_zoom - self.cam.zoom) * 0.15 
                self.cam.cam_x += (cx - self.cam.cam_x) * 0.15; self.cam.cam_y += (cy - self.cam.cam_y) * 0.15
                if abs(self.cam.zoom - target_zoom) < 0.01 and math.hypot(cx - self.cam.cam_x, cy - self.cam.cam_y) < 20: self.auto_cam = 'free'

            self.hovered_building = None
            if not self.dragging and my > RIBBON_H and self.city:
                wx, wy = self.cam.screen_to_world(mx, my)
                for b in reversed(self.city['buildings']):
                    dist_sq = (b['x'] - wx)**2 + (b['y'] - wy)**2
                    if dist_sq < (90 * b['scale'])**2: self.hovered_building = b; break

            self.ribbon.update(mx, my)
            self.static_ren.draw_bg()
            
            if self.city:
                self.static_ren.draw_map(self.city)
                if self.static_ren.show_graph: self.static_ren.draw_graph(self.city['nodes'], self.city['edges'])
                
                if self.total_anim_steps > 0 or len(self.search_edges_anim) > 0:
                    self.dynamic_ren.draw_anim_layer_ground(self.city['nodes'], self.search_edges_anim, self.final_path_anim, self.anim_progress)

                self.else_ren.draw_decorations()  # --- ini tambahan auriel ---    
                
                car_x, car_y, car_angle = None, None, None
                if self.final_path_anim and self.anim_progress > 0:
                    car_x, car_y, car_angle = self.dynamic_ren.get_car_transform(self.final_path_anim, self.anim_progress)
                
                car_drawn = False
                for b in self.city['buildings']:
                    if car_x is not None and not car_drawn and car_y < b['y']:
                        self.dynamic_ren.draw_car(car_x, car_y, car_angle)
                        car_drawn = True
                    self.building_ren.draw_building(b)
                
                if car_x is not None and not car_drawn:
                    self.dynamic_ren.draw_car(car_x, car_y, car_angle)
                
                if self.start_node: self.else_ren.draw_pin(self.start_node, (34, 197, 94), 'S')
                if self.end_node: self.else_ren.draw_pin(self.end_node, (239, 68, 68), 'E')
                if self.hovered_building: draw_tooltip(self.screen, self.hovered_building['name'], mx, my)

            self.ribbon.draw(self.screen); self.zoom_c.draw(self.screen, self.cam.zoom)
            if self.mode == 'start': draw_badge(self.screen, '📍 Mode SET START — klik titik pada peta', W)
            elif self.mode == 'end': draw_badge(self.screen, '🏁 Mode SET END — klik titik pada peta', W)

            pygame.display.flip()
        pygame.quit()

    def _handle_action(self, action):
        if action == 'gen': self._do_generate()
        elif action == 'acak':
            if self.city and len(self.city['nodes']) > 1:
                self._reset_path(); a, b = random.sample(self.city['nodes'], 2); self.start_node = a; self.end_node = b; self.auto_cam = 'free'
        elif action == 'start': self.mode = 'start' if self.mode != 'start' else None
        elif action == 'end': self.mode = 'end' if self.mode != 'end' else None
        elif action == 'play': self._toggle_play()
        elif action == 'reset': self._reset_path()
        elif action == 'prev': self._step_anim(-1)
        elif action == 'next': self._step_anim(1)
        elif action == 'graph':
            self.static_ren.show_graph = not self.static_ren.show_graph
            self.ribbon.btns['graph'].active = self.static_ren.show_graph