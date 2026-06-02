import pygame
import math

# --- ENGINE PROYEKSI MATRIKS 3D ISOMETRIK MANUAL ---
SCALE = 1.4

def to_iso(x, y, z, ox, oy):
    """Mengubah koordinat ruang 3D (X, Y, Z) menjadi koordinat bidang layar 2D"""
    ix = ox + (x - z) * 2 * SCALE
    iy = oy + (x + z) * 1 * SCALE - y * 2 * SCALE
    return (ix, iy)

def draw_wall_3d(screen, p1, p2, p3, p4, color, ox, oy, outline_color=(35, 45, 55)):
    """Menggambar poligon 3D dengan outline rapi"""
    points = [to_iso(p[0], p[1], p[2], ox, oy) for p in [p1, p2, p3, p4]]
    int_points = [(int(pt[0]), int(pt[1])) for pt in points]
    pygame.draw.polygon(screen, color, int_points)
    if outline_color:
        pygame.draw.polygon(screen, outline_color, int_points, 1)

def draw_hiu(screen, ox, oy):
    """Fungsi utama menggambar Sirip Hiu 3D emerging dengan bayangan tubuh di air"""
    
    # --- PALET WARNA HIU ---
    C_SHARK_TOP   = (130, 145, 155)     # Abu-abu punggung hiu atas
    C_SHARK_LEFT  = (100, 115, 125)     # Sisi kiri menghadap pengamat
    C_SHARK_SHAD  = (75, 85, 95)        # Sisi kanan bayangan
    C_OUTLINE     = (35, 45, 55)
    
    C_UNDERWATER  = (12, 40, 75)        # Bayangan tubuh bawah air

    # =================================================================
    # A. BAYANGAN BADAN BAWAH AIR (Y < 0)
    # Digambar di permukaan transparan
    # =================================================================
    temp_surf = pygame.Surface(screen.get_size())
    temp_surf.fill((0, 0, 0))
    temp_surf.set_colorkey((0, 0, 0))

    # Segmen Tubuh Hiu Bawah Air
    # Format: (X, Y_Bawah_Air, Z_Pusat, Lebar)
    underwater_segments = [
        (20,  -12, 40, 12),
        (50,  -22, 40, 26),
        (85,  -26, 40, 30),
        (120, -18, 40, 18),
        (145, -10, 40, 8),
        (160, -6,  40, 4)
    ]

    # Sirip Dada Samping (Pectoral Fin) bawah air
    p_pec_L = [(65, 0, 53), (82, -15, 68), (86, -13, 64), (72, 0, 51)]
    draw_wall_3d(temp_surf, p_pec_L[0], p_pec_L[1], p_pec_L[2], p_pec_L[3], C_UNDERWATER, ox, oy, outline_color=None)

    # Sirip Ekor Vertikal bawah air (Caudal Fin)
    # Lobe Atas
    draw_wall_3d(temp_surf, (160, -6, 41), (175, 10, 41), (170, -12, 41), (160, -6, 41), C_UNDERWATER, ox, oy, outline_color=None)
    # Lobe Bawah
    draw_wall_3d(temp_surf, (160, -6, 41), (170, -12, 41), (175, -28, 41), (160, -6, 41), C_UNDERWATER, ox, oy, outline_color=None)

    # Hubungkan segmen tubuh bawah air
    for i in range(len(underwater_segments) - 1):
        bx, by_bot, bz_c, bw = underwater_segments[i+1]
        fx, fy_bot, fz_c, fw = underwater_segments[i]
        
        bz_L, bz_R = bz_c + bw//2, bz_c - bw//2
        fz_L, fz_R = fz_c + fw//2, fz_c - fw//2

        # Dinding samping kiri
        draw_wall_3d(temp_surf, (bx, by_bot, bz_L), (fx, fy_bot, fz_L), (fx, 0, fz_L), (bx, 0, bz_L), C_UNDERWATER, ox, oy, outline_color=None)
        # Dinding samping kanan
        draw_wall_3d(temp_surf, (bx, 0, bz_R), (fx, 0, fz_R), (fx, fy_bot, fz_R), (bx, by_bot, bz_R), C_UNDERWATER, ox, oy, outline_color=None)
        # Atap Punggung (Top Cap pada Y = 0)
        draw_wall_3d(temp_surf, (bx, 0, bz_L), (fx, 0, fz_L), (fx, 0, fz_R), (bx, 0, bz_R), C_UNDERWATER, ox, oy, outline_color=None)
        # Perut Bawah (Bottom Cap)
        draw_wall_3d(temp_surf, (bx, by_bot, bz_L), (fx, fy_bot, fz_L), (fx, fy_bot, fz_R), (bx, by_bot, bz_R), C_UNDERWATER, ox, oy, outline_color=None)

    # Blit bayangan bawah air hiu
    temp_surf.set_alpha(100)
    screen.blit(temp_surf, (0, 0))

    # =================================================================
    # B. SIRIP PUNGGUNG DI ATAS AIR (Y > 0)
    # Sirip segitiga hiu yang menonjol dan memotong air
    # =================================================================
    # Posisi sirip punggung hiu melengkung dinamis (Z=39 ke Z=41)
    p_fin_left = [
        (75, 0, 41),
        (82, 12, 41),
        (88, 22, 41),
        (94, 32, 41),
        (92, 26, 41),
        (91, 15, 41),
        (93, 6, 41),
        (102, 0, 41),
        (90, 0, 41)
    ]
    p_fin_right = [
        (75, 0, 39),
        (82, 12, 39),
        (88, 22, 39),
        (94, 32, 39),
        (92, 26, 39),
        (91, 15, 39),
        (93, 6, 39),
        (102, 0, 39),
        (90, 0, 39)
    ]

    # 1. Sisi Kanan (Shadow) - Digambar duluan di belakang
    right_points_2d = [to_iso(p[0], p[1], p[2], ox, oy) for p in p_fin_right]
    right_points_2d_int = [(int(x), int(y)) for x, y in right_points_2d]
    pygame.draw.polygon(screen, C_SHARK_SHAD, right_points_2d_int)
    if C_OUTLINE:
        pygame.draw.polygon(screen, C_OUTLINE, right_points_2d_int, 1)

    # 2. Sisi Depan/Atas (Menghubungkan kiri dan kanan sepanjang tepi depan)
    front_nodes = [
        (75, 0),
        (82, 12),
        (88, 22),
        (94, 32)
    ]
    for j in range(len(front_nodes) - 1):
        n1 = front_nodes[j]
        n2 = front_nodes[j+1]
        draw_wall_3d(screen, (n1[0], n1[1], 41), (n2[0], n2[1], 41), (n2[0], n2[1], 39), (n1[0], n1[1], 39), C_SHARK_TOP, ox, oy, outline_color=C_OUTLINE)

    # 3. Sisi Belakang (Menghubungkan kiri dan kanan sepanjang tepi belakang)
    back_nodes = [
        (94, 32),
        (92, 26),
        (91, 15),
        (93, 6),
        (102, 0)
    ]
    for j in range(len(back_nodes) - 1):
        n1 = back_nodes[j]
        n2 = back_nodes[j+1]
        draw_wall_3d(screen, (n1[0], n1[1], 41), (n2[0], n2[1], 41), (n2[0], n2[1], 39), (n1[0], n1[1], 39), C_SHARK_SHAD, ox, oy, outline_color=C_OUTLINE)

    # 4. Sisi Kiri (Highlight) - Digambar paling depan/atas
    left_points_2d = [to_iso(p[0], p[1], p[2], ox, oy) for p in p_fin_left]
    left_points_2d_int = [(int(x), int(y)) for x, y in left_points_2d]
    pygame.draw.polygon(screen, C_SHARK_LEFT, left_points_2d_int)
    if C_OUTLINE:
        pygame.draw.polygon(screen, C_OUTLINE, left_points_2d_int, 1)

    # =================================================================
    # C. RIAK AIR DI SEKITAR SIRIP (Fin Wake Ripples)
    # =================================================================
    splash_surf = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    
    # Titik masuk sirip hiu di air
    p_front = to_iso(75, 0, 40, ox, oy)
    p_back = to_iso(105, 0, 40, ox, oy)
    
    splash_cx = (p_front[0] + p_back[0]) // 2
    splash_cy = (p_front[1] + p_back[1]) // 2
    splash_w = int(p_back[0] - p_front[0]) + 15
    splash_h = int(splash_w * 0.3)

    # Riak buih putih
    pygame.draw.ellipse(splash_surf, (255, 255, 255, 120), (splash_cx - splash_w//2, splash_cy - splash_h//2, splash_w, splash_h), 2)
    
    # Ombak riak kecil memanjang ke belakang fin
    pygame.draw.ellipse(splash_surf, (200, 230, 255, 60), (splash_cx - splash_w//2 + 10, splash_cy - splash_h//2 + 5, splash_w + 10, splash_h - 2), 1)

    screen.blit(splash_surf, (0, 0))
