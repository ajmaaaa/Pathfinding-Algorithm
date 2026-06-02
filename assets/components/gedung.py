import pygame
import sys

# --- PALET WARNA ---
KACA_KIRI = (62, 107, 147)
KACA_KANAN = (96, 155, 206)
KACA_ATAS = (210, 225, 235)
FRAME = (35, 60, 85)
TANAH_KIRI = (140, 150, 160)
TANAH_KANAN = (175, 185, 195)
TANAH_ATAS = (200, 210, 220)
RUMPUT_ATAS = (120, 180, 110)
HELIPAD_SIDE = (60, 65, 70)
HELIPAD_TOP = (80, 85, 90)
KUNING_HELI = (240, 210, 50)
LOBBY_KIRI = (170, 190, 210)
LOBBY_KANAN = (190, 210, 230)
LOBBY_ATAS = (150, 170, 190)

def gambar_poligon(layar, warna, titik, ketebalan=0):
    pygame.draw.polygon(layar, warna, titik, ketebalan)
    if ketebalan == 0:
        pygame.draw.aalines(layar, warna, True, titik)

def gambar_blok(layar, x, y, dx, dy, tinggi, w_kiri, w_kanan, w_atas):
    gambar_poligon(layar, w_kiri, [(x, y), (x-dx, y-dy), (x-dx, y-dy-tinggi), (x, y-tinggi)])
    gambar_poligon(layar, w_kanan, [(x, y), (x+dx, y-dy), (x+dx, y-dy-tinggi), (x, y-tinggi)])
    gambar_poligon(layar, w_atas, [(x, y-tinggi), (x-dx, y-dy-tinggi), (x, y-dy*2-tinggi), (x+dx, y-dy-tinggi)])

def iso_pt(bx, by, l, r):
    return bx - l*2 + r*2, by - l - r

def render_gedung(layar, cx, cy, scale=1.0):
    # (Base slab dan taman dihapus agar tidak tumpang tindih di klaster CBD)
    # CBD base sudah menyediakan alas bersama.
    y_top = cy

    cx_b, cy_b = iso_pt(cx, y_top, 40 * scale, 40 * scale)
    TINGGI = 360 * scale
    DX, DY = 140 * scale, 70 * scale
    
    gambar_blok(layar, cx_b, cy_b, DX, DY, TINGGI, KACA_KIRI, KACA_KANAN, KACA_ATAS)
    
    y_atap = cy_b - TINGGI
    pygame.draw.aaline(layar, FRAME, (cx_b, cy_b), (cx_b, y_atap))
    
    for i in range(1, 7):
        xk, ybk = cx_b - (DX * i // 7), cy_b - (DY * i // 7)
        xkn, ybkn = cx_b + (DX * i // 7), cy_b - (DY * i // 7)
        pygame.draw.aaline(layar, FRAME, (xk, ybk), (xk, ybk - TINGGI))
        pygame.draw.aaline(layar, FRAME, (xkn, ybkn), (xkn, ybkn - TINGGI))
        
    for i in range(1, 16):
        yg = cy_b - (TINGGI * i // 16)
        pygame.draw.aaline(layar, FRAME, (cx_b, yg), (cx_b-DX, yg-DY))
        pygame.draw.aaline(layar, FRAME, (cx_b, yg), (cx_b+DX, yg-DY))

    gambar_blok(layar, cx_b, cy_b, 40 * scale, 20 * scale, 30 * scale, LOBBY_KIRI, LOBBY_KANAN, LOBBY_ATAS)
    pygame.draw.aaline(layar, FRAME, (cx_b, cy_b), (cx_b, cy_b-30*scale))
    
    gambar_blok(layar, cx_b, cy_b-26*scale, 44 * scale, 22 * scale, 4 * scale, FRAME, FRAME, KACA_ATAS)
    
    d1_kiri, d2_kiri = iso_pt(cx_b, cy_b, 5 * scale, 0), iso_pt(cx_b, cy_b, 15 * scale, 0)
    gambar_poligon(layar, KACA_ATAS, [(d1_kiri[0], d1_kiri[1]-2*scale), (d2_kiri[0], d2_kiri[1]-2*scale), (d2_kiri[0], d2_kiri[1]-22*scale), (d1_kiri[0], d1_kiri[1]-22*scale)])
    pygame.draw.polygon(layar, FRAME, [(d1_kiri[0], d1_kiri[1]-2*scale), (d2_kiri[0], d2_kiri[1]-2*scale), (d2_kiri[0], d2_kiri[1]-22*scale), (d1_kiri[0], d1_kiri[1]-22*scale)], max(1, int(scale)))

    d1_kan, d2_kan = iso_pt(cx_b, cy_b, 0, 5 * scale), iso_pt(cx_b, cy_b, 0, 15 * scale)
    gambar_poligon(layar, KACA_ATAS, [(d1_kan[0], d1_kan[1]-2*scale), (d2_kan[0], d2_kan[1]-2*scale), (d2_kan[0], d2_kan[1]-22*scale), (d1_kan[0], d1_kan[1]-22*scale)])
    pygame.draw.polygon(layar, FRAME, [(d1_kan[0], d1_kan[1]-2*scale), (d2_kan[0], d2_kan[1]-2*scale), (d2_kan[0], d2_kan[1]-22*scale), (d1_kan[0], d1_kan[1]-22*scale)], max(1, int(scale)))

    cx_r, cy_r = iso_pt(cx_b, y_atap, 35 * scale, 35 * scale) 
    
    # Helipad dibesarkan dan diposisikan di tengah
    cx_heli = cx_r
    cy_heli = cy_r + 25 * scale
    gambar_blok(layar, cx_heli, cy_heli, 50 * scale, 25 * scale, 4 * scale, HELIPAD_SIDE, HELIPAD_SIDE, HELIPAD_TOP)
    
    cx_ht, cy_ht = cx_r, cy_r - 4 * scale
    
    # Perbesar logo "H" sedikit
    p1, p2 = iso_pt(cx_ht, cy_ht, 10 * scale, -5 * scale), iso_pt(cx_ht, cy_ht, -10 * scale, -5 * scale)
    pygame.draw.line(layar, KUNING_HELI, p1, p2, max(1, int(4*scale)))
    p3, p4 = iso_pt(cx_ht, cy_ht, 10 * scale, 5 * scale), iso_pt(cx_ht, cy_ht, -10 * scale, 5 * scale)
    pygame.draw.line(layar, KUNING_HELI, p3, p4, max(1, int(4*scale)))
    p5, p6 = iso_pt(cx_ht, cy_ht, 0, -5 * scale), iso_pt(cx_ht, cy_ht, 0, 5 * scale)
    pygame.draw.line(layar, KUNING_HELI, p5, p6, max(1, int(4*scale)))

    ax, ay = iso_pt(cx_b, y_atap, 10 * scale, 60 * scale)
    gambar_blok(layar, ax, ay, 10 * scale, 5 * scale, 15 * scale, TANAH_KIRI, TANAH_KANAN, (230,230,230))
    pygame.draw.line(layar, (150,150,150), (ax, ay-15*scale), (ax, ay-90*scale), max(1, int(2*scale)))
    pygame.draw.circle(layar, (255,50,50), (ax, ay-90*scale), max(1, int(4*scale)))


# --- CLASS WRAPPER UNTUK OOP ---
class Gedung:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.scale = 1.0
        
    def render(self, screen):
        scale = getattr(self, 'scale', 1.0)
        render_gedung(screen, self.x, self.y, scale=scale)
