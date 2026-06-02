import pygame
import math

# --- ENGINE PROYEKSI MATRIKS 3D ISOMETRIK MANUAL ---
SCALE = 1.4

def to_iso(x, y, z, ox, oy):
    """Mengubah koordinat ruang 3D (X, Y, Z) menjadi koordinat bidang layar 2D"""
    ix = ox + (x - z) * 2 * SCALE
    iy = oy + (x + z) * 1 * SCALE - y * 2 * SCALE
    return (ix, iy)

def draw_wall_3d(screen, p1, p2, p3, p4, color, ox, oy, outline_color=(45, 30, 20)):
    """Menggambar poligon 3D dengan outline rapi"""
    points = [to_iso(p[0], p[1], p[2], ox, oy) for p in [p1, p2, p3, p4]]
    int_points = [(int(pt[0]), int(pt[1])) for pt in points]
    pygame.draw.polygon(screen, color, int_points)
    if outline_color:
        pygame.draw.polygon(screen, outline_color, int_points, 1)

def draw_kapal_layar(screen, ox, oy):
    """Fungsi utama menggambar Kapal Layar / Kapal Pencari Ikan Tradisional 3D"""
    
    # --- PALET WARNA KAPAL LAYAR ---
    C_WOOD_TOP    = (175, 110, 65)      # Kayu jati atas dek
    C_WOOD_LEFT   = (135, 80, 45)       # Lambung kiri kayu
    C_WOOD_SHAD   = (90, 50, 25)        # Lambung kanan bayangan
    C_OUTLINE     = (45, 30, 20)
    
    C_MAST        = (75, 65, 55)        # Tiang layar logam/kayu tua
    C_SAIL_MAIN   = (245, 245, 240)     # Layar utama putih bersih
    C_SAIL_JIB    = (230, 230, 225)     # Layar depan (Jib) abu-abu terang
    C_SAIL_OUT    = (185, 185, 180)
    
    C_FLAG        = (225, 45, 50)       # Bendera merah di puncak
    C_CABIN       = (195, 205, 215)     # Kabin awak kapal
    C_CABIN_SHAD  = (150, 160, 170)
    
    C_WAKE        = (240, 250, 255, 90) # Buih air di belakang kapal

    # =================================================================
    # 1. EFFECT OMBAK CIPRATAN AIR (Water Wake)
    # =================================================================
    splash_surf = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    p_bow = to_iso(30, 0, 40, ox, oy)
    p_stern = to_iso(130, 0, 40, ox, oy)
    
    wake_cx = (p_bow[0] + p_stern[0]) // 2
    wake_cy = (p_bow[1] + p_stern[1]) // 2
    wake_w = int(p_stern[0] - p_bow[0]) + 50
    wake_h = int(wake_w * 0.32)

    # Riak air melingkari seluruh kapal
    pygame.draw.ellipse(splash_surf, (200, 230, 255, 55), (wake_cx - wake_w//2, wake_cy - wake_h//2, wake_w, wake_h), 2)
    screen.blit(splash_surf, (0, 0))

    # =================================================================
    # 2. LAMBUNG KAPAL 3D (Wooden Hull Segments)
    # X dari 30 (Haluan/Depan) ke 130 (Buritan/Belakang)
    # =================================================================
    hull_segments = [
        (30,  6, 14, 40, 6),   # 0: Bow (Haluan Lancip)
        (55,  0, 13, 40, 18),  # 1
        (80,  0, 12, 40, 22),  # 2: Tengah Lambung
        (105, 2, 11, 40, 20),  # 3
        (130, 6, 10, 40, 14)   # 4: Transom (Belakang Datar)
    ]

    for i in range(len(hull_segments) - 2, -1, -1):
        back_seg = hull_segments[i+1]
        frnt_seg = hull_segments[i]
        
        bx, by_bot, by_top, bz_c, bw = back_seg
        fx, fy_bot, fy_top, fz_c, fw = frnt_seg
        
        bz_L, bz_R = bz_c + bw//2, bz_c - bw//2
        fz_L, fz_R = fz_c + fw//2, fz_c - fw//2

        # Dinding samping kiri kayu
        draw_wall_3d(screen, (bx, by_bot, bz_L), (fx, fy_bot, fz_L), (fx, fy_top, fz_L), (bx, by_top, bz_L), C_WOOD_LEFT, ox, oy, outline_color=C_OUTLINE)
        
        # Dek Kayu Atas
        draw_wall_3d(screen, (bx, by_top, bz_L), (fx, fy_top, fz_L), (fx, fy_top, fz_R), (bx, by_top, bz_R), C_WOOD_TOP, ox, oy, outline_color=C_OUTLINE)
        
        # Dinding kanan kayu (Shadow)
        draw_wall_3d(screen, (bx, by_top, bz_R), (fx, fy_top, fz_R), (fx, fy_bot, fz_R), (bx, by_bot, bz_R), C_WOOD_SHAD, ox, oy, outline_color=C_OUTLINE)

    # =================================================================
    # 3. KABIN AWAK KAPAL (Deckhouse Cabin)
    # =================================================================
    # Terletak di dek belakang (X=85 ke X=105, lebar Z=12, tinggi Y=12 ke Y=18)
    draw_wall_3d(screen, (105, 11, 46), (85, 12, 46), (85, 18, 46), (105, 18, 46), C_CABIN, ox, oy, outline_color=C_OUTLINE)
    draw_wall_3d(screen, (105, 18, 46), (85, 18, 46), (85, 18, 34), (105, 18, 34), C_SAIL_MAIN, ox, oy, outline_color=C_OUTLINE)
    draw_wall_3d(screen, (105, 18, 34), (85, 18, 34), (85, 12, 34), (105, 11, 34), C_CABIN_SHAD, ox, oy, outline_color=C_OUTLINE)
    # Pintu masuk kabin kecil
    p_door = to_iso(85, 12, 41, ox, oy)
    pygame.draw.rect(screen, C_OUTLINE, (int(p_door[0]) - 3, int(p_door[1]) - 6, 6, 8))

    # =================================================================
    # 4. TIANG LAYAR UTAMA (Main Mast Cylinder)
    # Berdiri di X=70, Z=40, menjulang dari dek Y=12 ke Y=110
    # =================================================================
    mast_base = to_iso(70, 12, 40, ox, oy)
    mast_top = to_iso(70, 110, 40, ox, oy)
    pygame.draw.line(screen, C_MAST, (int(mast_base[0]), int(mast_base[1])), (int(mast_top[0]), int(mast_top[1])), 4)
    pygame.draw.line(screen, (45, 45, 45), (int(mast_base[0]), int(mast_base[1])), (int(mast_top[0]), int(mast_top[1])), 1)

    # =================================================================
    # 5. LAYAR-LAYAR TIUP ANGIN (Wind-Filled Sails with 3D Depth)
    # =================================================================
    # A. Layar Utama (Mainsail - Di belakang tiang, X=70 ke X=120)
    # Sisi Kiri Layar
    draw_wall_3d(screen, (70, 20, 40.5), (70, 95, 40.5), (120, 30, 40.5), (110, 15, 40.5), C_SAIL_MAIN, ox, oy, outline_color=C_SAIL_OUT)
    # Sisi Kanan/Tepi Layar
    draw_wall_3d(screen, (70, 20, 39.5), (70, 95, 39.5), (120, 30, 39.5), (110, 15, 39.5), C_SAIL_JIB, ox, oy, outline_color=C_SAIL_OUT)
    # Sambungan Pinggir Layar Utama (3D thickness)
    draw_wall_3d(screen, (70, 20, 40.5), (70, 95, 40.5), (70, 95, 39.5), (70, 20, 39.5), C_SAIL_MAIN, ox, oy, outline_color=None)
    draw_wall_3d(screen, (70, 95, 40.5), (120, 30, 40.5), (120, 30, 39.5), (70, 95, 39.5), C_SAIL_MAIN, ox, oy, outline_color=None)
    draw_wall_3d(screen, (120, 30, 40.5), (110, 15, 40.5), (110, 15, 39.5), (120, 30, 39.5), C_SAIL_MAIN, ox, oy, outline_color=None)

    # B. Layar Depan (Jib Sail - Di depan tiang, X=35 ke X=70)
    # Sisi Kiri Jib
    draw_wall_3d(screen, (35, 14, 40.5), (70, 85, 40.5), (70, 25, 40.5), (65, 14, 40.5), C_SAIL_JIB, ox, oy, outline_color=C_SAIL_OUT)
    # Sisi Kanan Jib
    draw_wall_3d(screen, (35, 14, 39.5), (70, 85, 39.5), (70, 25, 39.5), (65, 14, 39.5), C_SAIL_MAIN, ox, oy, outline_color=C_SAIL_OUT)
    # Sambungan Pinggir Jib
    draw_wall_3d(screen, (35, 14, 40.5), (70, 85, 40.5), (70, 85, 39.5), (35, 14, 39.5), C_SAIL_JIB, ox, oy, outline_color=None)
    draw_wall_3d(screen, (70, 85, 40.5), (70, 25, 40.5), (70, 25, 39.5), (70, 85, 39.5), C_SAIL_JIB, ox, oy, outline_color=None)

    # =================================================================
    # 6. BENDERA MERAH (Flag at Mast Peak)
    # Berada di puncak tiang Y=110, berkibar ke kiri (X berkurang)
    # =================================================================
    flag_points = [
        to_iso(70, 110, 40, ox, oy),
        to_iso(52, 105, 40, ox, oy),
        to_iso(70, 100, 40, ox, oy)
    ]
    int_flag = [(int(pt[0]), int(pt[1])) for pt in flag_points]
    pygame.draw.polygon(screen, C_FLAG, int_flag)
    pygame.draw.polygon(screen, (150, 20, 20), int_flag, 1)
