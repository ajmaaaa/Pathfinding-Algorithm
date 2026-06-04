import pygame
import sys

def render_lampu(screen, x, y, scale=0.25):
    surf = pygame.Surface((400, 600), pygame.SRCALPHA)
    _render_lampu_internal(surf, 200, 550)
    w, h = surf.get_size()
    scaled = pygame.transform.smoothscale(surf, (int(w * scale), int(h * scale)))
    screen.blit(scaled, (x - int(200 * scale), y - int(550 * scale)))

def _render_lampu_internal(screen, x, y):
    """
    Fungsi Menggambar Lampu Jalan Premium Vektor Kartun.
    - Bayangan berbentuk siluet tiang lengkap di atas tanah (Proyeksi Diagonal).
    - Bola lampu keluar dari pitting/kap lampu secara penuh mendatar ke bawah.
    (x, y) = Titik koordinat tengah bawah dari alas lampu yang menyentuh tanah.
    """
    
    # ==========================================
    # 1. REALISTIC POLE SILHOUETTE SHADOW (Bayangan Berbentuk Tiang)
    # ==========================================
    # Membuat canvas transparan khusus untuk menggambar siluet bayangan tiang di tanah
    shadow_surf = pygame.Surface((500, 300), pygame.SRCALPHA)
    S_COLOR = (43, 53, 65, 50)  # Warna bayangan transparan (semi-dark grey-blue)
    
    # Titik awal bayangan pada canvas lokal (disesuaikan dengan posisi kaki tiang asli)
    bx, by = 60, 200
    
    # a. Bayangan Dudukan Bawah (Base)
    pygame.draw.ellipse(shadow_surf, S_COLOR, (bx - 25, by - 10, 50, 20))
    
    # b & c. Bayangan Lurus ke Kanan (Tapered Lower Base & Main Long Pole Shadow)
    pygame.draw.polygon(shadow_surf, S_COLOR, [
        (bx, by - 5), (bx, by + 5),
        (bx + 260, by + 5), (bx + 260, by - 5)
    ])
    
    # d. Bayangan Lengkungan Atas & Kap Lampu (Curve Hook & Cap Shadow)
    pygame.draw.circle(shadow_surf, S_COLOR, (bx + 275, by), 12)
    pygame.draw.circle(shadow_surf, S_COLOR, (bx + 290, by), 15)
    
    # Blit seluruh bayangan tiang ke layar utama dengan offset posisi kaki
    screen.blit(shadow_surf, (x - bx, y - by))

    # ==========================================
    # 2. DEFINISI PALETTE WARNA LOGAM (Slate Blue 3D)
    # ==========================================
    C_DARK   = (43, 53, 65)     # Sisi bayangan gelap logam (Kanan)
    C_MID    = (64, 78, 96)     # Warna dasar logam (Tengah)
    C_LIGHT  = (106, 124, 146)  # Sisi pantulan cahaya logam (Kiri)
    C_PITTING= (30, 38, 48)     # Warna hitam/gelap fitting/pitting tempat sekrup lampu
    C_GLOW_1 = (255, 255, 230)  # Inti lampu pijar terang (Putih Susu)
    C_GLOW_2 = (254, 230, 110)  # Warna bodi luar bohlam (Kuning Hangat)
    
    # ==========================================
    # 3. BAGIAN ALAS DAN TIANG BAWAH (Base Pedestal)
    # ==========================================
    # Dudukan paling bawah (Cylinder Base)
    pygame.draw.ellipse(screen, C_DARK, (x - 22, y - 12, 44, 12))
    pygame.draw.ellipse(screen, C_MID, (x - 22, y - 15, 44, 12))
    pygame.draw.ellipse(screen, C_LIGHT, (x - 19, y - 14, 38, 9))
    
    # Tiang Selubung Bawah (Lower Tapered Pillar)
    pygame.draw.polygon(screen, C_MID, [(x - 14, y - 12), (x + 14, y - 12), (x + 9, y - 90), (x - 9, y - 90)])
    pygame.draw.polygon(screen, C_LIGHT, [(x - 14, y - 12), (x - 5, y - 12), (x - 3, y - 90), (x - 9, y - 90)])
    pygame.draw.polygon(screen, C_DARK, [(x + 4, y - 12), (x + 14, y - 12), (x + 9, y - 90), (x + 3, y - 90)])

    # Cincin Pembatas / Ornamen Tengah (Collar Ring)
    pygame.draw.ellipse(screen, C_DARK, (x - 11, y - 94, 22, 8))
    pygame.draw.ellipse(screen, C_MID, (x - 11, y - 96, 22, 8))
    pygame.draw.ellipse(screen, C_LIGHT, (x - 9, y - 96, 18, 5))

    # ==========================================
    # 4. TIANG VERTIKAL UTAMA (Main Slender Pole)
    # ==========================================
    pygame.draw.rect(screen, C_MID, (x - 6, y - 420, 12, 326))
    pygame.draw.rect(screen, C_LIGHT, (x - 6, y - 420, 4, 326))
    pygame.draw.rect(screen, C_DARK, (x + 2, y - 420, 4, 326))

    # ==========================================
    # 5. LENGKUKAN ATAS TIANG (The Curve Hook)
    # ==========================================
    R = 52
    cx = x - R
    cy = y - 420
    
    for i in range(1040):
        px = (x - 104) + i * 0.1
        dx = px - cx
        if R**2 - dx**2 >= 0:
            dy = (R**2 - dx**2)**0.5
            py = cy - dy
            pygame.draw.circle(screen, C_DARK, (int(px + 1), int(py + 1)), 6)
            pygame.draw.circle(screen, C_MID, (int(px), int(py)), 6)
            pygame.draw.circle(screen, C_LIGHT, (int(px - 1), int(py - 1)), 4)

    # ==========================================
    # 6. KAP LAMPU (The Dome Shade)
    # ==========================================
    lx = x - 104
    ly = y - 420

    # Dudukan kecil kap lampu (Top Cap Collar)
    pygame.draw.rect(screen, C_DARK, (lx - 6, ly, 14, 8))
    pygame.draw.rect(screen, C_MID, (lx - 6, ly, 11, 8))
    pygame.draw.rect(screen, C_LIGHT, (lx - 6, ly, 4, 8))

    # Kubah Utama Kap Lampu (Shade Dome)
    for h in range(18):
        w = 12 + (h * 1.8)
        curr_y = ly + 8 + h
        pygame.draw.line(screen, C_DARK, (int(lx - w), curr_y), (int(lx + w), curr_y), 1)
        pygame.draw.line(screen, C_MID, (int(lx - w), curr_y), (int(lx + w - 3), curr_y), 1)
        pygame.draw.line(screen, C_LIGHT, (int(lx - w), curr_y), (int(lx - w + 5), curr_y), 1)

    # List Lingkar Bawah Kap Lampu (Bottom Rim Shade)
    pygame.draw.ellipse(screen, C_DARK, (lx - 23, ly + 22, 46, 10))
    pygame.draw.ellipse(screen, C_MID, (lx - 23, ly + 20, 46, 10))
    pygame.draw.ellipse(screen, C_LIGHT, (lx - 21, ly + 21, 42, 6))

    # ==========================================
    # 7. PITTING LAMPU & BOHLAM YANG KELUAR MENONJOL
    # ==========================================
    # Membuat Ulir/Pitting Leher Lampu (Soket) keluar dari bawah kap penutup
    pygame.draw.rect(screen, C_PITTING, (lx - 8, ly + 26, 16, 12))
    pygame.draw.ellipse(screen, (70, 80, 95), (lx - 8, ly + 34, 16, 6))
    
    # Menurunkan posisi pusat bola lampu (ly + 54) agar keluar penuh dari pitting
    BY = ly + 54
    R_BULB = 22

    # Efek Aura Cahaya Radial yang mengikuti posisi lampu baru di bawah
    glow_surf = pygame.Surface((200, 200), pygame.SRCALPHA)
    for r_glow in range(80, 0, -4):
        alpha = int(45 * (1.0 - r_glow / 80))
        pygame.draw.circle(glow_surf, (254, 230, 110, alpha), (100, 100), r_glow)
    screen.blit(glow_surf, (lx - 100, BY - 100))

    # Menggambar fisik Bola Lampu Kaca yang menggantung menonjol ke bawah
    for r_b in range(R_BULB, 0, -1):
        factor = r_b / float(R_BULB)
        r_c = int(C_GLOW_1[0] + (C_GLOW_2[0] - C_GLOW_1[0]) * factor)
        g_c = int(C_GLOW_1[1] + (C_GLOW_2[1] - C_GLOW_1[1]) * factor)
        b_c = int(C_GLOW_1[2] + (C_GLOW_2[2] - C_GLOW_1[2]) * factor)
        
        # Titik refleksi kilau 3D (Specular Highlight) digeser ke atas-kiri dalam bola
        ox = int((1.0 - factor) * -5)
        oy = int((1.0 - factor) * -5)
        pygame.draw.circle(screen, (r_c, g_c, b_c), (lx + ox, BY + oy), r_b)