import pygame
import sys

def render_pohon(screen, x, y, scale=0.6):
    surf = pygame.Surface((300, 300), pygame.SRCALPHA)
    _render_pohon_internal(surf, 150, 280)
    w, h = surf.get_size()
    scaled = pygame.transform.smoothscale(surf, (int(w * scale), int(h * scale)))
    screen.blit(scaled, (x - int(150 * scale), y - int(280 * scale)))

def _render_pohon_internal(screen, x, y):
    """
    Fungsi Menggambar Pohon Bulat Premium Vektor Kartun.
    (x, y) = Titik koordinat tengah bawah batang pohon (menyentuh tanah).
    """
    
    # ==========================================
    # 1. SOFT GROUND SHADOW (Bayangan Transparan)
    # ==========================================
    # Menggunakan permukaan ber-alpha supaya bayangan membaur sempurna dengan BG
    shadow_surf = pygame.Surface((180, 45), pygame.SRCALPHA)
    # Bayangan oval tipis bergeser sedikit ke kanan bawah sesuai arah cahaya gambar
    pygame.draw.ellipse(shadow_surf, (45, 65, 90, 55), (0, 0, 180, 45))
    screen.blit(shadow_surf, (x - 85, y - 22))

    # ==========================================
    # 2. DEFINISI PALETTE WARNA (Vector Style)
    # ==========================================
    # Warna Kayu/Batang
    W_DARK   = (102, 66, 42)    # Bayangan batang/sisi kanan
    W_MID    = (138, 93, 58)    # Warna dasar batang
    W_LIGHT  = (173, 124, 87)   # Highlight batang/sisi kiri

    # Fungsi pembantu menggambar gumpalan daun bola 3D dengan gradasi halus
    def draw_clump(cx, cy, r, light_bias=0.0):
        """
        Menggambar 1 gumpalan berbentuk bola/awan dengan efek shading volumetrik.
        light_bias: mengatur tingkat kecerahan gumpalan (minus=gelap/bawah, plus=terang/atas)
        """
        steps = 16
        for i in range(steps):
            f = i / (steps - 1)
            # Menghitung faktor warna efektif dicampur dengan bias posisi gumpalan
            eff_f = max(0.0, min(1.0, f * 0.85 + 0.15 + light_bias))
            
            # Interpolasi warna halus dari gelap ke sangat terang
            if eff_f < 0.25:
                t = eff_f / 0.25
                color = (int(32 + (52-32)*t), int(72 + (112-72)*t), int(28 + (42-28)*t))
            elif eff_f < 0.60:
                t = (eff_f - 0.25) / 0.35
                color = (int(52 + (88-52)*t), int(112 + (168-112)*t), int(42 + (52-42)*t))
            elif eff_f < 0.85:
                t = (eff_f - 0.60) / 0.25
                color = (int(88 + (132-88)*t), int(168 + (208-168)*t), int(52 + (62-52)*t))
            else:
                t = (eff_f - 0.85) / 0.15
                color = (int(132 + (172-132)*t), int(208 + (232-208)*t), int(62 + (82-62)*t))
            
            # Mengecilkan ukuran lingkaran seiring mendekati highlight pusat
            curr_r = int(r * (1.0 - f * 0.18))
            if curr_r < 1: curr_r = 1
            
            # Menggeser pusat lingkaran ke arah atas-kiri (menuju arah datang cahaya)
            ox = int(f * r * 0.24 * -0.8)
            oy = int(f * r * 0.24 * -0.9)
            
            pygame.draw.circle(screen, color, (cx + ox, cy + oy), curr_r)


    # ==========================================
    # 3. KANOPI BELAKANG (Deep Fill Layer)
    # ==========================================
    # Digambar di belakang struktur batang agar tidak ada celah kosong
    draw_clump(x, y - 130, 65, light_bias=-0.15)
    draw_clump(x - 35, y - 145, 50, light_bias=-0.1)
    draw_clump(x + 35, y - 145, 50, light_bias=-0.2)

    # ==========================================
    # 4. STRUKTUR BATANG, CABANG & AKAR
    # ==========================================
    # Akar Kiri (Shadow & Base)
    pygame.draw.polygon(screen, W_DARK, [(x - 26, y + 4), (x - 8, y - 25), (x, y)])
    pygame.draw.polygon(screen, W_MID, [(x - 20, y + 2), (x - 8, y - 25), (x - 4, y)])
    pygame.draw.polygon(screen, W_LIGHT, [(x - 18, y), (x - 10, y - 25), (x - 12, y)])

    # Akar Kanan (Shadow)
    pygame.draw.polygon(screen, W_DARK, [(x + 26, y + 4), (x + 8, y - 25), (x, y)])
    pygame.draw.polygon(screen, W_MID, [(x + 18, y + 2), (x + 8, y - 25), (x + 2, y)])

    # Batang Utama (Tengah)
    pygame.draw.polygon(screen, W_MID, [(x - 14, y + 2), (x + 14, y + 2), (x + 9, y - 70), (x - 9, y - 70)])
    # Highlight Batang Sisi Kiri
    pygame.draw.polygon(screen, W_LIGHT, [(x - 14, y + 2), (x - 4, y + 2), (x - 2, y - 70), (x - 9, y - 70)])
    # Shadow Batang Sisi Kanan
    pygame.draw.polygon(screen, W_DARK, [(x + 4, y + 2), (x + 14, y + 2), (x + 9, y - 70), (x + 3, y - 70)])

    # Cabang Kiri Utama
    pygame.draw.polygon(screen, W_MID, [(x - 9, y - 65), (x - 2, y - 70), (x - 24, y - 110), (x - 34, y - 105)])
    pygame.draw.polygon(screen, W_LIGHT, [(x - 9, y - 65), (x - 5, y - 67), (x - 28, y - 110), (x - 34, y - 105)])

    # Cabang Kanan Utama
    pygame.draw.polygon(screen, W_DARK, [(x + 2, y - 70), (x + 9, y - 65), (x + 34, y - 105), (x + 24, y - 110)])
    pygame.draw.polygon(screen, W_MID, [(x + 2, y - 70), (x + 5, y - 68), (x + 29, y - 109), (x + 24, y - 110)])

    # ==========================================
    # 5. KANOPI DEPAN & ATAS (Main Cloud Canopy)
    # ==========================================
    # Urutan rendering dari bawah ke atas untuk menutupi cabang secara organik
    draw_clump(x - 52, y - 120, 44, light_bias=-0.08) # Daun Kiri Bawah
    draw_clump(x + 52, y - 120, 42, light_bias=-0.22) # Daun Kanan Bawah (Lebih gelap)
    
    draw_clump(x - 58, y - 160, 48, light_bias=0.02)  # Daun Kiri Tengah
    draw_clump(x + 58, y - 160, 45, light_bias=-0.15) # Daun Kanan Tengah
    
    draw_clump(x, y - 155, 60, light_bias=0.05)       # Kubah Tengah Utama
    
    draw_clump(x - 32, y - 198, 48, light_bias=0.18)  # Daun Kiri Atas (Sangat Terang)
    draw_clump(x + 32, y - 198, 46, light_bias=0.08)  # Daun Kanan Atas
    
    draw_clump(x, y - 215, 52, light_bias=0.25)       # Pucuk Mahkota Paling Atas