import pygame

# --- PALET WARNA ---
C_GROUND_TOP = (160, 165, 170)
C_GROUND_L = (130, 135, 140)
C_GROUND_R = (100, 105, 110)

C_GRASS_TOP = (150, 200, 90)
C_GRASS_L = (120, 170, 70)
C_GRASS_R = (90, 140, 50)

C_TREE_L = (120, 190, 60)
C_TREE_R = (70, 140, 40)

# Warna Gedung Utama (Abu-abu terang/Putih)
C_BLDG_TOP = (245, 245, 250)
C_BLDG_L = (220, 220, 225)
C_BLDG_R = (180, 180, 190)
C_ROOF_DARK = (110, 115, 120)

# Warna Blok Bank (Biru)
C_BLUE_TOP = (30, 130, 220)
C_BLUE_L = (20, 100, 180)
C_BLUE_R = (10, 65, 140)

# Warna Kaca / Jendela (Cyan/Biru Muda)
C_GLASS_RIM = (180, 225, 245)
C_GLASS_L = (100, 170, 220)
C_GLASS_R = (60, 120, 170)

C_TEXT = (255, 255, 255)

def project(x, y, z, cx, cy, scale_x=2, scale_y=1, scale_z=2, scale=1.0):
    """Fungsi proyeksi matematika 3D ke 2D Isometrik"""
    sx = cx + (y - x) * scale_x * scale
    sy = cy + (x + y) * scale_y * scale - (z * scale_z * scale)
    return sx, sy

def draw_box(surface, cx, cy, x, y, z, dx, dy, dz, c_top, c_left, c_right, scale=1.0):
    """Fungsi untuk menggambar balok 3D (Building blocks)"""
    p = []
    for pz in (z, z+dz):
        for px, py in [(x, y), (x+dx, y), (x+dx, y+dy), (x, y+dy)]:
            p.append(project(px, py, pz, cx, cy, scale=scale))
            
    left_face = [p[1], p[2], p[6], p[5]]   # Menghadap kiri bawah
    right_face = [p[3], p[2], p[6], p[7]]  # Menghadap kanan bawah
    top_face = [p[4], p[5], p[6], p[7]]    # Menghadap atas

    if dz > 0:
        if dy > 0: pygame.draw.polygon(surface, c_left, left_face)
        if dx > 0: pygame.draw.polygon(surface, c_right, right_face)
    if dx > 0 and dy > 0:
        pygame.draw.polygon(surface, c_top, top_face)


def draw_path_right(surface, cx, cy, points_xz, y_face, color, thickness=2, scale=1.0):
    """Fungsi untuk menggambar teks/garis di sisi tembok kanan"""
    proj_points = [project(x, y_face, z, cx, cy, scale=scale) for x, z in points_xz]
    pygame.draw.lines(surface, color, False, proj_points, max(1, int(thickness * scale)))

def draw_tree(surface, cx, cy, x, y, z, h=18, r=7, scale=1.0):
    """Fungsi untuk menggambar pohon berbentuk kerucut 3D"""
    bc = project(x, y, z, cx, cy, scale=scale)
    tip = project(x, y, z+h, cx, cy, scale=scale)
    scaled_r = r * scale
    left = (bc[0] - scaled_r*2, bc[1] - scaled_r*0.2)
    right = (bc[0] + scaled_r*2, bc[1] - scaled_r*0.2)
    
    pygame.draw.polygon(surface, C_TREE_L, [tip, left, bc])
    pygame.draw.polygon(surface, C_TREE_R, [tip, bc, right])

def draw_bank(screen, cx, cy, scale=1.0):
    # 1. Base Ground (Lantai Hitam/Abu)
    draw_box(screen, cx, cy, -15, -15, -2, 110, 150, 2, C_GROUND_TOP, C_GROUND_L, C_GROUND_R, scale=scale)
    
    # 2. Rumput Kanan & Kiri
    draw_box(screen, cx, cy, 0, 112, 0, 40, 18, 1, C_GRASS_TOP, C_GRASS_L, C_GRASS_R, scale=scale)
    draw_box(screen, cx, cy, 72, 0, 0, 18, 80, 1, C_GRASS_TOP, C_GRASS_L, C_GRASS_R, scale=scale)

    # 4. Gedung Utama (Abu-abu)
    draw_box(screen, cx, cy, 0, 0, 0, 70, 110, 50, C_BLDG_TOP, C_BLDG_L, C_BLDG_R, scale=scale)
    draw_box(screen, cx, cy, 2, 2, 49.8, 66, 106, 0.3, C_ROOF_DARK, C_ROOF_DARK, C_ROOF_DARK, scale=scale) # Atap dalam

    # 5. Unit AC di Atap
    draw_box(screen, cx, cy, 15, 20, 50, 15, 20, 5, C_BLDG_TOP, C_BLDG_L, C_BLDG_R, scale=scale)
    draw_box(screen, cx, cy, 40, 20, 50, 15, 20, 5, C_BLDG_TOP, C_BLDG_L, C_BLDG_R, scale=scale)
    draw_box(screen, cx, cy, 16, 65, 50, 4, 5, 3, C_BLDG_TOP, C_BLDG_L, C_BLDG_R, scale=scale)
    draw_box(screen, cx, cy, 21, 65, 50, 4, 5, 3, C_BLDG_TOP, C_BLDG_L, C_BLDG_R, scale=scale)
    draw_box(screen, cx, cy, 26, 65, 50, 4, 5, 3, C_BLDG_TOP, C_BLDG_L, C_BLDG_R, scale=scale)

    # 6. Jendela Dinding Kiri (3 Kolom)
    for y_pos in [10, 32, 54]:
        draw_box(screen, cx, cy, 70, y_pos, 5, 0.5, 12, 15, C_GLASS_RIM, C_GLASS_L, C_GLASS_RIM, scale=scale)
        draw_box(screen, cx, cy, 70, y_pos, 25, 0.5, 12, 15, C_GLASS_RIM, C_GLASS_L, C_GLASS_RIM, scale=scale)

    # 7. Jendela Dinding Kanan (1 Kolom)
    draw_box(screen, cx, cy, 15, 110, 5, 12, 0.5, 15, C_GLASS_RIM, C_GLASS_RIM, C_GLASS_R, scale=scale)
    draw_box(screen, cx, cy, 15, 110, 25, 12, 0.5, 15, C_GLASS_RIM, C_GLASS_RIM, C_GLASS_R, scale=scale)

    # 8. Tangga Kecil & Blok Biru (Bank)
    draw_box(screen, cx, cy, 38, 78, -1, 44, 44, 1, C_GROUND_TOP, C_GROUND_L, C_GROUND_R, scale=scale)
    draw_box(screen, cx, cy, 40, 80, 0, 40, 40, 65, C_BLUE_TOP, C_BLUE_L, C_BLUE_R, scale=scale)
    draw_box(screen, cx, cy, 42, 82, 64.8, 36, 36, 0.3, C_BLUE_R, C_BLUE_R, C_BLUE_R, scale=scale) # Atap biru dalam

    # 9. Pintu Kaca di Blok Biru (Menghadap Kiri)
    draw_box(screen, cx, cy, 80, 92, 0, 0.5, 7.5, 20, C_GLASS_RIM, C_GLASS_L, C_GLASS_RIM, scale=scale)
    draw_box(screen, cx, cy, 80, 100.5, 0, 0.5, 7.5, 20, C_GLASS_RIM, C_GLASS_L, C_GLASS_RIM, scale=scale)

    # 10. Mesin ATM di Blok Biru (Menghadap Kanan)
    for x_pos in [48, 60]:
        draw_box(screen, cx, cy, x_pos, 120, 5, 7, 0.5, 10, C_GROUND_TOP, C_GROUND_L, C_GROUND_R, scale=scale)
        draw_box(screen, cx, cy, x_pos+1, 120.5, 9, 5, 0.2, 4, C_GLASS_RIM, C_GLASS_RIM, C_GLASS_R, scale=scale) # Layar

    # 11. Teks "BANK" 3D Isometrik di Blok Biru
    text_y = 120.1
    # B
    draw_path_right(screen, cx, cy, [(75,45), (75,55), (72,55), (71,53), (75,50), (71,48), (71,45), (75,45)], text_y, C_TEXT, scale=scale)
    # A
    draw_path_right(screen, cx, cy, [(68,45), (66,55), (64,45)], text_y, C_TEXT, scale=scale)
    draw_path_right(screen, cx, cy, [(67,50), (65,50)], text_y, C_TEXT, scale=scale)
    # N
    draw_path_right(screen, cx, cy, [(61,45), (61,55), (57,45), (57,55)], text_y, C_TEXT, scale=scale)
    # K
    draw_path_right(screen, cx, cy, [(54,45), (54,55)], text_y, C_TEXT, scale=scale)
    draw_path_right(screen, cx, cy, [(54,50), (50,55)], text_y, C_TEXT, scale=scale)
    draw_path_right(screen, cx, cy, [(54,50), (50,45)], text_y, C_TEXT, scale=scale)

    # 12. Pohon di Kiri (Depan)
    draw_tree(screen, cx, cy, 81, 15, 1, scale=scale)
    draw_tree(screen, cx, cy, 81, 40, 1, scale=scale)
    draw_tree(screen, cx, cy, 81, 65, 1, scale=scale)

    # 13. Pohon di Kanan
    draw_tree(screen, cx, cy, 15, 121, 1, scale=scale)
    draw_tree(screen, cx, cy, 32, 121, 1, scale=scale)
