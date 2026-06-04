"""
city_gen.py — Procedural island city generator (Phase 2 - Full Procedural Zoning).

Replaces the old template-copy approach with a fully procedural pipeline:
  1. Road skeleton   – one connected graph built from diagonal iso-axes.
  2. Zoning System   – geometric division into CBD, RESIDENTIAL, PARK, etc.
  3. Connector roads – short stubs added from each platform edge to the skeleton.
  4. Validation      – connectivity check + green/road ratio guard.
  5. Trees & sea     – zone-aware tree scatter and decorative sea objects.
"""

import math
import random
from enum import Enum

from src.mapgen.building_placer import get_building_radius
from assets.components import (
    Pulau, RoadSegment, Roundabout, RoadCorner90, BasePlatform,
    BalaiKota, Bandara, Stadion, Gedung,
    GedungA, GedungB, GedungC, GedungD, Apartemen,
    RumahA, RumahB, RumahC, RumahD,
    Sekolah, RumahSakit, Museum, Masjid, Pemadam, KantorPolisi,
    PusatPerbelanjaan, Bank, SPBU, Minimarket, Danau, Taman, Bianglala,
    PohonBulat, PohonPinus,
    Pelabuhan, Mercusuar, KapalKargo, KapalLayar, Hiu, Lampu,
    grid_to_screen, screen_to_grid,

)

# ──────────────────────────────────────────────────────────────────────────────
# Constants & Enums
# ──────────────────────────────────────────────────────────────────────────────

ISO_X = 200.0          # screen px per grid-column unit
ISO_Y = 100.0          # screen px per grid-row unit
ROAD_HALF_WIDTH = 80.0 # half the road body width in px (adjusted to match actual rendered road border shadow width)

TREE_TARGET_RANGE = (28, 48)
LIGHT_TARGET_RANGE = (8, 14)

class ZoneType(Enum):
    CBD = 1
    RESIDENTIAL = 2
    INDUSTRIAL = 3
    PARK = 4
    PUBLIC = 5
    PORT = 6

# Component footprint and anchor metadata
COMPONENT_META = {
    "Bandara":           {"w": 2112, "h": 1056, "ax": 0.0, "ay": 0.0},
    "SPBU":              {"w": 260, "h": 200, "ax": 0.0, "ay": 0.0},
    "BalaiKota":         {"w": 1664, "h": 832, "ax": 0.0, "ay": 0.0},
    "Sekolah":           {"w": 1152, "h": 576, "ax": 0.0, "ay": 0.0},
    "Danau":             {"w": 832, "h": 416, "ax": 0.0, "ay": 0.0},
    "Museum":            {"w": 1144, "h": 572, "ax": 0.0, "ay": 0.0},
    "Bianglala":         {"w": 1500, "h": 800, "ax": 0.0, "ay": 0.0},
    "Taman":             {"w": 190, "h": 160, "ax": 0.0, "ay": 0.0},
    "Masjid":            {"w": 576, "h": 288, "ax": 0.0, "ay": 0.0},
    "PusatPerbelanjaan": {"w": 864, "h": 590, "ax": 0.0, "ay": 0.0},
    "Minimarket":        {"w": 250, "h": 190, "ax": 0.0, "ay": 0.0},
    "KantorPolisi":      {"w": 260, "h": 150, "ax": 0.0, "ay": 0.0},
    "Pemadam":           {"w": 220, "h": 180, "ax": 0.0, "ay": 0.0},
    "Bank":              {"w": 280, "h": 150, "ax": 0.0, "ay": 0.0},
    "Stadion":           {"w": 1000, "h": 800, "ax": 0.0, "ay": 0.0},
    "RumahSakit":        {"w": 560, "h": 580, "ax": 0.0, "ay": 0.0},
    "Pelabuhan":         {"w": 260, "h": 210, "ax": 0.0, "ay": 0.0},
    "Gedung":            {"w": 150, "h": 130, "ax": 0.0, "ay": 0.0},
    "GedungA":           {"w": 150, "h": 130, "ax": 0.0, "ay": 0.0},
    "GedungB":           {"w": 150, "h": 130, "ax": 0.0, "ay": 0.0},
    "GedungC":           {"w": 150, "h": 130, "ax": 0.0, "ay": 0.0},
    "GedungD":           {"w": 150, "h": 130, "ax": 0.0, "ay": 0.0},
    "Apartemen":         {"w": 150, "h": 130, "ax": 0.0, "ay": 0.0},
    "RumahA":            {"w": 80, "h": 70, "ax": 0.0, "ay": 0.0},
    "RumahB":            {"w": 80, "h": 70, "ax": 0.0, "ay": 0.0},
    "RumahC":            {"w": 80, "h": 70, "ax": 0.0, "ay": 0.0},
    "RumahD":            {"w": 80, "h": 70, "ax": 0.0, "ay": 0.0},
    "PohonBulat":        {"w": 60, "h": 80, "ax": 0.0, "ay": 0.0},
    "PohonPinus":        {"w": 50, "h": 80, "ax": 0.0, "ay": 0.0},
}

CLASS_MAP = {
    "RumahA": RumahA, "RumahB": RumahB, "RumahC": RumahC, "RumahD": RumahD,
    "Gedung": Gedung, "GedungA": GedungA, "GedungB": GedungB,
    "GedungC": GedungC, "GedungD": GedungD, "Apartemen": Apartemen,
    "BalaiKota": BalaiKota, "Sekolah": Sekolah, "Museum": Museum,
    "Masjid": Masjid, "RumahSakit": RumahSakit, "Stadion": Stadion,
    "PusatPerbelanjaan": PusatPerbelanjaan, "Minimarket": Minimarket,
    "Bank": Bank, "SPBU": SPBU, "KantorPolisi": KantorPolisi,
    "Pemadam": Pemadam, "Bandara": Bandara, "Pelabuhan": Pelabuhan,
    "Mercusuar": Mercusuar, "Lampu": Lampu, "KapalKargo": KapalKargo,
    "KapalLayar": KapalLayar, "Taman": Taman, "Danau": Danau,
    "Bianglala": Bianglala, "PohonBulat": PohonBulat, "PohonPinus": PohonPinus,
    "Hiu": Hiu,
}

# ──────────────────────────────────────────────────────────────────────────────
# Geometry helpers
# ──────────────────────────────────────────────────────────────────────────────

def _dist_pt_seg(px, py, ax, ay, bx, by):
    l2 = (bx - ax) ** 2 + (by - ay) ** 2
    if l2 <= 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * (bx - ax) + (py - ay) * (by - ay)) / l2))
    return math.hypot(px - ax - t * (bx - ax), py - ay - t * (by - ay))

def _entity_anchor(entity):
    return entity.x, getattr(entity, "render_y", entity.y)

# ──────────────────────────────────────────────────────────────────────────────
# Main generator
# ──────────────────────────────────────────────────────────────────────────────
class BSPNode:
    def __init__(self, ca, ra, cb, rb):
        self.ca, self.ra = ca, ra
        self.cb, self.rb = cb, rb
        self.left = None
        self.right = None
        self.split_dir = None
        self.split_val = None


class MapGen:
    def __init__(self, seed=None):
        self.rng = random.Random(seed)

    def generate(self):
        for attempt in range(15):
            self.entities   = []
            self.platforms  = []   
            self.roads      = []   
            self.land_ents  = []   
            self.occupied   = []   
            self._road_segs = []   
            self.intersections = []

            self._randomise_layout()
            
            self.num_large_unsplit = 0
            self.num_medium_unsplit = 0
            
            # 1. Procedural BSP split
            root = BSPNode(self.c_min + 1.0, self.r_min + 1.0, self.c_max - 1.0, self.r_max - 1.0)
            self.root = root
            leaves = self._bsp_split(root, depth=0)
            
            # Prune outer/corner leaves to make the overall city shape non-rectangular (stepped/bumpy)
            if len(leaves) > 26:
                c_min_val = min(l.ca for l in leaves)
                c_max_val = max(l.cb for l in leaves)
                r_min_val = min(l.ra for l in leaves)
                r_max_val = max(l.rb for l in leaves)
                c_span = c_max_val - c_min_val
                r_span = r_max_val - r_min_val
                
                candidates = []
                for leaf in leaves:
                    c_center = (leaf.ca + leaf.cb) / 2.0
                    r_center = (leaf.ra + leaf.rb) / 2.0
                    nc = (c_center - (c_min_val + c_max_val) / 2.0) / (c_span / 2.0 if c_span > 0 else 1.0)
                    nr = (r_center - (r_min_val + r_max_val) / 2.0) / (r_span / 2.0 if r_span > 0 else 1.0)
                    
                    # Score represents how close to the outer corners/edges the block is, with some organic noise.
                    score = abs(nc) + abs(nr) + self.rng.uniform(-0.15, 0.15)
                    candidates.append((score, leaf))
                
                candidates.sort(key=lambda x: x[0], reverse=True)
                max_prune = len(leaves) - 26
                num_to_prune = min(max_prune, int(len(leaves) * 0.20))
                if num_to_prune > 0:
                    pruned_leaves = set(leaf for score, leaf in candidates[:num_to_prune])
                    leaves = [l for l in leaves if l not in pruned_leaves]
            
            # Assign district roles and adjust boundaries before drawing roads
            if not self._assign_and_adjust_leaves(leaves):
                continue
            
            # 2. Roads first, so every later component can avoid them.
            self._draw_active_leaf_roads(leaves)
            self._place_roundabouts()
            self._place_corners_and_snap()

            # 3. Fill districts after the road network is known.
            self.leaves = leaves
            self._populate_districts(leaves)
            
            # 4. Generate Coastal Ports (Exactly 1 SE Port at random theta)
            rad_c_temp = self._compute_island_radius()
            theta = self.rng.uniform(0.02 * math.pi, 0.28 * math.pi)
            
            # Hitung arah normal dari pusat pulau menuju ke laut
            len_dir = math.hypot(math.cos(theta), 0.5 * math.sin(theta))
            nx = math.cos(theta) / len_dir
            ny = (0.5 * math.sin(theta)) / len_dir
            
            # Cari segmen jalan kota terdekat yang sejajar dengan Axis 2 (kemiringan negatif)
            candidates = []
            if self._road_segs:
                for p1, p2 in self._road_segs:
                    dx = p2[0] - p1[0]
                    dy = p2[1] - p1[1]
                    # Axis 2 runs top-right to bottom-left (dx and dy have opposite signs, so dx * dy < 0)
                    if dx * dy >= 0:
                        continue
                    mx = (p1[0] + p2[0]) / 2
                    my = (p1[1] + p2[1]) / 2
                    c_val = 0.5 * mx + my
                    candidates.append((c_val, (p1, p2)))
            
            best_seg = None
            if candidates:
                max_c = max(item[0] for item in candidates)
                # Ambil kandidat segmen terluar (dalam toleransi 150 px dari garis terluar)
                outer_candidates = [item[1] for item in candidates if item[0] >= max_c - 150.0]
                
                # Pilih yang paling dekat dengan target sudut port
                min_d = float('inf')
                target_x = self.cx + rad_c_temp * math.cos(theta)
                target_y = self.cy + rad_c_temp * 0.5 * math.sin(theta)
                for p1, p2 in outer_candidates:
                    mx = (p1[0] + p2[0]) / 2
                    my = (p1[1] + p2[1]) / 2
                    d = math.hypot(mx - target_x, my - target_y)
                    if d < min_d:
                        min_d = d
                        best_seg = (p1, p2)
            
            if not best_seg:
                continue
                
            p1, p2 = best_seg
            # Center the port loop around the midpoint of best_seg and cap the length along Axis 2
            mx = (p1[0] + p2[0]) / 2
            my = (p1[1] + p2[1]) / 2
            L_road = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
            H_len = min(240.0, L_road / 2.0 - 10.0)
            
            # Axis 2 direction unit vector: (-0.8944, 0.4472)
            dx_shift = H_len * 0.8944
            dy_shift = H_len * 0.4472
            pt_left_land = (mx - dx_shift, my + dy_shift)
            pt_right_land = (mx + dx_shift, my - dy_shift)
            
            # Project seaward along Axis 1 (direction (+700, +350))
            pt_left = (pt_left_land[0] + 700, pt_left_land[1] + 350)
            pt_right = (pt_right_land[0] + 700, pt_right_land[1] + 350)
            
            # Buat jalan loop petak pelabuhan
            r1 = self._make_screen_road([pt_left, pt_right], bend=0.0)
            r2 = self._make_screen_road([pt_right, pt_right_land], bend=0.0)
            r3 = self._make_screen_road([pt_left_land, pt_left], bend=0.0)
            for r in (r1, r2, r3):
                if r:
                    r.is_port_road = True
            
            # Posisikan Pelabuhan sejajar dan rapat di belakang jalan pt_left -> pt_right (geser seaward 440 px)
            mid_x = (pt_left[0] + pt_right[0]) / 2
            mid_y = (pt_left[1] + pt_right[1]) / 2
            px = mid_x + 440
            py = mid_y + 220
            
            port = Pelabuhan(px, py)
            port.scale = 1.3
            port.radius = 180.0
            self.entities.append(port)
            self.occupied.append((px, py, 180.0, "Pelabuhan"))
            
            # Place cargo ship at the pier tip (shifted seaward to prevent overlapping the port)
            ship_x = px + 590
            ship_y = py + 160
            ship = KapalKargo(ship_x, ship_y)
            ship.scale = 0.8
            ship.radius = 80.0
            self.entities.append(ship)
            self.occupied.append((ship_x, ship_y, 80.0, "KapalKargo"))
            
            # Letakkan semen platform (cement base) di tengah petak jalan pelabuhan
            bc_x = (pt_left[0] + pt_right[0] + pt_left_land[0] + pt_right_land[0]) / 4
            bc_y = (pt_left[1] + pt_right[1] + pt_left_land[1] + pt_right_land[1]) / 4
            self.port_center = (bc_x, bc_y)
            plat = BasePlatform(bc_x, bc_y, "cement", 300, int(H_len * 0.8))
            plat.is_port_platform = True
            self.platforms.append(plat)
            self.entities.append(plat)
            self.occupied.append((bc_x, bc_y, 300, "Platform"))
            
            # Letakkan gedung-gedung dan rumah di dalam petak (exclude Apartemen)
            pool = ["Gedung", "GedungA", "GedungB", "GedungC", "GedungD", "RumahA", "RumahB", "RumahC", "RumahD"]
            g_scale = 0.75
            g_radius = math.hypot(75, 65) * g_scale
            
            # Tempatkan 3 bangunan dalam satu baris sejajar Axis 1 (menghindari kerumunan/overlap)
            v1_x = 200 * 0.8944
            v1_y = 200 * 0.4472
            
            positions = [
                (bc_x - v1_x, bc_y - v1_y),
                (bc_x, bc_y),
                (bc_x + v1_x, bc_y + v1_y)
            ]
            
            for px_b, py_b in positions:
                b_type = self.rng.choice(pool)
                self._add_centered(b_type, px_b, py_b, radius=g_radius, scale=g_scale, snap=False, force=True)
            
            self._place_lights()
            self._place_trees()
 
            rad_c = self._compute_island_radius()
            self.island = Pulau(self.cx, self.cy, rad_c=rad_c, rad_r=rad_c // 2)
            self.entities.insert(0, self.island)

            self._place_sea_details()
            self._adjust_sea_details()

            if self._validate(rad_c):
                break
            else:
                print(f"Validation failed on attempt {attempt}, regenerating...")
                
        self.entities.sort(key=self._depth_key)
        if hasattr(self, "island") and self.island in self.entities:
            self.entities.remove(self.island)
            self.entities.insert(0, self.island)
        return self.entities

    def compile_graph(self):
        from src.core.graph import Node
        self.generate()
        
        # Split road segments at intersections
        def line_intersection(A, B, C, D):
            dx1, dy1 = B[0] - A[0], B[1] - A[1]
            dx2, dy2 = D[0] - C[0], D[1] - C[1]
            denom = dx1 * dy2 - dy1 * dx2
            if abs(denom) < 1e-5:
                return None
            t = ((C[0] - A[0]) * dy2 - (C[1] - A[1]) * dx2) / denom
            u = ((C[0] - A[0]) * dy1 - (C[1] - A[1]) * dx1) / denom
            eps = 1e-3
            is_inside_s1 = eps <= t <= 1.0 - eps
            is_on_s2 = -eps <= u <= 1.0 + eps
            is_inside_s2 = eps <= u <= 1.0 - eps
            is_on_s1 = -eps <= t <= 1.0 + eps
            if (is_inside_s1 and is_on_s2) or (is_inside_s2 and is_on_s1):
                return (A[0] + t * dx1, A[1] + t * dy1)
            return None

        intersections = {i: [] for i in range(len(self._road_segs))}
        for i in range(len(self._road_segs)):
            for j in range(i + 1, len(self._road_segs)):
                A, B = self._road_segs[i]
                C, D = self._road_segs[j]
                P = line_intersection(A, B, C, D)
                if P:
                    intersections[i].append(P)
                    intersections[j].append(P)

        final_segments = []
        for i, (A, B) in enumerate(self._road_segs):
            pts = intersections[i]
            if not pts:
                final_segments.append((A, B))
                continue
            pts.sort(key=lambda p: (p[0] - A[0])**2 + (p[1] - A[1])**2)
            curr = A
            for p in pts:
                if math.hypot(p[0] - curr[0], p[1] - curr[1]) > 0.5:
                    final_segments.append((curr, p))
                    curr = p
            if math.hypot(B[0] - curr[0], B[1] - curr[1]) > 0.5:
                final_segments.append((curr, B))

        nodes_dict = {}
        edges_set = []
        for p1, p2 in final_segments:
            p1_t = (round(p1[0], 2), round(p1[1], 2))
            p2_t = (round(p2[0], 2), round(p2[1], 2))
            if p1_t not in nodes_dict: nodes_dict[p1_t] = Node(p1_t[0], p1_t[1])
            if p2_t not in nodes_dict: nodes_dict[p2_t] = Node(p2_t[0], p2_t[1])
            n1 = nodes_dict[p1_t]
            n2 = nodes_dict[p2_t]
            if not any((e[0] is n1 and e[1] is n2) or (e[0] is n2 and e[1] is n1) for e in edges_set):
                edge = (n1, n2)
                edges_set.append(edge)
                n1.edges.append(edge)
                n2.edges.append(edge)
            
        nodes_list = list(nodes_dict.values())
        edges_list = edges_set

        # Integrasi Bundaran ke dalam Graph
        # Cocokkan posisi bundaran yang sudah diletakkan di generate() dengan node terdekat di graph.
        # Hal ini menjamin keselarasan dengan tata letak bangunan dan mencegah tabrakan (overlap).
        rb_nodes = []
        for rx, ry in self.roundabout_positions:
            if not nodes_list:
                continue
            closest_node = min(nodes_list, key=lambda n: math.hypot(n.x - rx, n.y - ry))
            # Pastikan jaraknya masuk akal (misal < 100px) dan belum ditambahkan
            if math.hypot(closest_node.x - rx, closest_node.y - ry) < 100.0 and closest_node not in rb_nodes:
                closest_node.is_roundabout = True
                rb_nodes.append(closest_node)

        # Sinkronkan posisi visual bundaran dengan node yang dipilih
        self.roundabout_positions = [(rb.x, rb.y) for rb in rb_nodes]
        
        # Kontraksi node yang terlalu dekat dengan pusat bundaran (< 180.0) ke pusat bundaran
        for rb in rb_nodes:
            to_merge = []
            for n in nodes_list:
                if n is not rb and math.hypot(n.x - rb.x, n.y - rb.y) < 180.0:
                    to_merge.append(n)
            for n_close in to_merge:
                if n_close not in nodes_list:
                    continue
                for e in list(n_close.edges):
                    u, v = e
                    nb = v if u is n_close else u
                    
                    if nb is rb:
                        if e in edges_list:
                            edges_list.remove(e)
                        if e in rb.edges:
                            rb.edges.remove(e)
                        continue
                    
                    if e in edges_list:
                        edges_list.remove(e)
                    
                    new_edge = (rb, nb) if u is n_close else (nb, rb)
                    
                    if not any((ge[0] is rb and ge[1] is nb) or (ge[0] is nb and ge[1] is rb) for ge in edges_list):
                        edges_list.append(new_edge)
                        rb.edges.append(new_edge)
                        if e in nb.edges:
                            nb.edges.remove(e)
                        nb.edges.append(new_edge)
                    else:
                        if e in nb.edges:
                            nb.edges.remove(e)
                
                if n_close in nodes_list:
                    nodes_list.remove(n_close)

        # Hapus entitas Roundabout lama dari _place_roundabouts() —
        # posisinya tidak tepat dengan node graph, dan renderer sudah
        # menggunakan rb_nodes (bukan entities) untuk menggambar bundaran.
        self.entities = [e for e in self.entities if e.__class__.__name__ != 'Roundabout']

        buildings = []
        for e in self.entities:
            name = e.__class__.__name__
            if name not in ["Pulau", "RoadSegment", "RoadCorner90", "Roundabout"]:
                buildings.append({
                    'x': e.x,
                    'y': e.y,
                    'sort_y': getattr(e, 'render_y', e.y),
                    'type': name,
                    'scale': getattr(e, 'scale', 1.0),
                    'name': name,
                    'radius': getattr(e, 'radius', get_building_radius(name))
                })
                
        return {
            'nodes': nodes_list,
            'edges': edges_list,
            'buildings': buildings,
            'edge_curves': {},
            'roundabouts': rb_nodes,
            'hidden_edges': set(),
            'entities': self.entities,
            'editor_bg_entities': [e for e in self.entities if e.__class__.__name__ in ['Pulau', 'BasePlatform']]
        }

    def _assign_and_adjust_leaves(self, leaves):
        building_reqs = [
            ("Bandara", 14.0, 14.0),
            ("Stadion", 11.0, 12.0),
            ("Bianglala", 10.0, 8.0),
            ("BalaiKota", 12.0, 10.0),
            ("Sekolah", 6.0, 10.0),
            ("Museum", 9.5, 8.5),
            ("PusatPerbelanjaan", 8.5, 8.5),
            ("Danau", 11.0, 7.5),
            ("RumahSakit", 5.5, 6.0),
            ("Masjid", 5.5, 5.5),
            ("Bank", 5.5, 5.0),
            ("KantorPolisi", 5.0, 4.5),
            ("Pemadam", 5.0, 5.0),
            ("Minimarket", 5.0, 5.0),
            ("Minimarket", 5.0, 5.0),
            ("Taman", 8.5, 7.0),
            ("Taman", 8.5, 7.0),
            ("Taman", 8.5, 7.0),
            ("SPBU", 6.0, 6.0),
            ("residential", 6.0, 6.0),
            ("residential", 6.0, 6.0),
            ("residential", 6.0, 6.0),
            ("residential", 6.0, 6.0),
            ("urban", 6.0, 6.0),
            ("urban", 6.0, 6.0),
        ]
        
        building_reqs.sort(key=lambda item: item[1] * item[2], reverse=True)
        if len(leaves) < len(building_reqs):
            return False
            
        leaves.sort(key=lambda l: (l.cb - l.ca) * (l.rb - l.ra), reverse=True)
        assigned_leaves = leaves[:len(building_reqs)]
        
        for idx, (name, req_w, req_h) in enumerate(building_reqs):
            L = assigned_leaves[idx]
            # JANGAN menukar dimensi req_w dan req_h, karena orientasi bangunan isometrik 3D bersifat tetap (statis)
            # dan tidak mendukung rotasi dinamis. Dengan menonaktifkan swap ini, ukuran blok (leaf)
            # akan otomatis menyesuaikan dengan orientasi asli bangunan.
            
            if name == "residential":
                L.district_type = "residential"
            elif name == "urban":
                L.district_type = "urban"
            else:
                L.district_type = "individual"
                L.b_types = [name]
                
            L.req_w = req_w
            L.req_h = req_h
            
        for idx_leftover, L in enumerate(leaves[len(building_reqs):]):
            if idx_leftover % 2 == 0:
                L.district_type = "residential"
            else:
                L.district_type = "urban"
            L.req_w = 6.0
            L.req_h = 6.0
            
        if not hasattr(self, 'root') or self.root is None:
            return False
            
        # Run bottom-up pass
        self._compute_min_sizes(self.root)
        
        # Run top-down pass
        W_actual = self.root.min_w + 2.0
        H_actual = self.root.min_h + 2.0
        
        self._assign_coordinates(self.root, -W_actual / 2.0, -H_actual / 2.0, W_actual / 2.0, H_actual / 2.0)
        
        self.c_min = -W_actual / 2.0 - 2.0
        self.c_max = W_actual / 2.0 + 2.0
        self.r_min = -H_actual / 2.0 - 2.0
        self.r_max = H_actual / 2.0 + 2.0
        self.tree_bound_rad = (self.c_max - self.c_min) / 2.0 * 200 + 400
        
        return True

    def _compute_min_sizes(self, node):
        if node.left is None and node.right is None:
            node.min_w = getattr(node, 'req_w', 1.0)
            node.min_h = getattr(node, 'req_h', 1.0)
            return node.min_w, node.min_h
            
        w_l, h_l = self._compute_min_sizes(node.left)
        w_r, h_r = self._compute_min_sizes(node.right)
        
        if node.split_dir == 'c':
            node.min_w = w_l + w_r
            node.min_h = max(h_l, h_r)
        else:
            node.min_w = max(w_l, w_r)
            node.min_h = h_l + h_r
            
        return node.min_w, node.min_h

    def _assign_coordinates(self, node, ca, ra, cb, rb):
        node.ca, node.ra = ca, ra
        node.cb, node.rb = cb, rb
        
        if node.left is None and node.right is None:
            return
            
        w_total = cb - ca
        h_total = rb - ra
        
        if node.split_dir == 'c':
            min_w_l = node.left.min_w
            min_w_r = node.right.min_w
            extra_w = max(0.0, w_total - (min_w_l + min_w_r))
            share_l = min_w_l / (min_w_l + min_w_r) if (min_w_l + min_w_r) > 0 else 0.5
            split_val = ca + min_w_l + extra_w * share_l
            node.split_val = split_val
            
            self._assign_coordinates(node.left, ca, ra, split_val, rb)
            self._assign_coordinates(node.right, split_val, ra, cb, rb)
        else:
            min_h_l = node.left.min_h
            min_h_r = node.right.min_h
            extra_h = max(0.0, h_total - (min_h_l + min_h_r))
            share_l = min_h_l / (min_h_l + min_h_r) if (min_h_l + min_h_r) > 0 else 0.5
            split_val = ra + min_h_l + extra_h * share_l
            node.split_val = split_val
            
            self._assign_coordinates(node.left, ca, ra, cb, split_val)
            self._assign_coordinates(node.right, ca, split_val, cb, rb)

    # ── layout randomisation ──────────────────────────────────────────────────

    def _randomise_layout(self):
        rng = self.rng
        self.cx = 2400 + rng.randint(-300, 300)
        self.cy = 2750 + rng.randint(-150, 200)

        # Jadikan tata letak jalan lebih kompak agar mendekati tepi laut
        self.c_min = -20.0
        self.c_max =  20.0
        self.r_min = -20.0
        self.r_max =  20.0
        
        self.tree_bound_rad = (self.c_max - self.c_min) / 2.0 * 200 + 400

    def _g(self, c, r):
        return (self.cx + (c - r) * 100,
                self.cy + (c + r) * 50)

    def _road_bend_amount(self, node_count):
        # Return 0.0 to make roads perfectly straight and grid-like
        return 0.0

    def _normalize_edge(self, a, b):
        return tuple(sorted((tuple(a), tuple(b))))

    def _trim_existing_segments(self, screen_nodes):
        if len(screen_nodes) < 2: return screen_nodes
        existing = {self._normalize_edge(p1, p2) for p1, p2 in self._road_segs}
        while len(screen_nodes) > 2:
            if self._normalize_edge(screen_nodes[0], screen_nodes[1]) not in existing: break
            screen_nodes = screen_nodes[1:]
        while len(screen_nodes) > 2:
            if self._normalize_edge(screen_nodes[-2], screen_nodes[-1]) not in existing: break
            screen_nodes = screen_nodes[:-1]
        return screen_nodes

    def _make_road(self, grid_nodes, bend=None):
        if len(grid_nodes) < 2: return None
        if bend is None: bend = self._road_bend_amount(len(grid_nodes))
        screen_nodes = [self._g(c, r) for c, r in grid_nodes]
        screen_nodes = self._trim_existing_segments(screen_nodes)
        if len(screen_nodes) < 2: return None
        return self._make_screen_road(screen_nodes, bend)

    def _make_screen_road(self, screen_nodes, bend=0.0):
        if len(screen_nodes) < 2:
            return None
        if isinstance(bend, (list, tuple)) and len(bend) == len(screen_nodes) - 1:
            bends = list(bend)
        else:
            bend_val = 0.0 if isinstance(bend, (list, tuple)) else bend
            bends = [bend_val for _ in range(len(screen_nodes) - 1)]
        from assets.components import RoadSegment
        road = RoadSegment(
            screen_nodes[0][0], screen_nodes[0][1],
            screen_nodes[-1][0], screen_nodes[-1][1],
            bend_amount=bend, nodes=[list(pt) for pt in screen_nodes], bends=bends
        )
        self.roads.append(road)
        self.entities.append(road)
        for p1, p2 in zip(screen_nodes, screen_nodes[1:]):
            self._road_segs.append((p1, p2))
        return road

    def _creative_axis_nodes(self, start, end, axis):
        return [start, end]

    def _bsp_split(self, node, depth=0):
        w = node.cb - node.ca
        h = node.rb - node.ra
        min_size = 3.2
        corridor = 0.0
        
        # Keep exactly 2 nodes unsplit at depth 3 for Bandara and Stadion
        if depth == 3 and self.num_large_unsplit < 2:
            self.num_large_unsplit += 1
            return [node]
            
        # Perbesar max depth agar lebih banyak blok
        if depth >= 6 or (w < min_size * 2 + corridor and h < min_size * 2 + corridor):
            return [node]
            
        split_dir = 'c' if w > h else 'r'
        if 0.8 < w/h < 1.2:
            split_dir = self.rng.choice(['c', 'r'])
            
        if split_dir == 'c':
            if w < min_size * 2 + corridor: return [node]
            split_val = self.rng.uniform(node.ca + min_size + corridor/2, node.cb - min_size - corridor/2)
            left = BSPNode(node.ca, node.ra, split_val - corridor/2, node.rb)
            right = BSPNode(split_val + corridor/2, node.ra, node.cb, node.rb)
            node.split_val = split_val; node.split_dir = 'c'
        else:
            if h < min_size * 2 + corridor: return [node]
            split_val = self.rng.uniform(node.ra + min_size + corridor/2, node.rb - min_size - corridor/2)
            left = BSPNode(node.ca, node.ra, node.cb, split_val - corridor/2)
            right = BSPNode(node.ca, split_val + corridor/2, node.cb, node.rb)
            node.split_val = split_val; node.split_dir = 'r'
            
        node.left = left; node.right = right
        
        if not hasattr(self, 'intersections'): self.intersections = []
        if split_dir == 'c':
            self.intersections.append((split_val, node.ra + h/2))
        else:
            self.intersections.append((node.ca + w/2, split_val))

        leaves = []
        leaves.extend(self._bsp_split(left, depth+1))
        leaves.extend(self._bsp_split(right, depth+1))
        return leaves

    def _draw_active_leaf_roads(self, leaves):
        # Group horizontal segments (constant r) by r_val
        horiz = {}
        # Group vertical segments (constant c) by c_val
        vert = {}
        
        for leaf in leaves:
            ca = round(leaf.ca, 4)
            cb = round(leaf.cb, 4)
            ra = round(leaf.ra, 4)
            rb = round(leaf.rb, 4)
            
            # Horizontals (constant r)
            for r_val in (ra, rb):
                r_key = round(r_val, 4)
                if r_key not in horiz:
                    horiz[r_key] = []
                horiz[r_key].append((min(ca, cb), max(ca, cb)))
                
            # Verticals (constant c)
            for c_val in (ca, cb):
                c_key = round(c_val, 4)
                if c_key not in vert:
                    vert[c_key] = []
                vert[c_key].append((min(ra, rb), max(ra, rb)))
                
        def merge_intervals(intervals):
            if not intervals:
                return []
            intervals = sorted(intervals, key=lambda x: x[0])
            merged = [intervals[0]]
            for cur in intervals[1:]:
                prev = merged[-1]
                if cur[0] <= prev[1] + 0.05:  # Tolerance for float/adjacent alignment
                    merged[-1] = (prev[0], max(prev[1], cur[1]))
                else:
                    merged.append(cur)
            return merged

        # Merge and draw horizontal roads
        for r_val, intervals in horiz.items():
            merged = merge_intervals(intervals)
            for c1, c2 in merged:
                if c2 - c1 > 0.01:
                    self._make_road([(c1, r_val), (c2, r_val)], bend=0.0)
                    
        # Merge and draw vertical roads
        for c_val, intervals in vert.items():
            merged = merge_intervals(intervals)
            for r1, r2 in merged:
                if r2 - r1 > 0.01:
                    self._make_road([(c_val, r1), (c_val, r2)], bend=0.0)

    def _get_perimeter_points(self, plat, margin_c=0, margin_r=0, spacing=90):
        import math
        eff_c = plat.rad_c - margin_c
        eff_r = plat.rad_r - margin_r
        if eff_c < 20 or eff_r < 10: return []
        pts = []
        edges = [
            ((0, -eff_r), (eff_c, 0)),
            ((eff_c, 0), (0, eff_r)),
            ((0, eff_r), (-eff_c, 0)),
            ((-eff_c, 0), (0, -eff_r))
        ]
        for A, B in edges:
            length = math.hypot(B[0]-A[0], (B[1]-A[1])*2.0)
            num_steps = max(1, int(length // spacing))
            for i in range(num_steps):
                t = i / num_steps
                px = plat.x + A[0] + t * (B[0]-A[0])
                py = plat.render_y + A[1] + t * (B[1]-A[1])
                pts.append((px, py))
        return pts

    def _min_dist_to_roads(self, x, y):
        if not self._road_segs:
            return float("inf")
        best = float("inf")
        for (ax, ay), (bx, by) in self._road_segs:
            d = _dist_pt_seg(x, y, ax, ay, bx, by)
            if d < best:
                best = d
        return best

    def _fits_road_clearance(self, x, y, radius):
        clearance = ROAD_HALF_WIDTH + radius + 15.0
        return self._min_dist_to_roads(x, y) >= clearance

    def _find_open_spot(self, x, y, radius, factor=0.85, max_shift=190):
        if self._fits_occupied(x, y, radius, factor=factor):
            return x, y

        for ring in (55, 95, 135, max_shift):
            steps = 12
            phase = self.rng.random() * math.pi * 2
            for i in range(steps):
                ang = phase + i * math.pi * 2 / steps
                px = x + math.cos(ang) * ring
                py = y + math.sin(ang) * ring * 0.55
                if self._fits_occupied(px, py, radius, factor=factor):
                    return px, py
        return None

    def _scale_for_component(self, type_name, rad_c=None, rad_r=None):
        preferred = {
            "RumahA": 1.3, "RumahB": 1.3, "RumahC": 1.3, "RumahD": 1.3,
            "Gedung": 1.5, "GedungA": 1.5, "GedungB": 1.5, "GedungC": 1.5,
            "GedungD": 1.5, "Apartemen": 1.5,
            "BalaiKota": 1.0, "Sekolah": 1.0, "Museum": 0.85, "Stadion": 1.6,
            "RumahSakit": 1.3, "PusatPerbelanjaan": 1.4, "Pelabuhan": 1.3,
            "Taman": 1.3, "Danau": 1.2, "Bianglala": 1.0,
            "Lampu": 1.3, "PohonBulat": 1.3, "PohonPinus": 1.3,
            "Bank": 1.2, "KantorPolisi": 1.2, "Pemadam": 1.2,
            "SPBU": 0.75, "Bandara": 0.8,
        }.get(type_name, 1.0)


        if rad_c is None or rad_r is None:
            return preferred

        fit = max(0.30, min(1.0, min(rad_c / 260.0, rad_r / 170.0)))
        return max(0.30, min(preferred, fit * preferred))

    def _place_roundabouts(self):
        # Cari semua titik persimpangan jalan secara geometris
        junctions = []
        for i in range(len(self._road_segs)):
            for j in range(i + 1, len(self._road_segs)):
                A, B = self._road_segs[i]
                C, D = self._road_segs[j]
                
                dx1, dy1 = B[0] - A[0], B[1] - A[1]
                dx2, dy2 = D[0] - C[0], D[1] - C[1]
                denom = dx1 * dy2 - dy1 * dx2
                if abs(denom) < 1e-5:
                    continue
                t = ((C[0] - A[0]) * dy2 - (C[1] - A[1]) * dx2) / denom
                u = ((C[0] - A[0]) * dy1 - (C[1] - A[1]) * dx1) / denom
                eps = 1e-3
                if -eps <= t <= 1.0 + eps and -eps <= u <= 1.0 + eps:
                    px = A[0] + t * dx1
                    py = A[1] + t * dy1
                    junctions.append((px, py))
                    
        # Hapus persimpangan duplikat yang sangat dekat (< 5px)
        unique_junctions = []
        for pt in junctions:
            if not any(math.hypot(pt[0] - u[0], pt[1] - u[1]) < 5.0 for u in unique_junctions):
                unique_junctions.append(pt)
        junctions = unique_junctions

        if not junctions:
            junctions = [self._g(c, r) for c, r in self.intersections]
        
        self.roundabout_positions = []
        # Acak urutan junctions agar letak bundaran berpindah-pindah
        self.rng.shuffle(junctions)
        
        target_count = self.rng.randint(3, 5)
        dist_req = 800
        
        while len(self.roundabout_positions) < target_count and dist_req >= 0:
            for x, y in junctions:
                if len(self.roundabout_positions) >= target_count:
                    break
                too_close = False
                for rx, ry in self.roundabout_positions:
                    if math.hypot(x - rx, y - ry) < dist_req:
                        too_close = True
                        break
                
                # Cek jika sudah menjadi bundaran
                if (x, y) in self.roundabout_positions:
                    too_close = True
            
                if not too_close:
                    rb = Roundabout(0, 0)
                    rb.c, rb.r = screen_to_grid(x, y)
                    rb.x, rb.y = x, y
                    self.entities.append(rb)
                    self.occupied.append((x, y, 230, "Roundabout"))
                    self.roundabout_positions.append((x, y))
            dist_req -= 200

    def _nudge_away_from_roundabouts(self, px, py, radius):
        import math
        nudge_occurred = False
        for rx, ry in self.roundabout_positions:
            dx = px - rx
            dy = py - ry
            dist = math.hypot(dx, dy * 2.0)
            min_dist = 140.25 + radius + 40.0 # 40px safety buffer
            if dist < min_dist:
                nudge_occurred = True
                if dist < 0.001:
                    dx, dy = 1.0, 0.0
                    dist = 1.0
                dir_x = dx / dist
                dir_y = (dy * 2.0) / dist
                px = rx + dir_x * min_dist
                py = ry + (dir_y / 2.0) * min_dist
        return px, py, nudge_occurred

    def _populate_districts(self, leaves):
        self.residential_district_count = 0
        self.urban_platforms = []
        
        for leaf in leaves:
            d_type = getattr(leaf, "district_type", None)
            if d_type == "individual":
                self._gen_individual_district(leaf, leaf.b_types)
            elif d_type == "residential":
                self._gen_residential_district(leaf)
            elif d_type == "urban":
                self._gen_urban_district(leaf)

    def _add_platform(self, c, r, material, rad_c, rad_r, x=None, y=None):
        if x is None or y is None:
            x, y = self._g(c, r)
        plat = BasePlatform(x, y, material, rad_c, rad_r)
        self.platforms.append(plat); self.entities.append(plat)
        self.occupied.append((x, y, max(rad_c, rad_r), "Platform"))
        return plat

    def _add_centered(self, type_name, x, y, radius=60, scale=None, snap=True, force=False):
        import math
        cls = CLASS_MAP.get(type_name)
        if not cls: return
        if scale is None:
            scale = self._scale_for_component(type_name)
        meta = COMPONENT_META.get(type_name, {"w": 80, "h": 80})
        meta_w = meta.get("w", 80)
        meta_h = meta.get("h", 80)
        if radius == 60:
            true_radius = math.hypot(meta_w / 2.0, meta_h / 2.0) * scale
        else:
            true_radius = radius
        if not force:
            if snap:
                spot = self._find_open_spot(x, y, true_radius)
                if spot is None:
                    return None
                x, y = spot
            else:
                # Cek tabrakan dengan bangunan lain DAN jarak ke jalan
                if not self._fits_occupied(x, y, true_radius, factor=1.0, include_roads=True):
                    return None
        meta = COMPONENT_META.get(type_name, {"ax": 0.0, "ay": 0.0})
        ox = meta.get("ax", 0.0)
        oy = meta.get("ay", 0.0)
        ent = cls(x - ox, y - oy)
        ent.scale = scale
        ent.map_scale = scale
        ent.radius = true_radius
        ent.map_radius = true_radius
        
        # Tambahkan render_y khusus untuk penataan kedalaman yang akurat bagi bangunan raksasa
        if type_name == "Museum":
            ent.render_y = y + 286 * scale
        elif type_name == "Bandara":
            ent.render_y = y + 528 * scale
        elif type_name == "BalaiKota":
            ent.render_y = y + 416 * scale
        elif type_name == "Sekolah":
            ent.render_y = y + 288 * scale
        elif type_name == "Stadion":
            ent.render_y = y + 282 * scale
            
        self.entities.append(ent); self.land_ents.append(ent)
        self.occupied.append((x, y, true_radius, type_name))
        return ent

    def _fits_occupied(self, x, y, radius, factor=0.85, include_roads=True):
        import math
        if include_roads and not self._fits_road_clearance(x, y, radius):
            return False
        for ox, oy, other_radius, o_type in self.occupied:
            if o_type == "Platform": continue
            dx = x - ox; dy = (y - oy) * 2.0
            if math.hypot(dx, dy) < (radius + other_radius) * factor: return False
        return True

    def _gen_residential_district(self, leaf):
        c_center = (leaf.ca + leaf.cb) / 2
        r_center = (leaf.ra + leaf.rb) / 2
        leaf_w = leaf.cb - leaf.ca
        leaf_h = leaf.rb - leaf.ra

        plat_c = int(leaf_w / 2.0 * 100.0 - ROAD_HALF_WIDTH)
        plat_r = int(leaf_h / 2.0 * 100.0 - ROAD_HALF_WIDTH)
        plat_c = max(40, plat_c)
        plat_r = max(40, plat_r)

        px, py = self._g(c_center, r_center)
        px, py, nudged = self._nudge_away_from_roundabouts(px, py, max(plat_c, plat_r))
        if nudged:
            x_rel = px - self.cx
            y_rel = py - self.cy
            c_center = (x_rel / 100.0 + y_rel / 50.0) / 2.0
            r_center = (y_rel / 50.0 - x_rel / 100.0) / 2.0

        plat = self._add_platform(c_center, r_center, "asphalt", plat_c, plat_r, x=px, y=py)

        house_pool = ["RumahA", "RumahB", "RumahC", "RumahD"]
        h_type = house_pool[self.residential_district_count % len(house_pool)]
        self.residential_district_count += 1

        meta_w = COMPONENT_META[h_type]["w"]
        house_scale = 0.75
        h_radius = math.hypot(meta_w / 2.0, meta_w / 2.0) * house_scale
        
        spacing = 180.0 * house_scale
        cols = 3
        rows = 3
        target_count = cols * rows

        placed = 0
        placed_entities = []
        for i in range(cols):
            for j in range(rows):
                if placed >= target_count:
                    break
                dc = - (cols - 1) * spacing / 2.0 + i * spacing
                dr = - (rows - 1) * spacing / 2.0 + j * spacing
                c_val = c_center + dc / 111.8
                r_val = r_center + dr / 111.8
                px, py = self._g(c_val, r_val)
                ent = self._add_centered(h_type, px, py, radius=h_radius, scale=house_scale, snap=False)
                if ent:
                    placed_entities.append(ent)
                    placed += 1

        if placed == 0:
            px, py = self._g(c_center, r_center)
            self._add_centered(h_type, px, py, radius=h_radius, scale=house_scale, snap=False, force=True)

    def _gen_urban_district(self, leaf):
        c_center = (leaf.ca + leaf.cb) / 2
        r_center = (leaf.ra + leaf.rb) / 2
        leaf_w = leaf.cb - leaf.ca
        leaf_h = leaf.rb - leaf.ra

        plat_c = int(leaf_w / 2.0 * 100.0 - ROAD_HALF_WIDTH)
        plat_r = int(leaf_h / 2.0 * 100.0 - ROAD_HALF_WIDTH)
        plat_c = max(40, plat_c)
        plat_r = max(40, plat_r)

        px, py = self._g(c_center, r_center)
        px, py, nudged = self._nudge_away_from_roundabouts(px, py, max(plat_c, plat_r))
        if nudged:
            x_rel = px - self.cx
            y_rel = py - self.cy
            c_center = (x_rel / 100.0 + y_rel / 50.0) / 2.0
            r_center = (y_rel / 50.0 - x_rel / 100.0) / 2.0

        plat = self._add_platform(c_center, r_center, "cement", plat_c, plat_r, x=px, y=py)
        self.urban_platforms.append(plat)

        pool = ["Gedung", "GedungA", "GedungB", "GedungC", "GedungD", "Apartemen"]
        
        g_scale = 0.7
        g_radius = math.hypot(75, 65) * g_scale
        
        spacing = 260.0 * g_scale
        cols = 2
        rows = 2
        target_count = cols * rows

        placed = 0
        placed_entities = []
        for i in range(cols):
            for j in range(rows):
                if placed >= target_count:
                    break
                dc = - (cols - 1) * spacing / 2.0 + i * spacing
                dr = - (rows - 1) * spacing / 2.0 + j * spacing
                c_val = c_center + dc / 111.8
                r_val = r_center + dr / 111.8
                px, py = self._g(c_val, r_val)
                b_type = self.rng.choice(pool)
                ent = self._add_centered(b_type, px, py, radius=g_radius, scale=g_scale, snap=False)
                if ent:
                    placed_entities.append(ent)
                    placed += 1

        if placed == 0:
            px, py = self._g(c_center, r_center)
            b_type = self.rng.choice(pool)
            self._add_centered(b_type, px, py, radius=g_radius, scale=g_scale, snap=False, force=True)

    def _gen_individual_district(self, leaf, b_types):
        b_type = b_types[0]
        if b_type == "Nature":
            return

        c_center = (leaf.ca + leaf.cb) / 2
        r_center = (leaf.ra + leaf.rb) / 2
        leaf_w = leaf.cb - leaf.ca
        leaf_h = leaf.rb - leaf.ra

        meta = COMPONENT_META.get(b_type, {"w": 250, "h": 190})
        meta_w = meta.get("w", 250)
        meta_h = meta.get("h", 190)

        target_w = meta_w
        target_h = meta_h

        # Swap dimensions to fit the leaf snugness if column is narrower than width
        if leaf_w * 100.0 - ROAD_HALF_WIDTH * 2 < target_w:
            target_w, target_h = target_h, target_w

        # All individual buildings draw their own bases or have none
        no_platform_types = [
            "Sekolah", "PusatPerbelanjaan", "Minimarket", "Danau", "Bandara", "Stadion",
            "BalaiKota", "Museum", "Masjid", "RumahSakit", "Bank", "KantorPolisi",
            "Pemadam", "SPBU", "Taman", "Bianglala"
        ]
        
        # Determine platform size to fill the leaf snugly
        half_leaf_w = leaf_w / 2.0
        half_leaf_h = leaf_h / 2.0
        plat_c = max(40, int(half_leaf_w * 100.0 - ROAD_HALF_WIDTH))
        plat_r = max(40, int(half_leaf_h * 100.0 - ROAD_HALF_WIDTH))

        if b_type in no_platform_types:
            material = None
        else:
            material = "cement"

        # Batasi skala secara dinamis agar bangunan tidak meluber keluar kavling (leaf) dan menabrak jalan
        preferred_scale = self._scale_for_component(b_type)
        max_scale_c = plat_c / (target_w / 2.0) if target_w > 0 else preferred_scale
        max_scale_r = plat_r / (target_h / 2.0) if target_h > 0 else preferred_scale
        b_scale = min(preferred_scale, max_scale_c, max_scale_r)
        true_col_radius = math.hypot(target_w / 2.0, target_h / 2.0) * b_scale

        px, py = self._g(c_center, r_center)
        R_avoid = max(true_col_radius, max(plat_c, plat_r) if material is not None else 0)
        px, py, _ = self._nudge_away_from_roundabouts(px, py, R_avoid)
        # Try to add building first
        ent = self._add_centered(b_type, px, py, radius=true_col_radius, scale=b_scale, snap=False, force=True)
        if ent is not None:
            # Building placed successfully! Now add platform.
            if material is not None:
                self._add_platform(c_center, r_center, material, plat_c, plat_r, x=px, y=py)

    def _place_corners_and_snap(self):
        pass

    def _place_lights(self):
        # Dapatkan semua node persimpangan/sudut
        nodes_to_light = []
        for ent in self.entities:
            if ent.__class__.__name__ in ("Roundabout", "RoadCorner90"):
                nodes_to_light.append((ent.x, ent.y))
        
        # Juga ambil dari endpoints jalan
        for p1, p2 in self._road_segs:
            nodes_to_light.append(p1)
            nodes_to_light.append(p2)
            
        # Buat set unik untuk menghindari duplikat lampu di posisi yang sama
        unique_nodes = []
        for pt in nodes_to_light:
            if not any(math.hypot(pt[0] - u[0], pt[1] - u[1]) < 30 for u in unique_nodes):
                unique_nodes.append(pt)
                
        # Untuk setiap persimpangan/sudut, tempatkan lampu di sisi jalan
        for x, y in unique_nodes:
            # Hitung arah bisector dari semua segmen jalan yang terhubung ke node ini
            connected_dirs = []
            for p1, p2 in self._road_segs:
                if math.hypot(p1[0] - x, p1[1] - y) < 5.0:
                    dx = p2[0] - x
                    dy = p2[1] - y
                    length = math.hypot(dx, dy)
                    if length > 0:
                        connected_dirs.append((dx / length, dy / length))
                elif math.hypot(p2[0] - x, p2[1] - y) < 5.0:
                    dx = p1[0] - x
                    dy = p1[1] - y
                    length = math.hypot(dx, dy)
                    if length > 0:
                        connected_dirs.append((dx / length, dy / length))
            
            if connected_dirs:
                avg_x = sum(d[0] for d in connected_dirs) / len(connected_dirs)
                avg_y = sum(d[1] for d in connected_dirs) / len(connected_dirs)
                avg_len = math.hypot(avg_x, avg_y)
                if avg_len > 0.01:
                    # Tempatkan di arah berlawanan dari bisector jalan (keluar dari persimpangan/sudut)
                    nx, ny = -avg_x / avg_len, -avg_y / avg_len
                else:
                    # Jika seimbang (seperti perempatan tegak lurus), gunakan tegak lurus dari jalan pertama
                    dx, dy = connected_dirs[0]
                    nx, ny = -dy, dx
            else:
                nx, ny = 1.0, 0.0
                
            # Offset ke pinggir jalan: setengah lebar jalan + margin lampu (RW = 85, setengahnya 42.5)
            lx = x + nx * 65.0
            ly = y + ny * 65.0
                
            # Pastikan tidak tumpang tindih dengan bangunan lain
            if self._fits_occupied(lx, ly, 10, include_roads=False):
                # Gunakan force=True agar tidak gagal dalam pengecekan jarak ke jalan
                # Gunakan scale=1.5 agar terlihat jelas dan tidak terlalu kecil
                self._add_centered("Lampu", lx, ly, radius=10, scale=1.5, snap=False, force=True)

    def _place_trees(self):
        # We want to fill the outer area with trees to make it a dense forest.
        rad_c = self._compute_island_radius()
        rad_r = rad_c // 2
        
        # Get the bounding box of the entire road network from self.cx, self.cy
        max_road_dx = 0.0
        max_road_dy = 0.0
        for p1, p2 in self._road_segs:
            max_road_dx = max(max_road_dx, abs(p1[0] - self.cx), abs(p2[0] - self.cx))
            max_road_dy = max(max_road_dy, abs(p1[1] - self.cy), abs(p2[1] - self.cy))
            
        # Get all port block centers
        port_centers = [self.port_center] if hasattr(self, 'port_center') else []

        # We will attempt to place around 8000 trees, randomly distributed.
        attempts = 8000
        for _ in range(attempts):
            # Uniform distribution inside the island ellipse (with 60px / 30px shore margin)
            r_scale = math.sqrt(self.rng.random())
            angle = self.rng.uniform(0, 2.0 * math.pi)
            
            tx = self.cx + (rad_c - 60) * r_scale * math.cos(angle)
            ty = self.cy + (rad_r - 30) * r_scale * math.sin(angle)
            
            # 1. Must NOT be inside the city block area. We find the nearest road segment
            # and verify if the sampled point is further from the center than that road.
            best_seg = None
            min_d = float('inf')
            for p1, p2 in self._road_segs:
                d = _dist_pt_seg(tx, ty, p1[0], p1[1], p2[0], p2[1])
                if d < min_d:
                    min_d = d
                    best_seg = (p1, p2)
                    
            if best_seg:
                p1, p2 = best_seg
                mx = (p1[0] + p2[0]) / 2
                my = (p1[1] + p2[1]) / 2
                dist_point = math.hypot(tx - self.cx, (ty - self.cy) * 2.0)
                dist_road = math.hypot(mx - self.cx, (my - self.cy) * 2.0)
                # If the point is closer to the center than the nearest road (with 50px buffer), skip
                if dist_point <= dist_road - 50.0:
                    continue
                
            # Make trees inside the city/urban area (between streets/columns) extremely sparse
            is_inside_city = (abs(tx - self.cx) <= max_road_dx + 80.0 and abs(ty - self.cy) <= max_road_dy + 40.0)
            if is_inside_city:
                # 90% chance to skip trees inside the city area to prevent them from being dense
                if self.rng.random() > 0.10:
                    continue
                
            # 2. Must NOT be inside/near the port block areas
            inside_port_hard = False
            near_port = False
            for bc_x, bc_y in port_centers:
                dist = math.hypot(tx - bc_x, (ty - bc_y) * 2.0)
                if dist < 320:
                    inside_port_hard = True
                    break
                elif dist < 800:
                    near_port = True
            
            if inside_port_hard:
                continue
            if near_port and self.rng.random() > 0.15:
                # 85% chance to skip trees near the port to keep it sparse
                continue
                
            # 3. Choose tree type
            t_type = self.rng.choice(["PohonPinus", "PohonBulat"])
            scale = self._scale_for_component(t_type)
            meta_w = COMPONENT_META.get(t_type, {"w": 60}).get("w", 60)
            t_radius = meta_w * scale * 0.55
            
            # 4. Check road and platform clearance (road width RW = 85, so half is 42.5. We use 65.0 clearance to prevent road overlaps)
            if self._min_dist_to_roads(tx, ty) < 65.0:
                continue
            if self._in_platform(tx, ty):
                continue
                
            # 5. Check other occupied entities (with factor=0.9 so trees are comfortable but not overlapping)
            if not self._fits_occupied(tx, ty, t_radius, factor=0.9, include_roads=False):
                continue
                
            # Add tree
            self._add_centered(t_type, tx, ty, radius=t_radius)

    def _place_sea_details(self):
        # 1. Place 3 Mercusuar in the sea (beyond island boundary)
        mercusuar_thetas = [
            -0.5 * math.pi,   # Utara
            0.9 * math.pi,    # Barat
            1.45 * math.pi,   # Barat Laut
        ]
        for theta in mercusuar_thetas:
            mx = self.cx + math.cos(theta) * self.island.rad_c * 1.35
            my = self.cy + math.sin(theta) * self.island.rad_r * 1.35
            # Force placement in the sea: bypass road checks, just check occupation
            if self._fits_occupied(mx, my, 80, factor=0.8, include_roads=False):
                cls = CLASS_MAP.get("Mercusuar")
                if cls:
                    ent = cls(mx, my)
                    ent.scale = 1.0
                    ent.radius = 80.0
                    self.entities.append(ent)
                    self.occupied.append((mx, my, 80.0, "Mercusuar"))

        # 2. Place sea entities (ships, sharks, etc.) — Ikan removed
        sea_pool = ["KapalKargo", "KapalLayar", "KapalNelayan", "Speedboat", "Hiu"]
        num_sea_items = self.rng.randint(35, 50)
        for _ in range(num_sea_items):
            theta = self.rng.uniform(0, 2 * math.pi)
            dist_factor = self.rng.uniform(1.1, 1.8)
            sx = self.cx + math.cos(theta) * self.island.rad_c * dist_factor
            sy = self.cy + math.sin(theta) * self.island.rad_r * dist_factor
            
            if self._fits_occupied(sx, sy, 100, factor=0.7, include_roads=False):
                s_type = self.rng.choice(sea_pool)
                scale = 0.8 if s_type.startswith("Kapal") else 1.0
                radius = 80 if s_type.startswith("Kapal") else 30
                
                cls = CLASS_MAP.get(s_type)
                if cls:
                    meta = COMPONENT_META.get(s_type, {"ax": 0.0, "ay": 0.0})
                    ox = meta.get("ax", 0.0)
                    oy = meta.get("ay", 0.0)
                    ent = cls(sx - ox, sy - oy)
                    ent.scale = scale
                    ent.map_scale = scale
                    ent.radius = radius
                    ent.map_radius = radius
                    self.entities.append(ent)
                    self.occupied.append((sx, sy, radius, s_type))

    def _adjust_sea_details(self):
        pass

    def _push_outside_island(self, x, y):
        import math
        dx = x - self.cx
        dy = y - self.cy
        length = math.hypot(dx, dy)
        if length == 0: dx, dy = 1, 0; length = 1
        min_rad = self.island.rad_c + 150
        if length < min_rad:
            return self.cx + dx / length * min_rad, self.cy + dy / length * (min_rad * 0.5)
        return x, y

    def _in_ellipse(self, x, y, rad_c):
        dx = (x - self.cx) / rad_c
        dy = (y - self.cy) / (rad_c * 0.5)
        return dx * dx + dy * dy <= 1.0

    def _in_platform(self, x, y):
        return any(p.is_point_inside((x, y)) for p in self.platforms)

    def _compute_island_radius(self):
        max_dx = max_dy = 0.0
        def touch(x, y):
            nonlocal max_dx, max_dy
            max_dx = max(max_dx, abs(x - self.cx))
            max_dy = max(max_dy, abs(y - self.cy))

        for ent in self.entities:
            name = ent.__class__.__name__
            if name in ("Pelabuhan", "KapalKargo", "KapalLayar", "Hiu", "KapalNelayan", "Speedboat", "Mercusuar"):
                continue
            if getattr(ent, "is_port_road", False) or getattr(ent, "is_port_platform", False):
                continue
            if name == "BasePlatform":
                for cx, cy in ent.get_corners(): touch(cx, cy)
            elif name == "RoadSegment":
                for nx, ny in ent.nodes: touch(nx, ny)
            elif name in ("Roundabout", "RoadCorner90"):
                touch(ent.x + 270, ent.y); touch(ent.x - 270, ent.y)
                touch(ent.x, ent.y + 145); touch(ent.x, ent.y - 145)
            else:
                ex, ey = getattr(ent, "x", 0), getattr(ent, "y", 0)
                touch(ex, ey)

        rad_c = int(max(1700, max_dx + 40, max_dy * 2.0 + 40))
        road_area = self._road_length() * (40.0 * 2.0)
        import math
        min_rad = math.sqrt((road_area * 1.50) / (math.pi * 0.5))
        return int(max(rad_c, min_rad))

    def _road_length(self):
        import math
        return sum(math.hypot(bx - ax, by - ay) for (ax, ay), (bx, by) in self._road_segs)

    def _validate(self, rad_c):
        required = [
            "Bandara", "Museum", "BalaiKota", "Sekolah", "Stadion",
            "PusatPerbelanjaan", "RumahSakit", "Masjid", "Pemadam",
            "Danau", "Taman", "Bianglala", "Bank", "KantorPolisi",
            "SPBU"
        ]
        names = [e.__class__.__name__ for e in self.entities]
        for req in required:
            if req not in names:
                return False
        if names.count("Minimarket") < 2:
            return False
        return True

    def _roads_connected(self):
        return True

    def _depth_key(self, entity):
        name = entity.__class__.__name__
        x, y = getattr(entity, "x", 0), getattr(entity, "y", 0)
        if hasattr(entity, "render_y"): y = entity.render_y
        if name == "Pulau": return y - 8000
        if name == "BasePlatform": return y - 5000
        if name in ("RoadSegment", "Roundabout", "RoadCorner90"): return y - 4500
        if name in ("KapalKargo", "KapalLayar", "Hiu", "Mercusuar", "KapalNelayan", "Speedboat"): return y + 1000
        return y + x * 0.0001
