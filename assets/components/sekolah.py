import pygame
import math

# Palet Warna Sekolah Modern
C_BASE = (245, 245, 240)
C_WALL = (250, 248, 245) # Putih tulang
C_ACCENT = (210, 80, 50) # Bata / Oranye
C_ROOF = (200, 205, 210) # Atap abu muda
C_GRASS = (130, 200, 100)
C_COURT_BLUE = (70, 120, 180) # Lapangan olahraga biru
C_COURT_RED = (180, 80, 80) # Lapangan olahraga merah bata
C_LINE = (240, 250, 255)

def render_sekolah(screen, cx, cy, scale=1.0):
    # Skala Global Sekolah
    s = 1.6 * scale

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

        # 3. Kaca Bangunan
        g_c = (150, 220, 255)
        gl_c = (100, 160, 200)
        ins = 2
        
        if glass_x and d > 2*ins and h > 2*ins:
            gx_pts = [iso(x+w, y+ins, z+ins), iso(x+w, y+d-ins, z+ins), 
                      iso(x+w, y+d-ins, z+h-ins), iso(x+w, y+ins, z+h-ins)]
            pygame.draw.polygon(screen, g_c, gx_pts)
            pygame.draw.lines(screen, gl_c, True, gx_pts, thick)
            for i in range(1, max(2, int(d/8))):
                yi = y + ins + (d - 2*ins) * (i/int(d/8))
                pygame.draw.line(screen, gl_c, iso(x+w, yi, z+ins), iso(x+w, yi, z+h-ins), thick)
            for i in range(1, max(2, int(h/12))):
                zi = z + ins + (h - 2*ins) * (i/int(h/12))
                pygame.draw.line(screen, gl_c, iso(x+w, y+ins, zi), iso(x+w, y+d-ins, zi), thick)
                
        if glass_y and w > 2*ins and h > 2*ins:
            gy_pts = [iso(x+ins, y+d, z+ins), iso(x+w-ins, y+d, z+ins), 
                      iso(x+w-ins, y+d, z+h-ins), iso(x+ins, y+d, z+h-ins)]
            pygame.draw.polygon(screen, g_c, gy_pts)
            pygame.draw.lines(screen, gl_c, True, gy_pts, thick)
            for i in range(1, max(2, int(w/8))):
                xi = x + ins + (w - 2*ins) * (i/int(w/8))
                pygame.draw.line(screen, gl_c, iso(xi, y+d, z+ins), iso(xi, y+d, z+h-ins), thick)
            for i in range(1, max(2, int(h/12))):
                zi = z + ins + (h - 2*ins) * (i/int(h/12))
                pygame.draw.line(screen, gl_c, iso(x+ins, y+d, zi), iso(x+w-ins, y+d, zi), thick)



    def draw_court(cx_crt, cy_crt, w_crt, d_crt, color, line_color):
        """Menggambar lapangan olahraga beserta markahnya"""
        draw_block(cx_crt, cy_crt, 3, w_crt, d_crt, 0.5, color)
        pts = [iso(cx_crt+2, cy_crt+2, 3.6), iso(cx_crt+w_crt-2, cy_crt+2, 3.6), 
               iso(cx_crt+w_crt-2, cy_crt+d_crt-2, 3.6), iso(cx_crt+2, cy_crt+d_crt-2, 3.6)]
        pygame.draw.lines(screen, line_color, True, pts, 2)
        pygame.draw.line(screen, line_color, iso(cx_crt+w_crt/2, cy_crt+2, 3.6), iso(cx_crt+w_crt/2, cy_crt+d_crt-2, 3.6), 2)
        mid_pt = iso(cx_crt+w_crt/2, cy_crt+d_crt/2, 3.6)
        pygame.draw.ellipse(screen, line_color, (mid_pt[0]-10, mid_pt[1]-5, 20, 10), 2)

    def draw_tree_s(x, y, z):
        """Menggambar pohon simpel"""
        base = iso(x, y, z)
        top = iso(x, y, z+12)
        pygame.draw.line(screen, (100, 70, 40), base, top, 4)
        pygame.draw.circle(screen, (80, 160, 60), (int(top[0]), int(top[1])), 12)
        pygame.draw.circle(screen, (100, 190, 80), (int(top[0]-3), int(top[1]-5)), 8)

    # 1. HALAMAN RUMPUT
    draw_block(0, 0, 0, 120, 240, 2, C_GRASS)

    # 2. PAVING & HALAMAN DEPAN
    draw_block(40, 20, 2, 80, 200, 1, C_BASE)
    
    # 3. LAPANGAN OLAHRAGA
    draw_court(60, 30, 40, 60, C_COURT_BLUE, C_LINE)
    draw_court(60, 150, 40, 60, C_COURT_RED, C_LINE)

    # 4. TIANG BENDERA
    tiang_base = iso(100, 120, 3)
    tiang_top = iso(100, 120, 40)
    pygame.draw.line(screen, (220, 220, 220), tiang_base, tiang_top, 3)
    # Bendera Merah Putih
    flag_red = [tiang_top, iso(100, 130, 40), iso(100, 130, 35), iso(100, 120, 35)]
    pygame.draw.polygon(screen, (220, 50, 50), flag_red)
    flag_white = [iso(100, 120, 35), iso(100, 130, 35), iso(100, 130, 30), iso(100, 120, 30)]
    pygame.draw.polygon(screen, (250, 250, 250), flag_white)

    # 5. BANGUNAN SEKOLAH

    # Pohon Belakang (y=10)
    for px in [10, 30, 50, 70, 90, 110]:
        draw_tree_s(px, 10, 2)

    # --- SAYAP KIRI (Kelas, Y=20..100) ---
    draw_block(10, 20, 3, 30, 80, 15, C_WALL, glass_x=True)
    draw_block(10, 20, 18, 30, 80, 15, C_ACCENT, glass_x=True)
    draw_block(8, 18, 33, 34, 84, 2, C_ROOF) # Atap Sayap Kiri

    # --- MAIN LOBBY (Tengah, Y=100..140) ---
    draw_block(10, 100, 3, 40, 40, 20, C_WALL, glass_x=True, glass_y=True)
    draw_block(10, 100, 23, 40, 40, 20, C_ACCENT, glass_x=True, glass_y=True)
    # Pilar masuk
    draw_block(48, 110, 3, 6, 20, 12, C_WALL)
    # Kanopi Pintu Utama
    draw_block(45, 108, 15, 10, 24, 2, C_ROOF)
    # Atap Main Lobby
    draw_block(8, 98, 43, 44, 44, 3, C_ROOF)
    # Toren/Menara Logo Sekolah di Atas
    draw_block(15, 105, 46, 30, 30, 8, C_ACCENT)
    
    # Render text SCHOOL menempel di sisi balok merah (Right-Front face)
    try:
        font = pygame.font.SysFont("arial", 13, bold=True)
        text_surf = font.render("S C H O O L", True, (255, 255, 255))
        
        # Rotasi +26.565 derajat agar sejajar dengan kemiringan isometrik
        # Wajah kanan-depan (x=45) miring ke atas-kanan di layar
        rotated_text = pygame.transform.rotate(text_surf, 26.565)
        
        # Pusat wajah kanan-depan: x=45 (tepi kanan), y=120 (tengah dari 105..135), z=50 (tengah dari 46..54)
        txt_pos = iso(45, 120, 50)
        text_rect = rotated_text.get_rect(center=(txt_pos[0], txt_pos[1]))
        
        screen.blit(rotated_text, text_rect)
    except Exception as e:
        print("Error render text SCHOOL:", e)

    # --- SAYAP KANAN (Kelas, Y=140..220) ---
    draw_block(10, 140, 3, 30, 80, 15, C_WALL, glass_x=True)
    draw_block(10, 140, 18, 30, 80, 15, C_ACCENT, glass_x=True)
    draw_block(8, 138, 33, 34, 84, 2, C_ROOF) # Atap Sayap Kanan

    # Pohon Depan (y=230) - Digambar terakhir agar menimpa bangunan di belakangnya
    for px in [10, 30, 50, 70, 90, 110]:
        draw_tree_s(px, 230, 2)

class Sekolah:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.scale = 1.0
    def render(self, screen):
        scale = getattr(self, 'scale', 1.0)
        render_sekolah(screen, self.x + 192 * scale, self.y - 288 * scale, scale=scale)
