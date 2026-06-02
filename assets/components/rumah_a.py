import pygame

class RumahA:
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
            c_door = (80, 50, 30)
            draw_poly([(x1, y, z1), (x2, y, z1), (x2, y, z2), (x1, y, z2)], c_door)

        def draw_hip_roof(x1, x2, y1, y2, z_base, z_top, color_base):
            r, g, b = color_base
            c_front_left = (max(0, r-10), max(0, g-10), max(0, b-10))
            c_front_right = (max(0, r-30), max(0, g-30), max(0, b-30))
            
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            dx = x2 - x1
            dy = y2 - y1
            
            if dx > dy:
                offset = dy / 2
                ridge_x1 = x1 + offset
                ridge_x2 = x2 - offset
                
                # Left Face (y = y2) - Trapesium
                pts_left = [(x1, y2, z_base), (x2, y2, z_base), (ridge_x2, mid_y, z_top), (ridge_x1, mid_y, z_top)]
                # Right Face (x = x2) - Segitiga
                pts_right = [(x2, y1, z_base), (x2, y2, z_base), (ridge_x2, mid_y, z_top)]
            else:
                offset = dx / 2
                ridge_y1 = y1 + offset
                ridge_y2 = y2 - offset
                
                # Left Face (y = y2) - Segitiga
                pts_left = [(x1, y2, z_base), (x2, y2, z_base), (mid_x, ridge_y2, z_top)]
                # Right Face (x = x2) - Trapesium
                pts_right = [(x2, y1, z_base), (x2, y2, z_base), (mid_x, ridge_y2, z_top), (mid_x, ridge_y1, z_top)]

            pts2d_left = [iso(*p) for p in pts_left]
            pygame.draw.polygon(screen, c_front_left, pts2d_left)
            pygame.draw.aalines(screen, (50,50,50), True, pts2d_left)
            
            pts2d_right = [iso(*p) for p in pts_right]
            pygame.draw.polygon(screen, c_front_right, pts2d_right)
            pygame.draw.aalines(screen, (50,50,50), True, pts2d_right)

        # URUTAN MENGGAMBAR DARI BELAKANG KE DEPAN
        
        # 2. Main Body (x: 20..80, y: 20..70, z:2..40)
        draw_block(20, 80, 20, 70, 2, 40, (245, 235, 215))
        
        # Jendela Samping Kanan (wajah kanan, x=80)
        draw_window_right(80, 30, 60, 12, 28)
        
        # Pintu Depan (wajah kiri, y=70)
        draw_door_left(40, 60, 70, 2, 28)
        
        # Jendela Depan Kiri & Kanan (wajah kiri, y=70)
        draw_window_left(25, 35, 70, 12, 28)
        draw_window_left(65, 75, 70, 12, 28)
        
        # 3. Main Roof Base (Listplang) (x: 15..85, y: 15..75, z:40..43)
        draw_block(15, 85, 15, 75, 40, 43, (250, 250, 250))
        
        # 4. Main Hip Roof (Atap Perisai) (x: 17..83, y: 17..73, z:43..70)
        draw_hip_roof(17, 83, 17, 73, 43, 70, (180, 70, 50))
        
        # 5. Teras Depan Beton (x: 25..75, y: 70..95, z:2..4)
        draw_block(25, 75, 70, 95, 2, 4, (160, 165, 170))
        
        # 6. Pilar Teras (Kayu) di Kiri & Kanan Depan (z:4..40)
        draw_block(27, 32, 85, 90, 4, 40, (120, 70, 40))
        draw_block(68, 73, 85, 90, 4, 40, (120, 70, 40))
        
        # 7. Porch Roof / Kanopi Teras (x: 25..75, y: 75..95, z:40..43)
        draw_block(25, 75, 75, 95, 40, 43, (250, 250, 250))
        
        # 8. Atap Kanopi Teras Hip Pendek (x: 27..73, y: 75..93, z:43..55)
        draw_hip_roof(27, 73, 75, 93, 43, 55, (180, 70, 50))
