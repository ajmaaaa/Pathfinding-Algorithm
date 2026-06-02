import pygame

class RumahC:
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
            # Sangat tipis border
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
            # Bingkai
            draw_poly([(x1, y, z1), (x2, y, z1), (x2, y, z2), (x1, y, z2)], c_frame)
            # Kaca
            draw_poly([(x1+2, y, z1+2), (x2-2, y, z1+2), (x2-2, y, z2-2), (x1+2, y, z2-2)], c_glass)

        def draw_window_right(x, y1, y2, z1, z2):
            c_glass = (150, 210, 230)
            c_frame = (255, 255, 255)
            # Bingkai
            draw_poly([(x, y1, z1), (x, y2, z1), (x, y2, z2), (x, y1, z2)], c_frame)
            # Kaca
            draw_poly([(x, y1+2, z1+2), (x, y2-2, z1+2), (x, y2-2, z2-2), (x, y1+2, z2-2)], c_glass)

        # URUTAN MENGGAMBAR DARI BELAKANG KE DEPAN! (Painter's Algorithm)
        
        # 2. Back Wing (x: 10..50, y: 10..90) - Starts at z=2
        draw_block(10, 50, 10, 90, 2, 45, (250, 250, 250))
        # Jendela pada Back Wing (wajah kiri, y=90)
        draw_window_left(15, 45, 90, 15, 35)

        # 3. Side Wing (x: 50..90, y: 10..40) - Starts at z=2
        draw_block(50, 90, 10, 40, 2, 45, (250, 250, 250))
        # Jendela pada Side Wing (wajah kiri, y=40)
        draw_window_left(55, 85, 40, 15, 35)
        # Jendela pada Side Wing (wajah kanan, x=90)
        draw_window_right(90, 15, 35, 15, 35)
        
        # Pintu di sayap belakang (wajah kanan, x=50) -> menghadap sayap
        # draw_block(50, 51, 60, 80, 2, 25, (100, 60, 40)) 
        
        # 4. Deck Beton Teras Depan (Lantai Teras Abu-abu)
        # Teras ini akan pas berada di lekukan L-shape (x: 50..90, y: 40..90)
        draw_block(50, 90, 40, 90, 2, 4, (180, 185, 190))
        
        # 6. Wood Accent Pillar in Corner (x: 85..90, y: 85..90)
        draw_block(85, 90, 85, 90, 8, 45, (160, 110, 60))
        
        # 7. Floating Canopy
        draw_block(5, 95, 5, 95, 45, 50, (50, 55, 60))
