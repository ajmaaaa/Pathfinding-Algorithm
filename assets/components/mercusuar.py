import pygame
import sys

def draw_3d_stack(surface, cx, base_y, bw, tw, h, c_light, c_dark, c_top):
    """
    Fungsi engine 3D untuk membuat objek silinder/kerucut dengan efek shading (bayangan).
    - bw: Lebar bawah (Bottom Width)
    - tw: Lebar atas (Top Width)
    - h: Tinggi objek
    """
    for i in range(int(h)):
        # Hitung rasio pengecilan untuk efek mengerucut (taper)
        ratio = i / float(h) if h > 1 else 0
        w = bw - (bw - tw) * ratio
        eh = w * 0.45  # Tinggi elips (perspektif isometrik)
        y = base_y - i
        
        # Gambar sisi kanan (Lebih gelap / Shadow)
        pygame.draw.ellipse(surface, c_dark, (cx - w/2, y - eh/2, w, eh))
        
        # Gambar sisi kiri (Lebih terang / Highlight), sedikit digeser & dikecilkan
        light_w = w * 0.8
        pygame.draw.ellipse(surface, c_light, (cx - w/2, y - eh/2, light_w, eh))
        
    # Tutup atas (Top Cap)
    if tw > 0:
        top_eh = tw * 0.45
        pygame.draw.ellipse(surface, c_top, (cx - tw/2, base_y - h - top_eh/2, tw, top_eh))
        
    return base_y - h # Mengembalikan posisi Y terbaru untuk ditumpuk objek selanjutnya

def draw_window(surface, wx, wy, w, h):
    """Fungsi untuk menggambar jendela melengkung khas mercusuar"""
    C_WIN = (29, 47, 71)
    C_WIN_FRAME = (150, 160, 170)
    
    # Kaca Jendela
    pygame.draw.rect(surface, C_WIN, (wx, wy, w, h))
    pygame.draw.ellipse(surface, C_WIN, (wx, wy - w/2, w, w))
    # Bingkai (Frame)
    pygame.draw.rect(surface, C_WIN_FRAME, (wx, wy, w, h), 1)
    pygame.draw.arc(surface, C_WIN_FRAME, (wx, wy - w/2, w, w), 0, 3.14, 1)

def draw_mercusuar(screen, cx, cy):
    """Fungsi utama merender seluruh pulau dan mercusuar"""
    
    # --- PALET WARNA ---
    C_WATER_TOP = (66, 135, 245)
    C_WATER_L = (37, 88, 168)
    C_WATER_R = (23, 62, 122)
    C_ROCK_L = (149, 163, 179)
    C_ROCK_D = (105, 116, 130)
    C_GRASS = (151, 204, 90)
    C_WHITE_L = (250, 252, 255)
    C_WHITE_D = (179, 193, 209)
    C_RED_L = (227, 59, 73)
    C_RED_D = (161, 33, 45)
    C_GLASS_L = (116, 194, 242)
    C_GLASS_D = (63, 132, 181)
    C_GREY_L = (130, 140, 155)
    C_GREY_D = (81, 94, 110)

    # 1. (Alas air dan riak ombak dihapus agar mercusuar dapat diletakkan di lautan utama)

    # 2. RENDER BATU (ROCKS ISLAND)
    rocks = [
        (-90, -10, 60, 25), (-70, -30, 65, 20), (0, -45, 90, 30),
        (60, -35, 70, 25), (90, 0, 60, 20), (80, 35, 75, 25),
        (30, 50, 90, 35), (-35, 45, 80, 25), (-85, 20, 65, 22),
        (-45, 10, 95, 30), (25, 15, 90, 30)
    ]
    rocks.sort(key=lambda r: r[1]) # Sortir Y agar tumpukan 3D benar (Painters Algorithm)
    
    for r_dx, r_dy, r_w, r_h in rocks:
        rx, ry = cx + r_dx, cy + r_dy
        for z in range(r_h):
            pygame.draw.ellipse(screen, C_ROCK_D, (rx - r_w/2, ry - z - (r_w*0.45)/2, r_w, r_w*0.45))
        # Permukaan atas batu
        top_rect = (rx - r_w/2, ry - r_h - (r_w*0.45)/2, r_w, r_w*0.45)
        pygame.draw.ellipse(screen, C_ROCK_L, top_rect)
        pygame.draw.ellipse(screen, (90, 100, 110), top_rect, 1) # Garis tegas batu

    # 3. RENDER RUMPUT (GRASS BASE)
    grass_y = cy - 20
    pygame.draw.ellipse(screen, (110, 150, 70), (cx - 75, grass_y - 35, 150, 70))
    pygame.draw.ellipse(screen, C_GRASS, (cx - 70, grass_y - 32, 140, 64))

    # 4. RENDER MENARA MERCUSUAR (STACKING)
    y_cursor = grass_y - 5
    
    # Segmen Putih Bawah
    y_cursor = draw_3d_stack(screen, cx, y_cursor, 110, 95, 60, C_WHITE_L, C_WHITE_D, (230, 240, 250))
    # Segmen Merah Tengah
    y_cursor = draw_3d_stack(screen, cx, y_cursor, 95, 80, 55, C_RED_L, C_RED_D, (200, 45, 55))
    # Segmen Putih Atas
    y_cursor = draw_3d_stack(screen, cx, y_cursor, 80, 65, 50, C_WHITE_L, C_WHITE_D, (230, 240, 250))
    
    # 5. RENDER BALKON & RUANG KACA (LANTERN ROOM)
    # Dasar Balkon Merah
    y_cursor = draw_3d_stack(screen, cx, y_cursor, 75, 75, 10, C_RED_L, C_RED_D, (200, 45, 55))
    # Dek Balkon Abu-abu
    y_cursor = draw_3d_stack(screen, cx, y_cursor, 90, 90, 6, C_GREY_L, C_GREY_D, (150, 160, 170))
    # Kaca Ruang Lampu Biru
    y_cursor = draw_3d_stack(screen, cx, y_cursor, 55, 55, 40, C_GLASS_L, C_GLASS_D, (150, 210, 250))
    # Base Atap Abu-abu
    y_cursor = draw_3d_stack(screen, cx, y_cursor, 70, 70, 6, C_GREY_L, C_GREY_D, (150, 160, 170))
    
    # 6. RENDER ATAP KUBAH (DOME ROOF) & BOLA PUNCAK
    # Atap kerucut (Top width = 0)
    y_cursor = draw_3d_stack(screen, cx, y_cursor, 70, 0, 40, C_RED_L, C_RED_D, C_RED_L)
    # Bola Merah (Finial)
    pygame.draw.circle(screen, C_RED_D, (int(cx), int(y_cursor)), 9)
    pygame.draw.circle(screen, C_RED_L, (int(cx - 3), int(y_cursor - 3)), 5) # Highlight bola

    # 7. RENDER JENDELA (Digambar paling akhir agar berada di luar dinding)
    draw_window(screen, cx - 25, grass_y - 40, 14, 18)  # Jendela bawah
    draw_window(screen, cx - 20, grass_y - 100, 12, 16) # Jendela tengah
    draw_window(screen, cx - 17, grass_y - 150, 10, 14) # Jendela atas