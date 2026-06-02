import pygame

class RumahB:
    def __init__(self, x, y):
        self.x, self.y = x, y
        
    def render(self, screen):
        cx, cy = self.x, self.y
        scale = getattr(self, 'scale', 1.0)
        s = 1.4 * scale
        
        def iso(x, y, z):
            rx = x - 50
            ry = y - 50
            return cx + (rx - ry) * s, cy + (rx + ry) * 0.5 * s - z * s

        def draw_poly(pts3d, color):
            pts2d = [iso(*p) for p in pts3d]
            pygame.draw.polygon(screen, color, pts2d)
            pygame.draw.aalines(screen, (max(0, color[0]-30), max(0, color[1]-30), max(0, color[2]-30)), True, pts2d)

        def draw_block(x1, x2, y1, y2, z1, z2, color_base):
            r, g, b = color_base
            c_top = (min(255, r+15), min(255, g+15), min(255, b+15))
            c_left = (max(0, r-20), max(0, g-20), max(0, b-20))
            c_right = (max(0, r-40), max(0, g-40), max(0, b-40))
            
            draw_poly([(x1,y2,z1), (x2,y2,z1), (x2,y2,z2), (x1,y2,z2)], c_left)
            draw_poly([(x2,y1,z1), (x2,y2,z1), (x2,y2,z2), (x2,y1,z2)], c_right)
            draw_poly([(x1,y1,z2), (x1,y2,z2), (x2,y2,z2), (x2,y1,z2)], c_top)

        def draw_window_left(x1, x2, y, z1, z2):
            c_glass = (150, 210, 230)
            c_frame = (255, 255, 255)
            draw_poly([(x1, y, z1), (x2, y, z1), (x2, y, z2), (x1, y, z2)], c_frame)
            draw_poly([(x1+2, y, z1+2), (x2-2, y, z1+2), (x2-2, y, z2-2), (x1+2, y, z2-2)], c_glass)

        def draw_window_right(x, y1, y2, z1, z2):
            c_glass = (150, 210, 230)
            c_frame = (255, 255, 255)
            draw_poly([(x, y1, z1), (x, y2, z1), (x, y2, z2), (x, y1, z2)], c_frame)
            draw_poly([(x, y1+2, z1+2), (x, y2-2, z1+2), (x, y2-2, z2-2), (x, y1+2, z2-2)], c_glass)

        def draw_door_left(x1, x2, y, z1, z2):
            c_door = (100, 60, 40)
            draw_poly([(x1, y, z1), (x2, y, z1), (x2, y, z2), (x1, y, z2)], c_door)

        def draw_pyramid_roof(x1, x2, y1, y2, z_base, z_top, color_base):
            r, g, b = color_base
            c_front_left = (max(0, r-10), max(0, g-10), max(0, b-10))
            c_front_right = (max(0, r-30), max(0, g-30), max(0, b-30))
            
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            
            # Left Face of Roof (y = y2)
            pts_left = [(x1, y2, z_base), (x2, y2, z_base), (mid_x, mid_y, z_top)]
            pts2d_left = [iso(*p) for p in pts_left]
            pygame.draw.polygon(screen, c_front_left, pts2d_left)
            pygame.draw.aalines(screen, (50,50,50), True, pts2d_left)
            
            # Right Face of Roof (x = x2)
            pts_right = [(x2, y1, z_base), (x2, y2, z_base), (mid_x, mid_y, z_top)]
            pts2d_right = [iso(*p) for p in pts_right]
            pygame.draw.polygon(screen, c_front_right, pts2d_right)
            pygame.draw.aalines(screen, (50,50,50), True, pts2d_right)

        # 2. Teras Beton Depan (x: 15..85, y: 70..95)
        draw_block(15, 85, 70, 95, 2, 5, (180, 185, 190))
        
        # 3. Lantai 1 (x: 15..85, y: 15..70)
        draw_block(15, 85, 15, 70, 2, 30, (245, 245, 245))
        
        # Pintu Depan (wajah kiri, y=70)
        draw_door_left(40, 60, 70, 2, 22)
        # Jendela Kiri (wajah kiri, y=70)
        draw_window_left(18, 35, 70, 8, 22)
        # Jendela Kanan (wajah kiri, y=70)
        draw_window_left(65, 82, 70, 8, 22)
        
        # Jendela Samping Kanan (wajah kanan, x=85)
        draw_window_right(85, 20, 40, 8, 22)
        
        # 4. Lantai 2 (x: 15..85, y: 15..70)
        draw_block(15, 85, 15, 70, 30, 58, (230, 230, 235))
        
        # Jendela Lantai 2 Depan
        draw_window_left(20, 45, 70, 35, 50)
        draw_window_left(55, 80, 70, 35, 50)
        
        # 5. Atap Limas Modern (x: 10..90, y: 10..75)
        # Tambahkan base atap (listplang) agar sangat rapi dan tebal
        draw_block(10, 90, 10, 75, 58, 62, (50, 55, 60))
        # Piramida di atas base
        draw_pyramid_roof(12, 88, 12, 73, 62, 82, (60, 65, 70))
