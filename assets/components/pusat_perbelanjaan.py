import pygame
import sys

def iso(x, y, z, cx, cy, s):
    """Fungsi Engine Proyeksi 3D ke Layar 2D Isometrik (Rasio 2:1)"""
    screen_x = cx + (x - y) * 2 * s
    screen_y = cy + (x + y) * 1 * s - z * 2 * s
    return screen_x, screen_y

def draw_block(screen, cx, cy, s, x, y, z, w, d, h, color, glass_x=False, glass_y=False):
    """
    Fungsi super untuk menggambar balok 3D padat (Tembok/Lantai).
    Bisa otomatis merender kaca berjendela jika glass_x atau glass_y = True.
    """
    # Kalkulasi Pencahayaan (Lighting)
    c_top = (min(255, color[0]+25), min(255, color[1]+25), min(255, color[2]+25)) # Paling terang
    c_x = color  # Sisi kanan (Normal)
    c_y = (max(0, color[0]-35), max(0, color[1]-35), max(0, color[2]-35))         # Sisi kiri (Bayangan)
    c_line = (max(0, color[0]-75), max(0, color[1]-75), max(0, color[2]-75))      # Garis Outline
    
    # Titik-titik poligon 3D
    p_top = [iso(x,y,z+h, cx,cy,s), iso(x+w,y,z+h, cx,cy,s), iso(x+w,y+d,z+h, cx,cy,s), iso(x,y+d,z+h, cx,cy,s)]
    p_x = [iso(x+w,y,z, cx,cy,s), iso(x+w,y+d,z, cx,cy,s), iso(x+w,y+d,z+h, cx,cy,s), iso(x+w,y,z+h, cx,cy,s)]
    p_y = [iso(x,y+d,z, cx,cy,s), iso(x+w,y+d,z, cx,cy,s), iso(x+w,y+d,z+h, cx,cy,s), iso(x,y+d,z+h, cx,cy,s)]
    
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

    # 3. Gambar Dekorasi Kaca Mall (Mullions)
    g_c = (130, 200, 245)   # Warna Kaca
    gl_c = (70, 140, 190)   # Warna Rangka Kaca
    ins = 4                 # Inset (Jarak kaca dari pinggir tembok)
    
    if glass_x and d > 2*ins and h > 2*ins:
        # Kaca menghadap sisi kanan
        gx_pts = [iso(x+w, y+ins, z+ins, cx,cy,s), iso(x+w, y+d-ins, z+ins, cx,cy,s), 
                  iso(x+w, y+d-ins, z+h-ins, cx,cy,s), iso(x+w, y+ins, z+h-ins, cx,cy,s)]
        pygame.draw.polygon(screen, g_c, gx_pts)
        pygame.draw.lines(screen, gl_c, True, gx_pts, thick)
        # Garis Grid Kaca
        for i in range(1, 4):
            yi = y + ins + (d - 2*ins) * (i/4.0)
            pygame.draw.line(screen, gl_c, iso(x+w, yi, z+ins, cx,cy,s), iso(x+w, yi, z+h-ins, cx,cy,s), thick)
        for i in range(1, 3):
            zi = z + ins + (h - 2*ins) * (i/3.0)
            pygame.draw.line(screen, gl_c, iso(x+w, y+ins, zi, cx,cy,s), iso(x+w, y+d-ins, zi, cx,cy,s), thick)
            
    if glass_y and w > 2*ins and h > 2*ins:
        # Kaca menghadap sisi kiri
        gy_pts = [iso(x+ins, y+d, z+ins, cx,cy,s), iso(x+w-ins, y+d, z+ins, cx,cy,s), 
                  iso(x+w-ins, y+d, z+h-ins, cx,cy,s), iso(x+ins, y+d, z+h-ins, cx,cy,s)]
        pygame.draw.polygon(screen, g_c, gy_pts)
        pygame.draw.lines(screen, gl_c, True, gy_pts, thick)
        # Garis Grid Kaca
        for i in range(1, 4):
            xi = x + ins + (w - 2*ins) * (i/4.0)
            pygame.draw.line(screen, gl_c, iso(xi, y+d, z+ins, cx,cy,s), iso(xi, y+d, z+h-ins, cx,cy,s), thick)
        for i in range(1, 3):
            zi = z + ins + (h - 2*ins) * (i/3.0)
            pygame.draw.line(screen, gl_c, iso(x+ins, y+d, zi, cx,cy,s), iso(x+w-ins, y+d, zi, cx,cy,s), thick)



def draw_pusat_perbelanjaan(screen, cx, cy, width=800, height=600, scale=1.0):
    """Fungsi utama merender seluruh Mall, diurutkan lapis demi lapis (Z-Sorting)"""
    s = 1.2 * scale         # Skala Global
    cy = cy - 80 * scale    # Menaikkan jangkar agar pas di tengah layar

    C_ROAD = (105, 110, 115)
    C_PLAZA = (220, 220, 225)
    C_BLDG = (245, 235, 225) # Krem hangat

    # ================= 1. LANTAI DASAR & JALAN =================
    draw_block(screen, cx, cy, s, 0, 0, 0, 180, 180, 1, C_ROAD)
    # Garis Parkir (Cat Putih)
    for i in range(10, 170, 20):
        draw_block(screen, cx, cy, s, 155, i, 1, 25, 2, 0, (230, 230, 235))
        
    # ================= 2. PLAZA (Tempat Jalan Kaki) =================
    draw_block(screen, cx, cy, s, 10, 10, 1, 140, 140, 2, C_PLAZA)
    # Garis Ubin/Keramik Plaza
    for i in range(25, 150, 20):
        pygame.draw.line(screen, (200, 200, 205), iso(i, 10, 3, cx, cy, s), iso(i, 150, 3, cx, cy, s), 1)
        pygame.draw.line(screen, (200, 200, 205), iso(10, i, 3, cx, cy, s), iso(150, i, 3, cx, cy, s), 1)

    # ================= 3. SAYAP KANAN (Background Kanan) =================
    draw_block(screen, cx, cy, s, 80, 30, 3, 70, 50, 40, C_BLDG, glass_x=True, glass_y=True)
    draw_block(screen, cx, cy, s, 90, 40, 43, 6, 6, 4, (170, 175, 180)) # AC Atap

    # ================= 4. SAYAP KIRI (Background Kiri) =================
    draw_block(screen, cx, cy, s, 30, 80, 3, 50, 70, 40, C_BLDG, glass_x=True, glass_y=True)
    draw_block(screen, cx, cy, s, 50, 135, 43, 6, 6, 2, (180, 90, 80)) # Meja Kafe Atap
    draw_block(screen, cx, cy, s, 65, 115, 43, 6, 6, 2, (80, 150, 90)) # Meja Kafe Atap
    draw_block(screen, cx, cy, s, 40, 90, 43, 8, 6, 4, (170, 175, 180)) # AC Atap

    # ================= 5. TOWER TENGAH UTAMA =================
    draw_block(screen, cx, cy, s, 70, 70, 3, 50, 50, 55, (255, 245, 230), glass_x=True, glass_y=True)
    
    # Atap Kaca Melengkung (Skylight Dome) - Dibuat bertingkat
    draw_block(screen, cx, cy, s, 80, 80, 58, 30, 30, 4, (130, 190, 230))
    draw_block(screen, cx, cy, s, 85, 85, 62, 20, 20, 4, (150, 210, 245))
    draw_block(screen, cx, cy, s, 90, 90, 66, 10, 10, 3, (170, 230, 255))
    
    # Kanopi Melayang di Depan Pintu Masuk
    draw_block(screen, cx, cy, s, 80, 120, 15, 30, 15, 3, (210, 215, 220)) # Sisi Kiri
    draw_block(screen, cx, cy, s, 120, 80, 15, 15, 30, 3, (210, 215, 220)) # Sisi Kanan

    # ================= 6. PAPAN REKLAME / SIGNAGE =================
    # Menyisakan 1 Papan di posisi yang bagus (di tengah atap)
    draw_block(screen, cx, cy, s, 90, 115, 60, 25, 2, 12, (220, 40, 50))
    
    # Menambahkan tulisan MALL di papan tersebut
    try:
        if not hasattr(draw_pusat_perbelanjaan, "font"):
            draw_pusat_perbelanjaan.font = pygame.font.SysFont("Arial", int(18 * s), bold=True)
        text_surf = draw_pusat_perbelanjaan.font.render("MALL", True, (255, 255, 255))
        # Rotasi mengikuti grid isometrik (garis ke kanan bawah)
        text_surf = pygame.transform.rotate(text_surf, -26.5)
        # Koordinat layar dari tengah permukaan depan papan reklame
        text_x, text_y = iso(102.5, 117, 66, cx, cy, s)
        text_rect = text_surf.get_rect(center=(text_x, text_y))
        screen.blit(text_surf, text_rect)
    except Exception as e:
        pass

    # ================= 7. DETAIL LINGKUNGAN DEPAN (Draw Terakhir) =================
    # Parkiran Mobil
    def _draw_car(x, y, z, color):
        draw_block(screen, cx, cy, s, x+1, y-1, z, 3, 1, 2, (30, 30, 30))
        draw_block(screen, cx, cy, s, x+10, y-1, z, 3, 1, 2, (30, 30, 30))
        draw_block(screen, cx, cy, s, x, y, z, 14, 8, 4, color)
        draw_block(screen, cx, cy, s, x+2, y+1, z+4, 8, 6, 3, (200, 220, 235))
        draw_block(screen, cx, cy, s, x+1, y+8, z, 3, 1, 2, (30, 30, 30))
        draw_block(screen, cx, cy, s, x+10, y+8, z, 3, 1, 2, (30, 30, 30))

    _draw_car(160, 30, 3, (200, 40, 50))   # Mobil Merah
    _draw_car(160, 70, 3, (50, 100, 200))  # Mobil Biru
    _draw_car(160, 110, 3, (200, 200, 210)) # Mobil Putih
