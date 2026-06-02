import pygame
import sys

# --- PENGATURAN SKALA & PROYEKSI 3D ISOMETRIK ---
SCALE = 1.3

def to_iso(x, y, z, ox, oy):
    """Mengubah koordinat 3D (x,y,z) menjadi koordinat 2D Isometrik menyamping (rasio 2:1)"""
    ix = ox + (x - z) * 2 * SCALE
    iy = oy + (x + z) * 1 * SCALE - y * 2 * SCALE
    return (ix, iy)

def draw_polygon_iso(screen, color, points, ox, oy):
    """Menggambar poligon berdasarkan titik koordinat 3D"""
    iso_points = [to_iso(px, py, pz, ox, oy) for (px, py, pz) in points]
    pygame.draw.polygon(screen, color, iso_points)

def draw_base_block(screen, x, y, z, w, h, d, ox, oy, c_top, c_left, c_right):
    """Menggambar blok 3D padat (Digunakan untuk pulau tanah dan tiang pelantar)"""
    p_top = [(x, y+h, z), (x+w, y+h, z), (x+w, y+h, z+d), (x, y+h, z+d)]
    p_left = [(x, y, z+d), (x+w, y, z+d), (x+w, y+h, z+d), (x, y+h, z+d)]
    p_right = [(x+w, y, z), (x+w, y, z+d), (x+w, y+h, z+d), (x+w, y+h, z)]
    draw_polygon_iso(screen, c_left, p_left, ox, oy)
    draw_polygon_iso(screen, c_right, p_right, ox, oy)
    draw_polygon_iso(screen, c_top, p_top, ox, oy)


# --- STRUKTUR VEGETASI & BATU ALAM (BEBAS DARI MATH) ---

def draw_round_stone(screen, x, y, z, r, h, ox, oy, base_color):
    """Menggambar batu bulat alami dengan rumus kuadratis murni (Tanpa math.sqrt)"""
    for i in range(int(h)):
        curr_y = y + i
        pct = float(i) / h
        r_curr = r * (1.0 - 0.25 * pct * pct) # Efek lengkung halus kubah alami
        ix, iy = to_iso(x, curr_y, z, ox, oy)
        
        rc = min(255, int(base_color[0] + pct * 30))
        gc = min(255, int(base_color[1] + pct * 30))
        bc = min(255, int(base_color[2] + pct * 30))
        
        width = int(r_curr * 4 * SCALE)
        height = int(r_curr * 2 * SCALE)
        pygame.draw.ellipse(screen, (rc, gc, bc), (ix - width // 2, iy - height // 2, width, height))

def draw_tree(screen, x, y, z, ox, oy):
    """Menggambar pohon lebat pembatas luar danau"""
    ix, iy = to_iso(x, y, z, ox, oy)
    pygame.draw.rect(screen, (85, 55, 35), (ix - int(2*SCALE), iy - int(16*SCALE), int(4*SCALE), int(16*SCALE))) 
    pygame.draw.circle(screen, (55, 115, 45), (ix, iy - int(22*SCALE)), int(14*SCALE))    
    pygame.draw.circle(screen, (65, 130, 55), (ix - int(8*SCALE), iy - int(15*SCALE)), int(10*SCALE))  
    pygame.draw.circle(screen, (45, 100, 35), (ix + int(8*SCALE), iy - int(15*SCALE)), int(10*SCALE))  
    pygame.draw.circle(screen, (85, 155, 65), (ix - int(3*SCALE), iy - int(25*SCALE)), int(7*SCALE))   

def draw_dense_shrub(screen, x, y, z, ox, oy):
    """Menggambar semak bulat alami pengisi celah pulau"""
    ix, iy = to_iso(x, y, z, ox, oy)
    pygame.draw.circle(screen, (40, 85, 45), (ix, iy - 2), int(10 * SCALE))
    pygame.draw.circle(screen, (60, 130, 65), (ix - 4, iy - 5), int(8 * SCALE))
    pygame.draw.circle(screen, (95, 175, 90), (ix + 3, iy - 8), int(6 * SCALE))


# --- STRUKTUR PELANTAR KAYU SETENGAH (DOCK/PIER) ---

def draw_pier_segment(screen, z, ox, oy):
    """Menggambar satu potongan segmen pelantar kayu menjorok dari depan (Z=140) ke tengah (Z=80)"""
    y = 4.5  # Tinggi lantai pelantar berada di atas permukaan air
    x = 76   # Titik awal lebar pelantar pada sumbu X
    w = 8    # Lebar pelantar (Merentang dari X=76 sampai X=84)
    d = 4    # Panjang langkah per segmen papan kayu
    
    # 1. TIANG PANCANG UTAMA (Hanya digambar di ujung dermaga z=80 dan pangkal tengah z=112)
    if z == 80 or z == 112:
        # Tiang Pancang Sisi Kiri
        draw_base_block(screen, x, 0, z, 1.5, y, 1.5, ox, oy, (90, 65, 35), (70, 50, 25), (55, 40, 20))
        # Tiang Pancang Sisi Kanan
        draw_base_block(screen, x + w - 1.5, 0, z, 1.5, y, 1.5, ox, oy, (90, 65, 35), (70, 50, 25), (55, 40, 20))

    # 2. PAPAN LANTAI UTAMA (Top Face) - Warna kayu cokelat dermaga alami
    p_top = [(x, y, z), (x + w, y, z), (x + w, y, z + d), (x, y, z + d)]
    draw_polygon_iso(screen, (145, 100, 60), p_top, ox, oy)
    
    # 3. KETEBALAN TEPI PAPAN KANAN (Facing Front-Right Camera)
    p_side_r = [(x + w, y, z), (x + w, y, z + d), (x + w, y - 1.2, z + d), (x + w, y - 1.2, z)]
    draw_polygon_iso(screen, (110, 75, 40), p_side_r, ox, oy)

    # 4. PAGAR PEMBATAS TEPI (Kiri & Kanan) - Sengaja dikosongkan pada ujung depan z=80 agar realistis
    # Pagar Samping Kiri
    p_rail_l = [(x, y + 4, z), (x, y + 4, z + d), (x, y + 3.2, z + d), (x, y + 3.2, z)]
    draw_polygon_iso(screen, (120, 85, 45), p_rail_l, ox, oy)
    
    # Pagar Samping Kanan
    p_rail_r = [(x + w, y + 4, z), (x + w, y + 4, z + d), (x + w, y + 3.2, z + d), (x + w, y + 3.2, z)]
    draw_polygon_iso(screen, (160, 115, 70), p_rail_r, ox, oy)

    # TIANG PAGAR KECIL VERTIKAL (Muncul secara berkala setiap kelipatan jarak Z tertentu)
    if z % 16 == 0:
        # Tiang Pagar Kiri
        draw_base_block(screen, x, y, z, 0.8, 4, 0.8, ox, oy, (100, 70, 35), (80, 55, 25), (65, 45, 20))
        # Tiang Pagar Kanan
        draw_base_block(screen, x + w - 0.8, y, z, 0.8, 4, 0.8, ox, oy, (130, 95, 50), (105, 75, 35), (90, 60, 30))


# --- FUNGSI UTAMA RENDERING LINGKUNGAN DANAU ---
def draw_danau(screen, ox, oy):
    # Palet Elemen Lingkungan Tanah & Rumput
    C_BASE_TOP, C_BASE_LEFT, C_BASE_RIGHT = (240, 242, 245), (212, 216, 220), (178, 182, 186)
    C_GRASS_TOP, C_GRASS_LEFT, C_GRASS_RIGHT = (160, 200, 125), (130, 165, 100), (100, 130, 75)
    
    # Palet Air Danau Penuh
    C_WATER_BODY = (120, 205, 240)      
    C_WATER_GLOW = (155, 225, 255)      
    C_RIPPLE = (205, 242, 255)          

    # 1. LANDASAN UTAMA PULAU
    draw_base_block(screen, 0, -4, 0, 160, 4, 160, ox, oy, C_BASE_TOP, C_BASE_LEFT, C_BASE_RIGHT)
    draw_base_block(screen, 4, 0, 4, 152, 2, 152, ox, oy, C_GRASS_TOP, C_GRASS_LEFT, C_GRASS_RIGHT)

    # 2. PERMUKAAN AIR DANAU YANG PENUH SEBATAS BARISAN POHON
    water_full_curve = [
        (22, 2, 25), (45, 2, 18), (75, 2, 15), (110, 2, 18), (138, 2, 25),
        (145, 2, 45), (148, 2, 75), (145, 2, 110), (138, 2, 138),
        (115, 2, 145), (80, 2, 148), (45, 2, 145), (22, 2, 138),
        (15, 2, 110), (12, 2, 75), (15, 2, 45)
    ]
    draw_polygon_iso(screen, C_WATER_BODY, water_full_curve, ox, oy)

    # Gradasi kilau permukaan air tengah
    water_glow_curve = [
        (32, 2, 35), (55, 2, 28), (75, 2, 25), (105, 2, 28), (128, 2, 35),
        (135, 2, 48), (138, 2, 75), (135, 2, 102), (128, 2, 128),
        (105, 2, 135), (80, 2, 138), (55, 2, 135), (32, 2, 128),
        (25, 2, 102), (22, 2, 75), (25, 2, 48)
    ]
    draw_polygon_iso(screen, C_WATER_GLOW, water_glow_curve, ox, oy)

    # Efek Guratan Riak Air Statis Halus
    ripples = [(45, 40, 16, 8), (115, 45, 20, 10), (40, 115, 14, 7), (110, 120, 18, 9)]
    for rx, rz, rw, rh in ripples:
        ix_r, iy_r = to_iso(rx, 2, rz, ox, oy)
        pygame.draw.ellipse(screen, C_RIPPLE, (ix_r - int(rw*SCALE), iy_r - int(rh*SCALE), int(rw*2*SCALE), int(rh*2*SCALE)), 1)

    # 3. ANTRIAN PROSES RENDERING OBJEK DENGAN DEPTH SORTING (X + Z)
    render_queue = []

    # A. Susunan Pohon Lindung Tepi Pulau (Tetap Dipertahankan)
    tree_positions = [
        (12, 2, 15), (35, 2, 10), (60, 2, 8), (85, 2, 8), (110, 2, 10), (135, 2, 15), (150, 2, 35),
        (10, 2, 40), (152, 2, 65), (8, 2, 70), (150, 2, 95), (10, 2, 100), (148, 2, 125),
        (15, 2, 135), (40, 2, 145), (65, 2, 150), (90, 2, 150), (115, 2, 145), (140, 2, 135)
    ]
    for tx, ty, tz in tree_positions:
        render_queue.append(('tree', tx, ty, tz))

    # B. Batu Kali Bulat Pembatas Pinggiran Air
    rock_col = (190, 195, 200)
    for px, py, pz in water_full_curve:
        render_queue.append(('rock', px, py, pz, 6, 6, rock_col))

    # C. Semak-Semak Alami Pengisi Celah Komponen Tepi Pulau
    shrub_positions = [
        (22, 2, 12), (48, 2, 8), (72, 2, 6), (98, 2, 7), (122, 2, 9), (145, 2, 22),
        (6, 2, 55), (154, 2, 50), (5, 2, 85), (153, 2, 110),
        (28, 2, 148), (52, 2, 152), (78, 2, 154), (102, 2, 152), (128, 2, 146)
    ]
    for sx, sy, sz in shrub_positions:
        render_queue.append(('shrub', sx, sy, sz))

    # D. MENYIAPKAN SEGMEN PELANTAR SETENGAH (Menjorok dari pantai depan Z=140 mundur ke tengah Z=80 pada X=80)
    for bz in range(80, 144, 4):
        # Disimpan ke dalam antrian per bagian kecil agar disortir presisi bersama lingkungan sekitar
        render_queue.append(('pier', 80, 2, bz))

    # --- EKSEKUSI URUTAN RENDERING SESUAI KEDALAMAN PERSPEKTIF ISOMETRIK (Back-to-Front) ---
    render_queue.sort(key=lambda obj: obj[1] + obj[3]) 

    for obj in render_queue:
        otype = obj[0]
        cx, cy, cz = obj[1], obj[2], obj[3]
        
        if otype == 'tree':
            draw_tree(screen, cx, cy, cz, ox, oy)
        elif otype == 'shrub':
            draw_dense_shrub(screen, cx, cy, cz, ox, oy)
        elif otype == 'rock':
            rad, hgt, b_col = obj[4], obj[5], obj[6]
            draw_round_stone(screen, cx, cy, cz, rad, hgt, ox, oy, b_col)
        elif otype == 'pier':
            draw_pier_segment(screen, cz, ox, oy)
