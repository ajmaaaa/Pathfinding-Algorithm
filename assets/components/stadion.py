import pygame
import sys
import math

def draw_cylinder(surface, color_top, color_side, rect, depth, outline=False, outline_color=(0,0,0)):
    """Fungsi menggambar silinder 3D (Base/Dinding) dengan opsi garis batas"""
    x, y, w, h = rect
    
    pygame.draw.ellipse(surface, color_side, (x, y + depth, w, h))
    pygame.draw.rect(surface, color_side, (x, y + h / 2, w, depth + 1))
    
    if outline:
        pygame.draw.ellipse(surface, outline_color, (x, y + depth, w, h), 1)
        pygame.draw.line(surface, outline_color, (x, y + h/2), (x, y + h/2 + depth), 1)
        pygame.draw.line(surface, outline_color, (x + w - 1, y + h/2), (x + w - 1, y + h/2 + depth), 1)

    pygame.draw.ellipse(surface, color_top, (x, y, w, h))
    if outline:
        pygame.draw.ellipse(surface, outline_color, (x, y, w, h), 1)

def draw_stadion(screen, x, y, width=800, height=650):
    """
    Fungsi utama untuk merender Stadium Persegi Panjang dengan Border Radius (Rounded Rectangle).
    Tampilannya sangat rapi, modern, dan tidak lancip.
    """
    cx, cy = x, y
    s = min(width, height) / 500.0  # Skala dinamis

    # --- PALET WARNA ---
    base_top = (75, 130, 205)       
    base_left = (55, 110, 185)
    base_right = (35, 75, 150)       
    wall_top = (245, 248, 255)      
    wall_left = (210, 220, 240)
    wall_right = (180, 190, 215)     
    glass_color = (100, 200, 255)   
    roof_line = (210, 220, 235)     
    
    seat_colors = [
        (65, 120, 210),   
        (50, 100, 185),   
        (35, 80, 160),    
        (25, 60, 130)     
    ]

    sy = cy - 10 * s  # Level permukaan referensi

    def iso_pt(x_3d, y_3d, z_offset):
        return (cx + (y_3d - x_3d) * 2.2, sy + (x_3d + y_3d) * 1.1 + z_offset)

    def get_rounded_pts(L, W, R, z_offset):
        """Membuat titik-titik untuk Persegi Panjang dengan Sudut Melengkung (Border Radius) dalam 3D"""
        pts = []
        # Sudut Bawah (0-90)
        for a in range(0, 90, 10):
            rad = math.radians(a)
            pts.append(iso_pt(L-R + math.cos(rad)*R, W-R + math.sin(rad)*R, z_offset))
        # Sudut Kiri (90-180)
        for a in range(90, 180, 10):
            rad = math.radians(a)
            pts.append(iso_pt(-L+R + math.cos(rad)*R, W-R + math.sin(rad)*R, z_offset))
        # Sudut Atas (180-270)
        for a in range(180, 270, 10):
            rad = math.radians(a)
            pts.append(iso_pt(-L+R + math.cos(rad)*R, -W+R + math.sin(rad)*R, z_offset))
        # Sudut Kanan (270-360)
        for a in range(270, 360, 10):
            rad = math.radians(a)
            pts.append(iso_pt(L-R + math.cos(rad)*R, -W+R + math.sin(rad)*R, z_offset))
        return pts

    def draw_iso_rounded_box(L, W, R, H, z_base, c_top, c_left, c_right, glass_lines=0):
        """Menggambar blok 3D dengan sudut melengkung dan pencahayaan otomatis"""
        pts_top = get_rounded_pts(L, W, R, z_base - H)
        pts_bot = get_rounded_pts(L, W, R, z_base)
        
        N = len(pts_top)
        # Menggambar dinding vertikal hanya pada sisi yang menghadap ke depan
        for i in range(N):
            p1 = pts_top[i]
            p2 = pts_top[(i+1)%N]
            p3 = pts_bot[(i+1)%N]
            p4 = pts_bot[i]
            
            # Jika sisi bergerak dari Kiri ke Kanan di layar, berarti sisi tersebut menghadap depan
            if p1[0] < p2[0]:  
                color = c_left if p2[1] > p1[1] else c_right
                pygame.draw.polygon(screen, color, [p1, p2, p3, p4])
                pygame.draw.line(screen, (max(0, color[0]-15), max(0, color[1]-15), max(0, color[2]-15)), p3, p4, 1)

        # Menggambar permukaan atas
        pygame.draw.polygon(screen, c_top, pts_top)
        
        # Garis jendela kaca opsional
        if glass_lines > 0:
            for z_off in [12*s, 24*s, 36*s][:glass_lines]:
                pts_glass = get_rounded_pts(L, W, R, z_base - H + z_off)
                for i in range(N):
                    p1 = pts_glass[i]
                    p2 = pts_glass[(i+1)%N]
                    if p1[0] < p2[0]:
                        pygame.draw.line(screen, glass_color, p1, p2, max(1, int(2.5*s)))

    # 1. ALAS BIRU RAKSASA (Rounded Rectangle)
    base_z = 30 * s
    draw_iso_rounded_box(85*s, 67*s, 25*s, 1*s, base_z, (195, 200, 205), (175, 180, 185), (155, 160, 165))


    # 2. PILAR PENYANGGA BELAKANG (San Siro Style Corner Towers)
    pillar_r = 8 * s
    stadium_z = base_z - 20 * s  # Terrace level
    stadium_h = 45 * s
    pillar_d = stadium_h         # Reach from roof down to terrace
    
    # Sudut Atas (Top)
    p_cx, p_cy = iso_pt(-65*s, -47*s, stadium_z - stadium_h)
    draw_cylinder(screen, wall_top, wall_right, (p_cx - pillar_r, p_cy - pillar_r*0.6, pillar_r*2, pillar_r*1.2), pillar_d)

    # 3. DINDING STADIUM UTAMA (Rounded Rectangle dengan 3 garis kaca)
    draw_iso_rounded_box(70*s, 52*s, 20*s, stadium_h, stadium_z, wall_top, wall_left, wall_right, glass_lines=3)

    # 4. ATAP STADIUM (Pola Garis Konsentris)
    for z_off in [4*s, 9*s, 14*s]:
        pts_roof = get_rounded_pts(70*s - z_off, 52*s - z_off, max(4*s, 20*s - z_off), stadium_z - stadium_h)
        pygame.draw.polygon(screen, roof_line, pts_roof, max(1, int(1.5*s)))

    # 5. LUBANG DALAM & TRIBUN STADIUM
    iw, ih, ir = 54*s, 36*s, 12*s
    
    # Ketebalan atap menurun ke dalam
    rim_pts = get_rounded_pts(iw, ih, ir, stadium_z - stadium_h)
    pygame.draw.polygon(screen, (170, 180, 200), rim_pts)
    pygame.draw.polygon(screen, (100, 110, 130), rim_pts, max(1, int(1.5*s)))

    # Tribun berundak dengan border radius
    for i, color in enumerate(seat_colors):
        shrink = (i * 5) * s
        z_drop = 6*s + i * 8*s
        seat_pts = get_rounded_pts(iw - shrink, ih - shrink, max(2*s, ir - shrink), stadium_z - stadium_h + z_drop)
        pygame.draw.polygon(screen, color, seat_pts)
        pygame.draw.polygon(screen, (15, 30, 80), seat_pts, max(1, int(1.5*s)))

    # 6. LAPANGAN HIJAU (Rounded Rectangle)
    pitch_L, pitch_W = 34 * s, 16 * s
    pitch_R = 4 * s
    pitch_z = stadium_z - stadium_h + 6*s + 4*8*s + 2*s 

    for dp, c_pitch in [(0, (40, 110, 40)), (1, (60, 150, 50)), (2, (80, 175, 70))]:
        p_pts = get_rounded_pts(pitch_L - dp*s, pitch_W - dp*s, max(1*s, pitch_R - dp*s), pitch_z)
        pygame.draw.polygon(screen, c_pitch, p_pts)

    # Markah Lapangan
    pitch_line = (235, 255, 235)
    line_thick = max(1, int(1.2*s))
    
    # Garis Sentuh (Touchlines melengkung)
    touch_pts = get_rounded_pts(pitch_L - 3*s, pitch_W - 3*s, max(1*s, pitch_R - 1*s), pitch_z)
    pygame.draw.polygon(screen, pitch_line, touch_pts, line_thick)
    
    # Garis Tengah
    pygame.draw.line(screen, pitch_line, iso_pt(0, -pitch_W+3*s, pitch_z), iso_pt(0, pitch_W-3*s, pitch_z), line_thick)
    
    # Lingkaran Tengah
    pygame.draw.ellipse(screen, pitch_line, (cx - 10*s, sy + pitch_z - 5*s, 20*s, 10*s), line_thick)
    
    # Kotak Penalti Kiri
    pygame.draw.polygon(screen, pitch_line, [
        iso_pt(-pitch_L+3*s, -6*s, pitch_z), iso_pt(-pitch_L+10*s, -6*s, pitch_z), 
        iso_pt(-pitch_L+10*s, 6*s, pitch_z), iso_pt(-pitch_L+3*s, 6*s, pitch_z)
    ], line_thick)
    
    # Kotak Penalti Kanan
    pygame.draw.polygon(screen, pitch_line, [
        iso_pt(pitch_L-3*s, -6*s, pitch_z), iso_pt(pitch_L-10*s, -6*s, pitch_z), 
        iso_pt(pitch_L-10*s, 6*s, pitch_z), iso_pt(pitch_L-3*s, 6*s, pitch_z)
    ], line_thick)

    # 7. PILAR PENYANGGA DEPAN & SAMPING (Sudut Kanan, Bawah, Kiri)
    for px_3d, py_3d in [(65*s, -47*s), (65*s, 47*s), (-65*s, 47*s)]:
        p_cx, p_cy = iso_pt(px_3d, py_3d, stadium_z - stadium_h)
        draw_cylinder(screen, wall_top, wall_right, (p_cx - pillar_r, p_cy - pillar_r*0.6, pillar_r*2, pillar_r*1.2), pillar_d)
