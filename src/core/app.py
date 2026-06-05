import pygame
import math
import random
from config import SCREEN_W, SCREEN_H, RIBBON_H, FPS, SEARCH_ANIM_SPEED, DRIVE_ANIM_SPEED, get_system_theme, start_theme_check_thread
from src.renderer.camera import Camera
from src.renderer.static_renderer import StaticRenderer
from src.renderer.dynamic_renderer import DynamicRenderer
from src.mapgen.building_renderer import BuildingRenderer
from src.mapgen.else_renderer import ElseRenderer
from src.ui.ribbon import Ribbon, ZoomControls
from src.ui.hud import draw_badge, draw_tooltip, get_font
from src.ui.loading import show_loading_screen
from src.core.city_gen import MapGen
from src.algorithm.pathfinder import run_astar_anim
from src.core.geometry import get_smooth_path_coord, find_closest_road_point, split_curve_at_point
from src.core.graph import Node

class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.RESIZABLE)
        pygame.display.set_caption('Map Pathfinding — Bidirectional A* Visualizer')
        show_loading_screen(self.screen)
        self.clock  = pygame.time.Clock()

        W, H = self.screen.get_size()
        self.ribbon_h = RIBBON_H
        self.cam = Camera(W, H-self.ribbon_h)
        
        self.static_ren = StaticRenderer(self.screen, self.cam)
        self.dynamic_ren = DynamicRenderer(self.screen, self.cam)
        self.building_ren = BuildingRenderer(self.screen, self.cam)
        self.else_ren = ElseRenderer(self.screen, self.cam)
        
        self.ribbon = Ribbon(W)
        self.zoom_c = ZoomControls(W, H)
        self.current_theme = get_system_theme()
        self.theme_timer = 0.0

        self.city        = None; self.mode = None
        self.start_node  = None; self.end_node = None
        self.start_edge  = None; self.end_edge = None
        self.is_playing  = False; self.anim_progress = 0.0; self.total_anim_steps = 0.0
        self.search_edges_anim = []; self.final_path_anim = []
        self.active_nodes = None; self.active_edges = None; self.active_edge_curves = None
        self._pending_dist = 0.0  # jarak rute disimpan sementara
        self._pending_ms   = 0.0  # waktu cari disimpan sementara
        self._total_visited = 0   # total node dikunjungi A*
        self._path_nodes   = []   # daftar node pada jalur final

        self.auto_cam    = 'free' 
        self.dragging    = False; self.drag_last = (0,0)
        self.mouse_pos   = (-1000, -1000); self.hovered_building = None

        self.first_gen   = True
        self.load_or_generate()

    def center_camera_on_island(self, init=False):
        pulau_entity = None
        if self.city and 'entities' in self.city:
            for e in self.city['entities']:
                if e.__class__.__name__ == "Pulau":
                    pulau_entity = e
                    break
        if pulau_entity:
            self.cam.cam_x = pulau_entity.x
            self.cam.cam_y = getattr(pulau_entity, 'render_y', pulau_entity.y)
        else:
            self.cam.cam_x = 2400
            self.cam.cam_y = 2800
        if init:
            self.cam.zoom = 0.8

    def load_or_generate(self):
        self._do_generate()

    def _do_generate(self):
        self.city = show_loading_screen(self.screen, lambda: MapGen().compile_graph())
        self._reset_path()
        self.ribbon.set_disabled(False)
        self.center_camera_on_island(init=self.first_gen)
        self.first_gen = False

    def _clear_search_results(self):
        self.is_playing = False; self.anim_progress = 0.0; self.total_anim_steps = 0.0
        self.search_edges_anim = []; self.final_path_anim = []
        self.active_nodes = None; self.active_edges = None; self.active_edge_curves = None
        self._pending_dist = 0.0; self._pending_ms = 0.0
        self._total_visited = 0; self._path_nodes = []

        if self.city:
            for n in self.city['nodes']: n.eval_step = float('inf'); n.disc_step = float('inf')

        rb = self.ribbon
        rb.btns['play'].icon_name = 'play'; rb.btns['play'].label = 'Mulai'; rb.btns['play'].active = False
        rb.set_stat('Jarak Rute','—'); rb.set_stat('Waktu Cari','—')
        rb.set_stat('Dikunjungi','0'); rb.set_stat('Node Jalur','0'); rb.set_stat('Edge Jalur','0')
        rb.slider.disabled = True; rb.slider.val = 0; rb.slider.max_val = 100
        rb.btn_prev.disabled = True; rb.btn_next.disabled = True

    def _reset_path(self):
        self.start_node = None; self.end_node = None; self.mode = None
        self.start_edge = None; self.end_edge = None
        self.auto_cam = 'free'
        self._clear_search_results()

    def _sync_stats(self):
        if not self.city: return

        # --- Dikunjungi: node yang dievaluasi A* selama fase pencarian ---
        v_count = sum(1 for n in self.city['nodes'] if n.eval_step <= self.anim_progress)
        self.ribbon.set_stat('Dikunjungi', str(v_count))

        # --- Node & Edge Jalur: ikuti posisi mobil di jalur final ---
        # Hitung berapa node path yang sudah dilalui mobil
        # Setiap elemen final_path_anim dari node A ke B mewakili 1 edge
        # Node yang sudah dilewati = jumlah edge selesai + 1 (node awal)
        if self.final_path_anim and self.anim_progress >= self.final_path_anim[0]['start']:
            # Hitung edge jalur yang sudah SELESAI dilewati (pe['end'] <= progress)
            # Khusus: abaikan turn-curve (from == to) karena bukan edge graph asli
            real_edges_done = sum(
                1 for pe in self.final_path_anim
                if pe['from'] is not pe['to'] and self.anim_progress >= pe['end']
            )
            # Edge yang sedang dilalui saat ini
            real_edges_in_progress = sum(
                1 for pe in self.final_path_anim
                if pe['from'] is not pe['to']
                and pe['start'] <= self.anim_progress < pe['end']
            )
            node_count = real_edges_done + 1 if (real_edges_done + real_edges_in_progress) > 0 else 1
            self.ribbon.set_stat('Edge Jalur', str(real_edges_done))
            self.ribbon.set_stat('Node Jalur', str(node_count))
        else:
            self.ribbon.set_stat('Edge Jalur', '0')
            self.ribbon.set_stat('Node Jalur', '0')

        # --- Jarak Rute & Waktu Cari: tampil setelah animasi selesai ---
        if self.anim_progress >= self.total_anim_steps and self.total_anim_steps > 0:
            km = self._pending_dist / 100
            self.ribbon.set_stat('Jarak Rute', f'{km:.1f} km')
            self.ribbon.set_stat('Waktu Cari', f'{self._pending_ms:.2f} ms')
            self.ribbon.set_stat('Dikunjungi', str(self._total_visited))

    def _run_astar(self):
        if not self.start_node or not self.end_node: return
        
        # Simpan state graph asli
        original_nodes = list(self.city['nodes'])
        original_edges = list(self.city['edges'])
        
        modified_nodes_edges = {}
        def backup_node_edges(node):
            if node not in modified_nodes_edges:
                modified_nodes_edges[node] = list(node.edges)
                
        temp_nodes_to_add = []
        temp_edges_to_add = []
        edges_to_remove = []
        
        temp_edge_curves = dict(self.city.get('edge_curves', {}))
        
        # 1. Jika start_node adalah node baru
        if self.start_node not in original_nodes:
            temp_nodes_to_add.append(self.start_node)
            u, v = self.start_edge
            backup_node_edges(u)
            backup_node_edges(v)
            edges_to_remove.append((u, v))
            e1 = (u, self.start_node)
            e2 = (self.start_node, v)
            temp_edges_to_add.extend([e1, e2])
            
            orig_curve = temp_edge_curves.get(id(self.start_edge))
            if not orig_curve:
                orig_curve = [(u.x, u.y), (v.x, v.y)]
            else:
                if math.hypot(orig_curve[0][0] - v.x, orig_curve[0][1] - v.y) < 1.0:
                    orig_curve = list(reversed(orig_curve))
            c1, c2 = split_curve_at_point(orig_curve, (self.start_node.x, self.start_node.y))
            temp_edge_curves[id(e1)] = c1
            temp_edge_curves[id(e2)] = c2
            
        # 2. Jika end_node adalah node baru
        if self.end_node not in original_nodes:
            if self.end_node not in temp_nodes_to_add:
                temp_nodes_to_add.append(self.end_node)
            u, v = self.end_edge
            backup_node_edges(u)
            backup_node_edges(v)
            edges_to_remove.append((u, v))
            e1 = (u, self.end_node)
            e2 = (self.end_node, v)
            temp_edges_to_add.extend([e1, e2])
            
            orig_curve = temp_edge_curves.get(id(self.end_edge))
            if not orig_curve:
                orig_curve = [(u.x, u.y), (v.x, v.y)]
            else:
                if math.hypot(orig_curve[0][0] - v.x, orig_curve[0][1] - v.y) < 1.0:
                    orig_curve = list(reversed(orig_curve))
            c1, c2 = split_curve_at_point(orig_curve, (self.end_node.x, self.end_node.y))
            temp_edge_curves[id(e1)] = c1
            temp_edge_curves[id(e2)] = c2
            
        # Kasus khusus jika start_node dan end_node berada di edge yang sama
        if (self.start_node not in original_nodes and 
            self.end_node not in original_nodes and 
            self.start_edge == self.end_edge):
            u, v = self.start_edge
            dist_start = math.hypot(self.start_node.x - u.x, self.start_node.y - u.y)
            dist_end = math.hypot(self.end_node.x - u.x, self.end_node.y - u.y)
            
            temp_edges_to_add.clear()
            
            if dist_start < dist_end:
                e1 = (u, self.start_node)
                e2 = (self.start_node, self.end_node)
                e3 = (self.end_node, v)
            else:
                e1 = (u, self.end_node)
                e2 = (self.end_node, self.start_node)
                e3 = (self.start_node, v)
                
            temp_edges_to_add.extend([e1, e2, e3])
                
            orig_curve = temp_edge_curves.get(id(self.start_edge))
            if not orig_curve:
                orig_curve = [(u.x, u.y), (v.x, v.y)]
            else:
                if math.hypot(orig_curve[0][0] - v.x, orig_curve[0][1] - v.y) < 1.0:
                    orig_curve = list(reversed(orig_curve))
            if dist_start < dist_end:
                c1, c_rem = split_curve_at_point(orig_curve, (self.start_node.x, self.start_node.y))
                c2, c3 = split_curve_at_point(c_rem, (self.end_node.x, self.end_node.y))
            else:
                c1, c_rem = split_curve_at_point(orig_curve, (self.end_node.x, self.end_node.y))
                c2, c3 = split_curve_at_point(c_rem, (self.start_node.x, self.start_node.y))
            temp_edge_curves[id(e1)] = c1
            temp_edge_curves[id(e2)] = c2
            temp_edge_curves[id(e3)] = c3
                
        # Terapkan perubahan ke graph
        self.city['nodes'].extend(temp_nodes_to_add)
        for e in temp_edges_to_add:
            self.city['edges'].append(e)
            e[0].edges.append(e)
            e[1].edges.append(e)
            
        for u, v in edges_to_remove:
            to_remove_global = [ge for ge in self.city['edges'] if (ge[0] is u and ge[1] is v) or (ge[0] is v and ge[1] is u)]
            for ge in to_remove_global:
                if ge in self.city['edges']:
                    self.city['edges'].remove(ge)
            
            u_to_remove = [le for le in u.edges if (le[0] is u and le[1] is v) or (le[0] is v and le[1] is u)]
            for le in u_to_remove:
                if le in u.edges:
                    u.edges.remove(le)
                    
            v_to_remove = [le for le in v.edges if (le[0] is u and le[1] is v) or (le[0] is v and le[1] is u)]
            for le in v_to_remove:
                if le in v.edges:
                    v.edges.remove(le)
                    
        self.active_nodes = list(self.city['nodes'])
        self.active_edges = list(self.city['edges'])
        self.active_edge_curves = dict(temp_edge_curves)
        
        try:
            se, pe, dist, ms, steps = run_astar_anim(
                self.start_node,
                self.end_node,
                self.city['nodes'],
                temp_edge_curves
            )
        finally:
            # Kembalikan graph asli
            self.city['nodes'] = original_nodes
            self.city['edges'] = original_edges
            for node, orig_edges in modified_nodes_edges.items():
                node.edges = orig_edges
                
        self.search_edges_anim = se; self.final_path_anim = pe; self.total_anim_steps = steps
        # Simpan sementara — akan ditampilkan setelah animasi selesai
        self._pending_dist = dist
        self._pending_ms   = ms
        self._total_visited = sum(1 for n in self.city['nodes'] if n.eval_step < float('inf'))
        # Reset stat ke — hingga animasi selesai
        self.ribbon.set_stat('Jarak Rute', '—'); self.ribbon.set_stat('Waktu Cari', '—')
        self.ribbon.set_stat('Dikunjungi', '0'); self.ribbon.set_stat('Node Jalur', '0'); self.ribbon.set_stat('Edge Jalur', '0')
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
            
            # Poll system theme once every second
            self.theme_timer += dt_ms
            if self.theme_timer >= 1000.0:
                self.theme_timer = 0.0
                start_theme_check_thread()
                self.current_theme = get_system_theme()
                
            self.cam.sw = W; self.cam.sh = H-self.ribbon_h
            
            # Sync sizes to renderers
            self.static_ren.W = W; self.static_ren.H = H-self.ribbon_h
            self.dynamic_ren.W = W; self.dynamic_ren.H = H-self.ribbon_h
            self.building_ren.W = W; self.building_ren.H = H-self.ribbon_h
            
            self.ribbon.W = W; self.zoom_c = ZoomControls(W, H)
            mx, my = pygame.mouse.get_pos(); self.mouse_pos = (mx, my)

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT: running = False
                elif ev.type == pygame.VIDEORESIZE:
                    is_fs = self.screen.get_flags() & pygame.FULLSCREEN
                    if not is_fs:
                        self.screen = pygame.display.set_mode(ev.size, pygame.RESIZABLE)
                    W, H = ev.size
                    self.cam.sw = W
                    self.cam.sh = H - self.ribbon_h
                    self.static_ren.W = W
                    self.static_ren.H = H - self.ribbon_h
                    self.dynamic_ren.W = W
                    self.dynamic_ren.H = H - self.ribbon_h
                    self.building_ren.W = W
                    self.building_ren.H = H - self.ribbon_h
                    self.ribbon.W = W
                    self.zoom_c = ZoomControls(W, H)
                elif ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_e:
                        self._handle_action('edit')
                    elif ev.key == pygame.K_F11:
                        self._toggle_fullscreen()
                elif ev.type == pygame.MOUSEWHEEL:
                    if my > self.ribbon_h:
                        zoom_factor = 1.0 + (ev.y * 0.05); self.cam.do_zoom(zoom_factor); self.auto_cam = 'free' 
                elif ev.type == pygame.MULTIGESTURE:
                    if my > self.ribbon_h:
                        zoom_factor = 1.0 + (ev.dists * 2.5); self.cam.do_zoom(zoom_factor); self.auto_cam = 'free'
                elif ev.type == pygame.MOUSEBUTTONDOWN:
                    if ev.button == 1:
                        toggle_r = self.ribbon.get_toggle_rect()
                        if toggle_r.collidepoint(mx, my):
                            self.ribbon.visible = not self.ribbon.visible
                            self.ribbon_h = RIBBON_H if self.ribbon.visible else 0
                            self.cam.ribbon_h = self.ribbon_h
                            self.cam.sh = H - self.ribbon_h
                            self.static_ren.H = H - self.ribbon_h
                            self.dynamic_ren.H = H - self.ribbon_h
                            self.building_ren.H = H - self.ribbon_h
                        elif my <= self.ribbon_h:
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
                                 best_pt, best_edge = find_closest_road_point(wx, wy, self.city['edges'], self.city.get('edge_curves', {}))
                                 if best_pt:
                                     u, v = best_edge
                                     dist_u = math.hypot(best_pt[0] - u.x, best_pt[1] - u.y)
                                     dist_v = math.hypot(best_pt[0] - v.x, best_pt[1] - v.y)
                                     if dist_u < 1e-3:
                                         n = u
                                         edge = None
                                     elif dist_v < 1e-3:
                                         n = v
                                         edge = None
                                     else:
                                         n = Node(best_pt[0], best_pt[1])
                                         edge = best_edge
                                     self._clear_search_results()
                                     if self.mode == 'start':
                                         self.start_node = n
                                         self.start_edge = edge
                                     else:
                                         self.end_node = n
                                         self.end_edge = edge
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
                    elif self.dragging and my > self.ribbon_h:
                        dx = mx - self.drag_last[0]; dy = my - self.drag_last[1]; self.cam.pan(dx, dy); self.drag_last = (mx, my)

            if self.is_playing:
                old_prog = self.anim_progress
                # Gunakan SEARCH_ANIM_SPEED jika masih mencari rute, DRIVE_ANIM_SPEED jika mobil berjalan
                is_searching = True
                if self.final_path_anim:
                    car_start = self.final_path_anim[0]['start']
                    if self.anim_progress >= car_start:
                        is_searching = False
                
                speed = SEARCH_ANIM_SPEED if is_searching else DRIVE_ANIM_SPEED
                self.anim_progress += dt_ms * speed
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
                        target_zoom = 0.95 
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
            if not self.dragging and my > self.ribbon_h and self.city:
                wx, wy = self.cam.screen_to_world(mx, my)
                for b in reversed(self.city['buildings']):
                    if b['type'].lower().startswith('kavling'):
                        continue
                    dist_sq = (b['x'] - wx)**2 + (b['y'] - wy)**2
                    if dist_sq < (90 * b['scale'])**2: self.hovered_building = b; break

            self.ribbon.update(mx, my)
            self.static_ren.draw_bg()
            
            if self.city:
                self.static_ren.draw_map(self.city)
                


                if self.static_ren.show_graph:
                    nodes_to_draw = self.active_nodes if self.active_nodes is not None else self.city['nodes']
                    edges_to_draw = self.active_edges if self.active_edges is not None else self.city['edges']
                    curves_to_draw = self.active_edge_curves if self.active_edge_curves is not None else self.city.get('edge_curves', {})
                    self.static_ren.draw_graph(nodes_to_draw, edges_to_draw, curves_to_draw)
                
                if self.total_anim_steps > 0 or len(self.search_edges_anim) > 0:
                    self.dynamic_ren.draw_anim_layer_ground(self.city['nodes'], self.search_edges_anim, self.final_path_anim, self.anim_progress, self.city.get('edge_curves', {}))
                
                car_x, car_y, car_angle = None, None, None
                if self.final_path_anim and self.anim_progress > 0:
                    car_x, car_y, car_angle = self.dynamic_ren.get_car_transform(self.final_path_anim, self.anim_progress)
                
                # PASS 1: Render semua kavling (alas tanah) terlebih dahulu
                for b in self.city['buildings']:
                    if b['type'].lower().startswith('kavling'):
                        self.building_ren.draw_building(b)
                
                # PASS 2: Render mobil dan semua bangunan vertikal lainnya
                car_drawn = False
                for b in self.city['buildings']:
                    if b['type'].lower().startswith('kavling'):
                        continue
                    if car_x is not None and not car_drawn and car_y < b.get('sort_y', b['y']):
                        self.dynamic_ren.draw_car(car_x, car_y, car_angle)
                        car_drawn = True
                    self.building_ren.draw_building(b)
                
                if car_x is not None and not car_drawn:
                    self.dynamic_ren.draw_car(car_x, car_y, car_angle)
                
                if self.start_node: self.else_ren.draw_pin(self.start_node, (34, 197, 94), 'S')
                if self.end_node: self.else_ren.draw_pin(self.end_node, (239, 68, 68), 'E')
                if self.hovered_building: draw_tooltip(self.screen, self.hovered_building['name'], mx, my)

            self.ribbon.draw(self.screen, theme=self.current_theme); self.zoom_c.draw(self.screen, self.cam.zoom, theme=self.current_theme)
            if self.mode == 'start': draw_badge(self.screen, '📍 Mode SET START — klik titik pada peta', W, self.ribbon_h)
            elif self.mode == 'end': draw_badge(self.screen, '🏁 Mode SET END — klik titik pada peta', W, self.ribbon_h)

            pygame.display.flip()
        pygame.quit()

    def _handle_action(self, action):
        if action == 'gen': self._do_generate()
        elif action == 'acak':
            if self.city:
                valid_nodes = [n for n in self.city['nodes'] if not getattr(n, 'is_roundabout', False)]
                if len(valid_nodes) > 1:
                    self._reset_path()
                    a, b = random.sample(valid_nodes, 2)
                    self.start_node = a
                    self.end_node = b
                    self.auto_cam = 'free'
        elif action == 'start': self.mode = 'start' if self.mode != 'start' else None
        elif action == 'end': self.mode = 'end' if self.mode != 'end' else None
        elif action == 'edit': pass
        elif action == 'play': self._toggle_play()
        elif action == 'reset': self._reset_path()
        elif action == 'prev': self._step_anim(-1)
        elif action == 'next': self._step_anim(1)
        elif action == 'graph':
            self.static_ren.show_graph = not self.static_ren.show_graph
            self.ribbon.btns['graph'].active = self.static_ren.show_graph

    def _toggle_fullscreen(self):
        pygame.display.toggle_fullscreen()
        W, H = self.screen.get_size()
        self.cam.sw = W
        self.cam.sh = H - self.ribbon_h
        self.static_ren.W = W
        self.static_ren.H = H - self.ribbon_h
        self.dynamic_ren.W = W
        self.dynamic_ren.H = H - self.ribbon_h
        self.building_ren.W = W
        self.building_ren.H = H - self.ribbon_h
        self.ribbon.W = W
        self.zoom_c = ZoomControls(W, H)
