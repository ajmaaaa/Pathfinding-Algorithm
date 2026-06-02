import pygame
import sys

# ================= WARNA-WARNA (Palet Semi 3D Premium) =================
BG_COLOR = (240, 244, 240)       # Warna latar belakang abu-abu kehijauan muda
GRASS_TOP = (110, 190, 120)      # Hijau rumput atas yang lebih cerah & modern
GRASS_SIDE1 = (80, 140, 90)      # Sisi kiri rumput
GRASS_SIDE2 = (65, 120, 75)      # Sisi kanan rumput
PATH_TOP = (215, 220, 215)       # Paving abu-abu terang
PATH_SIDE = (165, 170, 165)      # Pinggiran paving 3D
WATER = (90, 190, 220)           # Air mancur biru
STONE_TOP = (220, 215, 205)      # Batu air mancur terang
STONE_SIDE = (170, 165, 155)     # Batu air mancur gelap
WOOD_TOP = (180, 120, 80)        # Kayu bangku terang
WOOD_SIDE = (130, 80, 50)        # Kayu bangku gelap
METAL = (80, 85, 90)             # Tiang lampu
LEAF_LIGHT = (100, 175, 95)      # Daun terang (untuk semak)
LEAF_DARK = (65, 130, 60)        # Daun gelap (untuk semak)

def draw_ellipse_3d(surface, color_top, color_side, x, y, w, h, depth):
    """Fungsi menggambar elips 3D dengan ketebalan tertentu"""
    # Alas bawah (sisi gelap)
    pygame.draw.ellipse(surface, color_side, (x, y + depth, w, h))
    # Dinding penghubung agar tidak ada celah
    pygame.draw.rect(surface, color_side, (x, y + h//2, w, depth))
    # Tutup atas (sisi terang)
    pygame.draw.ellipse(surface, color_top, (x, y, w, h))
    # Outline tutup atas
    pygame.draw.ellipse(surface, (45, 45, 45), (x, y, w, h), 1)

def draw_bush(surface, x, y):
    """Menggambar semak-semak kecil di atas rumput"""
    pygame.draw.ellipse(surface, LEAF_DARK, (x-20, y-20, 40, 30))
    pygame.draw.ellipse(surface, LEAF_LIGHT, (x-15, y-25, 40, 30))
    pygame.draw.ellipse(surface, (45, 45, 45), (x-15, y-25, 40, 30), 1)
    
    pygame.draw.ellipse(surface, LEAF_DARK, (x, y-15, 30, 20))
    pygame.draw.ellipse(surface, LEAF_LIGHT, (x+5, y-20, 30, 20))
    pygame.draw.ellipse(surface, (45, 45, 45), (x+5, y-20, 30, 20), 1)

def draw_lamppost(surface, x, y):
    """Menggambar tiang lampu jalan isometrik"""
    # Tiang dengan outline hitam tipis
    pygame.draw.rect(surface, (45, 45, 45), (x-3, y-91, 6, 92))
    pygame.draw.rect(surface, METAL, (x-2, y-90, 4, 90))
    
    # Base tiang
    draw_ellipse_3d(surface, PATH_SIDE, METAL, x-8, y-5, 16, 8, 3)
    
    # Kaca / Cahaya lampu
    pygame.draw.polygon(surface, (255, 255, 180), [(x-8, y-92), (x+8, y-92), (x+5, y-104), (x-5, y-104)])
    pygame.draw.polygon(surface, (45, 45, 45), [(x-8, y-92), (x+8, y-92), (x+5, y-104), (x-5, y-104)], 1)
    
    # Atap lampu
    pygame.draw.polygon(surface, METAL, [(x-10, y-104), (x, y-114), (x+10, y-104)])
    pygame.draw.polygon(surface, (45, 45, 45), [(x-10, y-104), (x, y-114), (x+10, y-104)], 1)

def draw_bench(surface, x, y, facing_right=True):
    """Menggambar bangku taman kayu 3D"""
    if facing_right:
        seat_top = [(x, y), (x+50, y-25), (x+70, y-15), (x+20, y+10)]
        back_rest = [(x+50, y-25), (x+70, y-15), (x+65, y-40), (x+45, y-50)]
        legs = [(x+5, y), (x+45, y-20), (x+65, y-10), (x+20, y+5)]
    else:
        seat_top = [(x, y), (x-50, y-25), (x-70, y-15), (x-20, y+10)]
        back_rest = [(x-50, y-25), (x-70, y-15), (x-65, y-40), (x-45, y-50)]
        legs = [(x-5, y), (x-45, y-20), (x-65, y-10), (x-20, y+5)]

    # Gambar Kaki Bangku
    for lx, ly in legs:
        pygame.draw.rect(surface, (45, 45, 45), (lx-1, ly, 5, 15))
        pygame.draw.rect(surface, METAL, (lx, ly, 3, 15))

    # Dudukan (Sisi tebal bawah lalu atas)
    seat_side = [(px, py+5) for px, py in seat_top]
    pygame.draw.polygon(surface, WOOD_SIDE, seat_side)
    pygame.draw.polygon(surface, (45, 45, 45), seat_side, 1)
    pygame.draw.polygon(surface, WOOD_TOP, seat_top)
    pygame.draw.polygon(surface, (45, 45, 45), seat_top, 1)

    # Sandaran Punggung
    back_side = [(px, py+3) for px, py in back_rest]
    pygame.draw.polygon(surface, WOOD_SIDE, back_side)
    pygame.draw.polygon(surface, (45, 45, 45), back_side, 1)
    pygame.draw.polygon(surface, WOOD_TOP, back_rest)
    pygame.draw.polygon(surface, (45, 45, 45), back_rest, 1)

def draw_taman(surface, offset_x=0, offset_y=0):
    """
    Fungsi utama untuk menggambar taman modern.
    Bisa dipanggil dari main.py dengan mengirimkan objek surface screen.
    """
    cx = 400 + offset_x
    cy = 300 + offset_y

    # Helper untuk Matematika Proyeksi Isometrik
    def iso(u, v, w):
        sx = cx + (u - v) * 1.6
        sy = cy + (u + v) * 0.8 - w
        return sx, sy

    def draw_poly_iso(pts, color, outline=True, lw=2, outline_color=(45, 45, 45)):
        pts2 = [iso(u, v, w) for u, v, w in pts]
        pygame.draw.polygon(surface, color, pts2)
        if outline:
            pygame.draw.polygon(surface, outline_color, pts2, lw)

    L = 93.75      # Setengah panjang alas taman agar dimensi pas 300x150px secara isometrik
    thickness = 2  # Alas dipertipis (2px) agar modern, sleek, dan tidak tebal

    # 1. PLATFORM TANAH (Alas Tipis Isometrik) - Menggunakan warna paving
    base_top = [(-L, -L, 0), (L, -L, 0), (L, L, 0), (-L, L, 0)]
    base_left = [(-L, L, -thickness), (L, L, -thickness), (L, L, 0), (-L, L, 0)]
    base_right = [(L, -L, -thickness), (L, L, -thickness), (L, L, 0), (L, -L, 0)]

    # Sisi alas menggunakan warna paving 3D untuk efek modern
    pygame.draw.polygon(surface, PATH_SIDE, [iso(u, v, w) for u, v, w in base_left])
    pygame.draw.polygon(surface, (145, 150, 145), [iso(u, v, w) for u, v, w in base_right])
    pygame.draw.polygon(surface, (45, 45, 45), [iso(u, v, w) for u, v, w in base_left], 2)
    pygame.draw.polygon(surface, (45, 45, 45), [iso(u, v, w) for u, v, w in base_right], 2)
    
    # Isi permukaan atas alas dengan warna paving utama
    draw_poly_iso(base_top, PATH_TOP, outline=True, lw=2)

    # 2. INNER LAWN (RUMPUT DALAM)
    # Ini menciptakan paved walkway di sekeliling taman (tepi jalan)
    L_grass = L - 15  # Lebar jalan setapak perimeter diatur 15 unit
    grass_top = [(-L_grass, -L_grass, 0), (L_grass, -L_grass, 0), (L_grass, L_grass, 0), (-L_grass, L_grass, 0)]
    draw_poly_iso(grass_top, GRASS_TOP, outline=True, lw=2, outline_color=(45, 45, 45))

    # 3. DECK KAYU TEPI KOLAM (Premium Modern Landscaping Feature)
    # Letakkan deck kayu di sisi kanan-atas dari kolam
    deck_top = [(cx + 10, cy - 25), (cx + 55, cy - 2), (cx + 35, cy + 8), (cx - 10, cy - 15)]
    deck_bot = [(x, y + 4) for x, y in deck_top]
    pygame.draw.polygon(surface, WOOD_SIDE, [deck_top[0], deck_top[3], deck_bot[3], deck_bot[0]])
    pygame.draw.polygon(surface, WOOD_SIDE, [deck_top[3], deck_top[2], deck_bot[2], deck_bot[3]])
    pygame.draw.polygon(surface, (45, 45, 45), [deck_top[0], deck_top[3], deck_bot[3], deck_bot[0]], 1)
    pygame.draw.polygon(surface, (45, 45, 45), [deck_top[3], deck_top[2], deck_bot[2], deck_bot[3]], 1)
    pygame.draw.polygon(surface, WOOD_TOP, deck_top)
    pygame.draw.polygon(surface, (45, 45, 45), deck_top, 1)
    # Plank lines untuk serat kayu deck
    pygame.draw.line(surface, WOOD_SIDE, (cx, cy - 20), (cx + 45, cy + 2.5), 1)
    pygame.draw.line(surface, WOOD_SIDE, (cx - 10, cy - 15), (cx + 35, cy + 8), 1)

    # 4. KOLAM ALAMI (POND)
    # Air kolam di bagian dalam
    pygame.draw.ellipse(surface, WATER, (cx - 68, cy - 34, 136, 68))
    
    # 5. BEBATUAN TEPI KOLAM (Natural Rock Border)
    # Bebatuan alami di pinggir kolam
    import math
    stone_positions = []
    num_stones = 16
    for i in range(num_stones):
        theta = i * (2 * math.pi / num_stones)
        # Menambahkan variasi jarak radius agar bentuknya organik/natural
        noise_r = (i % 3 - 1) * 3
        rx = 70 + noise_r
        ry = 35 + noise_r * 0.5
        sx = cx + rx * math.cos(theta)
        sy = cy + ry * math.sin(theta)
        # Ukuran bebatuan bervariasi
        sw = 14 + (i % 4) * 2
        sh = 9 + (i % 3) * 2
        s_depth = 4 + (i % 2) * 2
        # Menggambar batu 3D natural
        draw_ellipse_3d(surface, STONE_TOP, STONE_SIDE, sx - sw//2, sy - sh//2, sw, sh, s_depth)

    # Border hitam di atas air untuk merapikan tepi
    pygame.draw.ellipse(surface, (45, 45, 45), (cx - 68, cy - 34, 136, 68), 1)

    # 6. TANAMAN AIR (Lily Pads & Flowers)
    # Lily pads (daun teratai) hijau tua
    pygame.draw.ellipse(surface, (40, 110, 55), (cx - 40, cy - 12, 12, 7))
    pygame.draw.ellipse(surface, (45, 45, 45), (cx - 40, cy - 12, 12, 7), 1)
    pygame.draw.ellipse(surface, (40, 110, 55), (cx + 30, cy + 12, 13, 8))
    pygame.draw.ellipse(surface, (45, 45, 45), (cx + 30, cy + 12, 13, 8), 1)
    pygame.draw.ellipse(surface, (40, 110, 55), (cx + 10, cy - 18, 10, 6))
    pygame.draw.ellipse(surface, (45, 45, 45), (cx + 10, cy - 18, 10, 6), 1)

    # Bunga Teratai Pink Kecil
    pygame.draw.circle(surface, (255, 170, 190), (cx - 34, cy - 8), 3)
    pygame.draw.circle(surface, (255, 255, 255), (cx - 34, cy - 8), 1)
    pygame.draw.circle(surface, (255, 170, 190), (cx + 36, cy + 16), 4)
    pygame.draw.circle(surface, (255, 255, 255), (cx + 36, cy + 16), 2)

    # 7. AIR MANCUR SINGLE-JET MINIMALIS (Modern Fountain)
    # Kolom air utama
    pygame.draw.line(surface, (230, 245, 255), (cx, cy - 4), (cx, cy - 36), 3)
    pygame.draw.line(surface, (255, 255, 255), (cx - 1, cy - 4), (cx - 1, cy - 36), 1)
    # Efek semprotan air di puncak
    pygame.draw.circle(surface, (255, 255, 255), (cx, cy - 36), 5)
    pygame.draw.arc(surface, (200, 235, 255), (cx - 8, cy - 42, 16, 16), 0, 3.14, 2)
    pygame.draw.arc(surface, (200, 235, 255), (cx - 14, cy - 40, 28, 24), 0.5, 2.64, 2)
    # Tetesan cipratan air
    pygame.draw.circle(surface, (240, 250, 255), (cx - 5, cy - 25), 3)
    pygame.draw.circle(surface, (240, 250, 255), (cx + 6, cy - 22), 2)
    pygame.draw.circle(surface, (240, 250, 255), (cx - 10, cy - 15), 2)
    pygame.draw.circle(surface, (240, 250, 255), (cx + 12, cy - 13), 2)

    # 8. BAYANGAN ELEMENT (Hanya bayangan pond)
    shadow_surf = pygame.Surface((800, 600), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow_surf, (0, 0, 0, 35), (cx - 75, cy - 32, 150, 64))
    surface.blit(shadow_surf, (offset_x, offset_y))

    # 9. BANGKU TAMAN (Ditempatkan di tepi jalan setapak perimeter)
    draw_bench(surface, cx - 120, cy + 78, facing_right=True)
    draw_bench(surface, cx + 120, cy - 78, facing_right=False)

    # 10. SEMAK-SEMAK & BUNGA WARNA-WARNI (Lawn Landscaping)
    draw_bush(surface, *iso(-65, 65, 0))   # Kiri (Quadrant Grass C)
    draw_bush(surface, *iso(65, -65, 0))   # Kanan (Quadrant Grass D)
    draw_bush(surface, *iso(-65, -65, 0))  # Atas (Quadrant Grass B)
    draw_bush(surface, *iso(65, 65, 0))     # Bawah (Quadrant Grass A)

    # Bunga Merah
    pygame.draw.circle(surface, (235, 80, 80), (cx - 105, cy - 10), 3)
    pygame.draw.circle(surface, (235, 80, 80), (cx - 110, cy - 14), 2.5)
    pygame.draw.circle(surface, (235, 80, 80), (cx - 100, cy - 12), 2)
    # Bunga Kuning
    pygame.draw.circle(surface, (245, 215, 65), (cx + 105, cy + 12), 3)
    pygame.draw.circle(surface, (245, 215, 65), (cx + 100, cy + 16), 2.5)
    pygame.draw.circle(surface, (245, 215, 65), (cx + 110, cy + 8), 2)
    # Bunga Ungu
    pygame.draw.circle(surface, (175, 95, 225), (cx - 30, cy + 50), 3)
    pygame.draw.circle(surface, (175, 95, 225), (cx - 35, cy + 54), 2.5)
    pygame.draw.circle(surface, (175, 95, 225), (cx - 25, cy + 48), 2)

    # 11. TIANG LAMPU (Di tepi luar paving perimeter)
    draw_lamppost(surface, cx - 210, cy + 20)
    draw_lamppost(surface, cx + 210, cy - 20)
    draw_lamppost(surface, cx + 10, cy - 115)
    draw_lamppost(surface, cx - 10, cy + 115)

    # 12. TONG SAMPAH (Ditaruh rapi di tepi jalan)
    bx, by = cx + 175, cy - 40
    pygame.draw.polygon(surface, (120, 50, 40), [(bx, by), (bx+15, by-8), (bx+15, by+7), (bx, by+15)])
    pygame.draw.polygon(surface, (90, 30, 20), [(bx+15, by-8), (bx+30, by), (bx+30, by+15), (bx+15, by+7)])
    pygame.draw.polygon(surface, (50, 50, 50), [(bx, by), (bx+15, by-8), (bx+30, by), (bx+15, by+8)])
    pygame.draw.polygon(surface, (45, 45, 45), [(bx, by), (bx+15, by-8), (bx+30, by), (bx+15, by+8)], 1)


# ================= SCRIPT EKSEKUSI (Bisa dirun mandiri) =================
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Desain Taman 3D Isometrik")
    clock = pygame.time.Clock()

    while True:
        screen.fill(BG_COLOR)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        draw_taman(screen)

        pygame.display.flip()
        clock.tick(30)