import pygame

class RumahD:
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

        # URUTAN MENGGAMBAR DARI BELAKANG KE DEPAN
        
        # 2. Main Body Back (x: 20..80, y: 15..50)
        draw_block(20, 80, 15, 50, 2, 60, (235, 235, 235))
        
        # 3. Main Body Front (x: 20..80, y: 50..85)
        draw_block(20, 80, 50, 85, 2, 35, (235, 235, 235))
        
        # Pintu Depan Lantai 1
        draw_door_left(30, 50, 85, 2, 25)
        # Jendela Kanan Lantai 1
        draw_window_left(55, 75, 85, 10, 25)
        
        # Jendela Samping Kanan
        draw_window_right(80, 55, 80, 10, 25)
        
        # 4. Plat Topian Kayu (Canopy) di Atas Pintu Saja
        draw_block(28, 52, 85, 93, 26, 28, (160, 110, 60))
        
        # 5. Balkon Atas (x: 20..80, y: 50..70) - Di atas Lantai 1 Depan
        draw_block(20, 80, 50, 70, 35, 38, (80, 85, 90))
        
        # Pintu Balkon dan Jendela
        draw_door_left(45, 65, 50, 38, 55)
        draw_window_left(25, 40, 50, 38, 55)
        
        # Pagar Balkon Kaca (Kiri, Depan, Kanan)
        draw_block(20, 22, 50, 68, 38, 48, (150, 210, 230)) # Kiri
        draw_block(20, 80, 68, 70, 38, 48, (150, 210, 230)) # Depan
        draw_block(78, 80, 50, 68, 38, 48, (150, 210, 230)) # Kanan
        
        # 6. Atap Datar (x: 15..85, y: 10..55)
        draw_block(15, 85, 10, 55, 60, 65, (60, 65, 70))
