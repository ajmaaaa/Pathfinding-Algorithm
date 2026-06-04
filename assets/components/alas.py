import pygame
import math

class BasePlatform:
    def __init__(self, x, y, path_type='dirt', rad_c=360, rad_r=240):
        self.x = x
        self.render_y = y
        self.y = y - 300  # y harus kecil agar di-render sebelum bangunan di atasnya
        self.path_type = path_type
        self.rad_c = rad_c
        self.rad_r = rad_r
        
        # State untuk editor
        self.selected = False
        self.active_handle = None  # 'top', 'right', 'bottom', 'left'

    def get_corners(self):
        """Mendapatkan koordinat 4 sudut alas di layar"""
        cx, cy = self.x, self.render_y
        p_top = (cx - self.rad_c + self.rad_r, cy - (self.rad_c + self.rad_r) * 0.5)
        p_right = (cx + self.rad_c + self.rad_r, cy + (self.rad_c - self.rad_r) * 0.5)
        p_bot = (cx + self.rad_c - self.rad_r, cy + (self.rad_c + self.rad_r) * 0.5)
        p_left = (cx - self.rad_c - self.rad_r, cy + (-self.rad_c + self.rad_r) * 0.5)
        return p_top, p_right, p_bot, p_left

    def render(self, screen):
        cx, cy = self.x, self.render_y
        
        # Tentukan warna berdasarkan tipe
        if self.path_type == 'dirt': # Grass/Dirt
            c_top = (120, 180, 100)
            c_left = (100, 150, 80)
            c_right = (80, 120, 60)
        elif self.path_type == 'cement': # Semen
            c_top = (195, 200, 205)
            c_left = (175, 180, 185)
            c_right = (155, 160, 165)
        else:  # Asphalt
            c_top = (90, 95, 100)
            c_left = (70, 75, 80)
            c_right = (50, 55, 60)
            
        tinggi = 2
        
        # Hitung sudut-sudut alas
        p_top = (cx - self.rad_c + self.rad_r, cy - (self.rad_c + self.rad_r) * 0.5)
        p_right = (cx + self.rad_c + self.rad_r, cy + (self.rad_c - self.rad_r) * 0.5)
        p_bot = (cx + self.rad_c - self.rad_r, cy + (self.rad_c + self.rad_r) * 0.5)
        p_left = (cx - self.rad_c - self.rad_r, cy + (-self.rad_c + self.rad_r) * 0.5)
        
        pts_atas = [p_top, p_left, p_bot, p_right]
        pts_kiri = [p_left, p_bot, (p_bot[0], p_bot[1] + tinggi), (p_left[0], p_left[1] + tinggi)]
        pts_kanan = [p_bot, p_right, (p_right[0], p_right[1] + tinggi), (p_bot[0], p_bot[1] + tinggi)]
        
        # Draw sides and top
        pygame.draw.polygon(screen, c_left, pts_kiri)
        pygame.draw.polygon(screen, c_right, pts_kanan)
        pygame.draw.polygon(screen, c_top, pts_atas)
        
        pygame.draw.aalines(screen, c_left, True, pts_kiri)
        pygame.draw.aalines(screen, c_right, True, pts_kanan)
        pygame.draw.aalines(screen, c_top, True, pts_atas)

    def check_handle_click(self, mouse_pos, camera_x, camera_y, zoom, offset_x, offset_y):
        """Memeriksa apakah handle di-klik menggunakan koordinat screen space"""
        cx, cy = self.x, self.render_y
        p_top = (cx - self.rad_c + self.rad_r, cy - (self.rad_c + self.rad_r) * 0.5)
        p_right = (cx + self.rad_c + self.rad_r, cy + (self.rad_c - self.rad_r) * 0.5)
        p_bot = (cx + self.rad_c - self.rad_r, cy + (self.rad_c + self.rad_r) * 0.5)
        p_left = (cx - self.rad_c - self.rad_r, cy + (-self.rad_c + self.rad_r) * 0.5)
        
        handles = {'top': p_top, 'right': p_right, 'bottom': p_bot, 'left': p_left}
        
        for name, pt in handles.items():
            # Konversi titik dunia ke screen space
            scr_x = (pt[0] - camera_x) * zoom + offset_x
            scr_y = (pt[1] - camera_y) * zoom + offset_y
            
            if math.hypot(mouse_pos[0] - scr_x, mouse_pos[1] - scr_y) <= 15:
                return name
        return None

    def resize_with_mouse(self, mouse_pos):
        """Mengubah ukuran rad_c dan rad_r berdasarkan posisi mouse menggunakan proyeksi isometrik"""
        if not self.active_handle:
            return
            
        cx, cy = self.x, self.render_y
        
        # Konversi posisi mouse ke koordinat isometrik relatif (c, r) terhadap cx, cy
        dx = mouse_pos[0] - cx
        dy = mouse_pos[1] - cy
        
        c = dy + dx * 0.5
        r = dy - dx * 0.5
        
        # Update ukuran sesuai handle yang di-drag
        if self.active_handle == 'right':
            self.rad_c = max(40, int(c))
            self.rad_r = max(40, int(-r))
        elif self.active_handle == 'bottom':
            self.rad_c = max(40, int(c))
            self.rad_r = max(40, int(r))
        elif self.active_handle == 'left':
            self.rad_c = max(40, int(-c))
            self.rad_r = max(40, int(r))
        elif self.active_handle == 'top':
            self.rad_c = max(40, int(-c))
            self.rad_r = max(40, int(-r))
            
        self.y = self.render_y - 300

    def is_point_inside(self, pt):
        """Memeriksa apakah titik berada di dalam poligon atas alas"""
        cx, cy = self.x, self.render_y
        p_top = (cx - self.rad_c + self.rad_r, cy - (self.rad_c + self.rad_r) * 0.5)
        p_right = (cx + self.rad_c + self.rad_r, cy + (self.rad_c - self.rad_r) * 0.5)
        p_bot = (cx + self.rad_c - self.rad_r, cy + (self.rad_c + self.rad_r) * 0.5)
        p_left = (cx - self.rad_c - self.rad_r, cy + (-self.rad_c + self.rad_r) * 0.5)
        
        poly = [p_top, p_left, p_bot, p_right]
        num = len(poly)
        inside = False
        p1x, p1y = poly[0]
        for i in range(num + 1):
            p2x, p2y = poly[i % num]
            if pt[1] > min(p1y, p2y):
                if pt[1] <= max(p1y, p2y):
                    if pt[0] <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (pt[1] - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or pt[0] <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        return inside
