import pygame
import math

# Palet Warna Town Hall Modern
C_WHITE = (245, 245, 250)      # Beton Putih Bersih
C_DARK = (45, 50, 55)          # Abu-abu Gelap / Hitam Karbon
C_PLAZA = (220, 225, 230)      # Granit Alun-alun
C_GOLD = (230, 190, 60)        # Emas Aksentuasi
C_GRASS = (130, 200, 100)      # Taman Hijau
C_WATER = (90, 180, 230)       # Kolam Patung

def render_town_hall(screen, cx, cy, scale=1.0):
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
        g_c = (120, 200, 220)
        gl_c = (80, 160, 190)
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

    # =========================================================================
    # URUTAN RENDER (Berdasarkan Z-order isometrik: dari Kiri-Atas ke Kanan-Bawah)
    # 0. Alun-alun & Taman
    # 1. Sayap Kiri
    # 2. Main Building
    # 3. Kubah/Mahkota (Di Atas Main Building)
    # 4. Sayap Kanan
    # 5. Monumen Tengah Alun-alun
    # =========================================================================

    # 0. ALUN-ALUN & TAMAN (Plaza Base)
    draw_block(-60, 0, -2, 360, 280, 2, C_PLAZA)
    # Taman Rumput (Simetris)
    draw_block(-40, 160, 0, 100, 100, 1, C_GRASS) # Taman Kiri
    draw_block(180, 160, 0, 100, 100, 1, C_GRASS) # Taman Kanan

    # 1. SAYAP KIRI (x=-40..60, y=40..100)
    # Tembok Solid Lebar
    draw_block(-40, 40, 0, 100, 60, 60, C_WHITE, glass_x=False, glass_y=False)
    # Jendela Kaca (Kaca hanya di bagian tengah, sedikit menonjol ke depan Y)
    draw_block(-30, 99, 10, 80, 2, 40, C_WHITE, glass_x=False, glass_y=True)
    # Atap Sayap Kiri
    draw_block(-42, 38, 60, 104, 64, 4, C_DARK)

    # 2. BANGUNAN UTAMA SANGAT LEBAR (x=60..180, y=20..120)
    # Tembok Solid Utama
    draw_block(60, 20, 0, 120, 100, 80, C_WHITE, glass_x=False, glass_y=False)
    # Jendela Kaca Besar (Depan dan Samping)
    draw_block(70, 119, 10, 100, 2, 60, C_WHITE, glass_x=False, glass_y=True) # Kaca Kiri Depan
    draw_block(179, 30, 10, 2, 80, 60, C_WHITE, glass_x=True, glass_y=False) # Kaca Kanan Samping
    # Atap Bangunan Utama (Overhang)
    draw_block(58, 18, 80, 124, 104, 5, C_DARK)

    # Kanopi & Pintu Utama (Sangat Lebar)
    draw_block(80, 120, 0, 80, 30, 3, C_PLAZA) # Tangga Utama
    draw_block(80, 140, 3, 6, 6, 25, C_WHITE)  # Pilar Kiri
    draw_block(154, 140, 3, 6, 6, 25, C_WHITE) # Pilar Kanan
    draw_block(75, 120, 28, 90, 30, 4, C_DARK) # Atap Kanopi

    # 3. KOTA PERTEMUAN / STRUKTUR MAHKOTA (Pengganti Menara Tinggi)
    # Bangunan lebar, pendek, dan megah di atas atap utama (z=85)
    draw_block(80, 40, 85, 80, 60, 20, C_WHITE, glass_x=False, glass_y=True)
    draw_block(75, 35, 105, 90, 70, 5, C_DARK)

    # 4. SAYAP KANAN (x=180..280, y=40..100)
    # Tembok Solid Lebar
    draw_block(180, 40, 0, 100, 60, 60, C_WHITE, glass_x=False, glass_y=False)
    # Jendela Kaca
    draw_block(180, 45, 10, 2, 50, 40, C_WHITE, glass_x=True, glass_y=False) # Kaca Kanan Samping
    draw_block(190, 99, 10, 80, 2, 40, C_WHITE, glass_x=False, glass_y=True) # Kaca Kiri Depan
    # Atap Sayap Kanan
    draw_block(178, 38, 60, 104, 64, 4, C_DARK)

    # 5. MONUMEN / AIR MANCUR ALUN-ALUN (Berada di depan, Z-order paling besar)
    # Kolam Air Mancur (Center x=120, y=180)
    draw_block(100, 160, 0, 40, 40, 4, C_WHITE) # Rim Kolam
    draw_block(103, 163, 4, 34, 34, 1, C_WATER) # Air Kolam
    # Base Patung
    draw_block(115, 175, 4, 10, 10, 20, C_DARK)
    # Patung Emas Abstrak
    draw_block(112, 172, 24, 16, 16, 16, C_GOLD)



class BalaiKota:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.scale = 1.0
    def render(self, screen):
        scale = getattr(self, 'scale', 1.0)
        render_town_hall(screen, self.x + 52 * scale, self.y - 338 * scale, scale=scale)
