import pygame
import math
import random

C_GRASS_TOP = (130, 200, 100)
C_GRASS_SIDE = (80, 150, 60)
C_SAND_TOP  = (230, 210, 150)
C_SAND_SIDE = (180, 160, 110)
C_ROCK_TOP = (150, 155, 160)
C_ROCK_SIDE = (110, 115, 120)

class TerrainSystem:
    def __init__(self):
        self.grass_pts = []
        self.sand_pts = []
        self.rocks = []
        self.layer1_pts = []
        self.layer2_pts = []
        self.ocean_dir_center = (0, 0)

    def generate_island(self, entities):
        local_random = random.Random(42)
        if not entities:
            return
            
        # Pisahkan kapal, pelabuhan, & mercusuar dari perhitungan agar pulau tidak mekar sampai laut lepas
        land_entities = [e for e in entities if e.__class__.__name__ not in ('Pelabuhan', 'KapalKargo', 'KapalKargo2', 'Mercusuar')]
        if not land_entities:
            land_entities = entities
            
        ex = [e.x for e in land_entities]
        ey = [e.y for e in land_entities]
        
        cx = (min(ex) + max(ex)) / 2
        cy = (min(ey) + max(ey)) / 2
        self.ocean_dir_center = (cx, cy)
        
        # Jari-jari dihitung berdasarkan elips isometrik (lebar 2x tinggi)
        max_r = 0
        for e in land_entities:
            r = math.hypot((e.x - cx) / 2.0, e.y - cy)
            if r > max_r:
                max_r = r
                
        base_r = max_r + 200 
        
        N = 300 
        self.grass_pts = []
        self.layer1_pts = []
        self.layer2_pts = []
        self.sand_pts = []
        self.rocks = []
        
        for i in range(N):
            theta = (i / N) * math.pi * 2
            
            # Bentuk dasar pulau (Rumput)
            noise_grass = (
                60 * math.sin(4 * theta + 1) + 
                40 * math.cos(7 * theta) + 
                25 * math.sin(11 * theta + 2)
            )
            r_grass = base_r + noise_grass
            
            # Cliff factor menentukan tebing bergerigi vs wilayah pantai
            cliff_factor = math.sin(3 * theta) + 0.5 * math.cos(7 * theta)
            cliff_factor = max(0.0, min(1.0, (cliff_factor + 0.6) / 1.2))
            
            # Noise bergerigi tajam untuk lapisan bawah
            noise_l2 = 25 + 10 * math.sin(20 * theta) + 8 * math.cos(35 * theta)
            noise_l1 = 55 + 15 * math.cos(18 * theta) + 12 * math.sin(40 * theta)
            
            r_l2 = r_grass + cliff_factor * max(15, noise_l2)
            r_l1 = r_grass + cliff_factor * max(35, noise_l1)
            
            # Pantai
            beach_noise = math.sin(4 * theta + 2) + 0.6 * math.cos(7 * theta)
            sand_extension = 30 + max(0, 150 * beach_noise) * (1.0 - cliff_factor * 0.7)
            r_sand = r_l1 + sand_extension 
            
            # Konversi ke elips isometrik layar
            gx = cx + (r_grass * 2.0) * math.cos(theta)
            gy = cy + (r_grass * 1.0) * math.sin(theta)
            self.grass_pts.append((gx, gy))
            
            l2x = cx + (r_l2 * 2.0) * math.cos(theta)
            l2y = cy + (r_l2 * 1.0) * math.sin(theta)
            self.layer2_pts.append((l2x, l2y))
            
            l1x = cx + (r_l1 * 2.0) * math.cos(theta)
            l1y = cy + (r_l1 * 1.0) * math.sin(theta)
            self.layer1_pts.append((l1x, l1y))
            
            sx = cx + (r_sand * 2.0) * math.cos(theta)
            sy = cy + (r_sand * 1.0) * math.sin(theta)
            self.sand_pts.append((sx, sy))
            
            if cliff_factor > 0.5:
                rock_cluster = math.sin(6 * theta) + 0.5 * math.cos(14 * theta)
                if rock_cluster > 0.4 and local_random.random() < 0.4:
                    r_rock = r_l1 + local_random.uniform(2, 15)
                    rx = cx + (r_rock * 2.0) * math.cos(theta)
                    ry = cy + (r_rock * 1.0) * math.sin(theta)
                    size = local_random.uniform(20, 45)
                    height = local_random.uniform(15, 60)
                    self.rocks.append((rx, ry, size, height))

    def draw_extruded_polygon(self, screen, pts, offset_x, offset_y, camera_x, camera_y, zoom, color_top, color_side, z_top, z_bottom):
        screen_pts = []
        for p in pts:
            sx = (p[0] - camera_x) * zoom + offset_x
            sy = (p[1] - camera_y) * zoom + offset_y
            screen_pts.append((sx, sy))
            
        edges = []
        for i in range(len(screen_pts)):
            p1 = screen_pts[i]
            p2 = screen_pts[(i + 1) % len(screen_pts)]
            avg_sy = (p1[1] + p2[1]) / 2
            edges.append((avg_sy, p1, p2))
            
        edges.sort(key=lambda e: e[0]) 
        
        zt_scaled = z_top * zoom
        zb_scaled = z_bottom * zoom
        
        for avg_sy, p1, p2 in edges:
            dx = p2[0] - p1[0]
            if dx <= 0:
                p1_top = (p1[0], p1[1] - zt_scaled)
                p1_bot = (p1[0], p1[1] - zb_scaled)
                p2_top = (p2[0], p2[1] - zt_scaled)
                p2_bot = (p2[0], p2[1] - zb_scaled)
                
                shade = 1.0
                if dx < -2:
                    shade = 0.82
                
                c_side = (
                    int(color_side[0] * shade),
                    int(color_side[1] * shade),
                    int(color_side[2] * shade)
                )
                pygame.draw.polygon(screen, c_side, [p1_top, p2_top, p2_bot, p1_bot])
                pygame.draw.line(screen, (max(0, c_side[0]-25), max(0, c_side[1]-25), max(0, c_side[2]-25)), p1_top, p2_top, 1)
                
        top_pts = [(p[0], p[1] - zt_scaled) for p in screen_pts]
        pygame.draw.polygon(screen, color_top, top_pts)

    def draw_rock(self, screen, cx, cy, offset_x, offset_y, camera_x, camera_y, zoom, size, height, z_base):
        pts = []
        for i in range(6):
            angle = i * math.pi / 3
            r = size * (0.7 + 0.6 * ((i * 17 + int(cx)) % 10) / 10.0)
            px = cx + r * math.cos(angle) * 2.0
            py = cy + r * math.sin(angle) * 1.0
            pts.append((px, py))
            
        self.draw_extruded_polygon(screen, pts, offset_x, offset_y, camera_x, camera_y, zoom, C_ROCK_TOP, C_ROCK_SIDE, z_base + height, z_base)

    def render(self, screen, offset_x, offset_y, camera_x=0, camera_y=0, zoom=1.0):
        if not self.grass_pts or not self.sand_pts:
            return
            
        cy = self.ocean_dir_center[1]
        
        # Z-Levels
        Z_GRASS = 0     
        Z_MID = -20     
        Z_BOT = -45     
        Z_SEA = -70     
        
        # 1. Permukaan Pasir (Rata dengan air di Z_SEA = -70)
        sand_screen = []
        for p in self.sand_pts:
            sx = (p[0] - camera_x) * zoom + offset_x
            sy = (p[1] - Z_SEA - camera_y) * zoom + offset_y
            sand_screen.append((sx, sy))
        pygame.draw.polygon(screen, C_SAND_TOP, sand_screen)
        
        # 2. Bebatuan Belakang (Di belakang pulau)
        for rx, ry, size, height in self.rocks:
            if ry < cy:
                self.draw_rock(screen, rx, ry, offset_x, offset_y, camera_x, camera_y, zoom, size, height, Z_SEA)
        
        # 3. Tebing Berlapis
        C_DIRT_SIDE = (130, 110, 85)
        C_DIRT_TOP  = (150, 130, 100)
        C_ROCK_L2   = (105, 110, 115)
        C_ROCK_L1   = (85, 90, 95)
        
        # Layer 1
        self.draw_extruded_polygon(screen, self.layer1_pts, offset_x, offset_y, camera_x, camera_y, zoom, C_ROCK_L2, C_ROCK_L1, Z_BOT, Z_SEA)
        # Layer 2
        self.draw_extruded_polygon(screen, self.layer2_pts, offset_x, offset_y, camera_x, camera_y, zoom, C_DIRT_TOP, C_ROCK_L2, Z_MID, Z_BOT)
        # Layer 3
        self.draw_extruded_polygon(screen, self.grass_pts, offset_x, offset_y, camera_x, camera_y, zoom, C_GRASS_TOP, C_DIRT_SIDE, Z_GRASS, Z_MID)
        
        # 4. Bebatuan Depan
        for rx, ry, size, height in self.rocks:
            if ry >= cy:
                self.draw_rock(screen, rx, ry, offset_x, offset_y, camera_x, camera_y, zoom, size, height, Z_SEA)
