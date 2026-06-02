import pygame
import math

# Palet Warna Museum Modern / Kontemporer
C_WHITE = (245, 245, 245)      # Beton Putih
C_DARK = (45, 50, 55)          # Batu Hitam / Graphite
C_PLAZA = (210, 215, 210)      # Paving Abu-abu
C_GOLD = (230, 190, 60)        # Emas Monumen
C_GRASS = (168, 214, 123)      # Rumput
C_WATER = (90, 180, 230)       # Air Kolam

def render_museum(screen, cx, cy, scale=1.0):
    # Skala Global
    s = 1.3 * scale

    def iso(x, y, z):
        # Engine isometrik (rasio 2:1)
        sx = cx + (x - y) * 2 * s
        sy = cy + (x + y) * 1 * s - z * 2 * s
        return sx, sy

    def draw_block(x, y, z, w, d, h, color, glass_x=False, glass_y=False):
        # Kalkulasi Pencahayaan (Lighting)
        c_top = (min(255, color[0]+25), min(255, color[1]+25), min(255, color[2]+25)) 
        c_x = color  
        c_y = (max(0, color[0]-35), max(0, color[1]-35), max(0, color[2]-35))         
        c_line = (max(0, color[0]-75), max(0, color[1]-75), max(0, color[2]-75))      
        
        # Titik-titik poligon 3D
        p_top = [iso(x,y,z+h), iso(x+w,y,z+h), iso(x+w,y+d,z+h), iso(x,y+d,z+h)]
        p_x = [iso(x+w,y,z), iso(x+w,y+d,z), iso(x+w,y+d,z+h), iso(x+w,y,z+h)]
        p_y = [iso(x,y+d,z), iso(x+w,y+d,z), iso(x+w,y+d,z+h), iso(x,y+d,z+h)]
        
        # 1. Gambar Permukaan Padat
        if h > 0:
            pygame.draw.polygon(screen, c_x, p_x)
            pygame.draw.polygon(screen, c_y, p_y)
        pygame.draw.polygon(screen, c_top, p_top)
        
        # 2. Gambar Outline (Mempertegas bentuk 3D)
        thick = max(1, int(s*0.8))
        if h > 0:
            pygame.draw.lines(screen, c_line, True, p_x, thick)
            pygame.draw.lines(screen, c_line, True, p_y, thick)
        pygame.draw.lines(screen, c_line, True, p_top, thick)

        # 3. Kaca Bangunan Pemerintahan (Biru Cyan/Teal)
        g_c = (140, 210, 230)
        gl_c = (100, 170, 200)
        ins = 2
        
        if glass_x and d > 2*ins and h > 2*ins:
            gx_pts = [iso(x+w, y+ins, z+ins), iso(x+w, y+d-ins, z+ins), 
                      iso(x+w, y+d-ins, z+h-ins), iso(x+w, y+ins, z+h-ins)]
            pygame.draw.polygon(screen, g_c, gx_pts)
            pygame.draw.lines(screen, gl_c, True, gx_pts, thick)
            for i in range(1, max(2, int(d/10))):
                yi = y + ins + (d - 2*ins) * (i/int(d/10))
                pygame.draw.line(screen, gl_c, iso(x+w, yi, z+ins), iso(x+w, yi, z+h-ins), thick)
            for i in range(1, max(2, int(h/12))):
                zi = z + ins + (h - 2*ins) * (i/int(h/12))
                pygame.draw.line(screen, gl_c, iso(x+w, y+ins, zi), iso(x+w, y+d-ins, zi), thick)
                
        if glass_y and w > 2*ins and h > 2*ins:
            gy_pts = [iso(x+ins, y+d, z+ins), iso(x+w-ins, y+d, z+ins), 
                      iso(x+w-ins, y+d, z+h-ins), iso(x+ins, y+d, z+h-ins)]
            pygame.draw.polygon(screen, g_c, gy_pts)
            pygame.draw.lines(screen, gl_c, True, gy_pts, thick)
            for i in range(1, max(2, int(w/10))):
                xi = x + ins + (w - 2*ins) * (i/int(w/10))
                pygame.draw.line(screen, gl_c, iso(xi, y+d, z+ins), iso(xi, y+d, z+h-ins), thick)
            for i in range(1, max(2, int(h/12))):
                zi = z + ins + (h - 2*ins) * (i/int(h/12))
                pygame.draw.line(screen, gl_c, iso(x+ins, y+d, zi), iso(x+w-ins, y+d, zi), thick)

    def draw_pine_tree(x, y, z):
        tx, ty = iso(x, y, z)
        pygame.draw.rect(screen, (105, 65, 40), (tx-4, ty-12, 8, 12)) 
        for w, h, off in [(18, 25, 8), (14, 20, 20), (10, 15, 32)]: 
            pts = [(tx, ty-h-off), (tx-w, ty-off), (tx+w, ty-off)]
            pygame.draw.polygon(screen, (70, 120, 60), pts)
            pygame.draw.polygon(screen, (60, 50, 45), pts, 2)

    # =========================================================================
    # URUTAN RENDER (PAINTER'S ALGORITHM)
    # =========================================================================

    # 0. ALUN-ALUN & TAMAN (Plaza Base)
    draw_block(-20, -20, 0, 220, 220, 1, C_PLAZA) # Area paving keras

    # 1. BLOK A: Galeri Putih (Kiri Belakang) - (x=0..90, y=0..60)
    draw_block(0, 0, 0, 90, 60, 60, C_WHITE, glass_x=False, glass_y=False)
    # Trim Gelap Atap Blok A
    draw_block(0, 0, 60, 90, 60, 3, C_DARK)

    # 2. BLOK C: Sayap Penghubung (Kiri Depan) - (x=0..30, y=60..80)
    draw_block(0, 60, 0, 30, 20, 50, C_WHITE, glass_x=True, glass_y=False)
    # Trim Gelap Atap Blok C
    draw_block(0, 60, 50, 30, 20, 3, C_DARK)

    # 3. BLOK D: Atrium Kaca Raksasa (Tengah Depan) - (x=30..90, y=60..120)
    # Ini adalah lobi utama yang full kaca (Glass Pavilion)
    draw_block(30, 60, 0, 60, 60, 40, C_WHITE, glass_x=True, glass_y=True)
    # Trim Atap Pavilion
    draw_block(30, 60, 40, 60, 60, 3, C_WHITE)
    
    # 4. BLOK B: Menara Hitam Grafit (Kanan Belakang/Tengah) - (x=90..170, y=0..80)
    # Gedung menjulang tinggi asimetris khas museum kontemporer
    draw_block(90, 0, 0, 80, 80, 90, C_DARK, glass_x=False, glass_y=False)
    # Aksentuasi Fins (Sirip) Arsitektural Putih di sisi Kanan
    draw_block(168, 10, 0, 4, 10, 90, C_WHITE)
    draw_block(168, 30, 0, 4, 10, 90, C_WHITE)
    draw_block(168, 50, 0, 4, 10, 90, C_WHITE)

    # 5. HALAMAN DEPAN: Kolam & Instalasi Seni (Tengah Kanan)
    # Kolam Estetik Modern di depan pavilion kaca
    draw_block(30, 130, 0, 60, 40, 2, C_WHITE) # Rim Kolam
    draw_block(32, 132, 2, 56, 36, 1, C_WATER) # Air Kolam
    
    # Monumen Seni Kubisme (Emas)
    draw_block(55, 145, 2, 10, 10, 15, C_DARK) # Pedestal Hitam
    draw_block(52, 142, 17, 16, 16, 16, C_GOLD) # Kubus Emas Abstrak

    # Papan Nama MUSEUM melayang di dinding Blok B (Menghadap Kanan/Depan)
    # Diposisikan tepat di tengah fasad dinding grafit (x=130, y=81)
    j_cx, j_cy = iso(130, 81, 60)
    font = pygame.font.SysFont("Arial", 22, bold=True)
    text_surf = font.render("M U S E U M", True, (255, 255, 255))
    text_surf = pygame.transform.rotate(text_surf, -26.5) # Perspektif isometrik
    text_rect = text_surf.get_rect(center=(j_cx, j_cy))
    screen.blit(text_surf, text_rect)

    # 6. TAMAN & POHON PINUS
    draw_pine_tree(-30, -10, 0)
    draw_pine_tree(-10, -20, 0)
    
    draw_pine_tree(200, -10, 0)
    draw_pine_tree(190, 20, 0)
    
    draw_pine_tree(-30, 150, 0)
    draw_pine_tree(-10, 170, 0)
    
    draw_pine_tree(180, 160, 0)
    draw_pine_tree(150, 180, 0)


class Museum:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.scale = 1.0
    def render(self, screen):
        scale = getattr(self, 'scale', 1.0)
        render_museum(screen, self.x, self.y - 234 * scale, scale=scale)
