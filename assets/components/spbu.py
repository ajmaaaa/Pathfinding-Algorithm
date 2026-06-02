import pygame

# --- PALET WARNA (TEMA SPBU / POM BENSIN) ---
WALL_L      = (245, 245, 240)   
WALL_R      = (220, 220, 215)   
WALL_TOP    = (235, 235, 230)   
ROOF_L      = (215, 45,  35)    
ROOF_R      = (175, 30,  22)    
ROOF_TOP    = (225, 55,  45)    
PILLAR_L    = (195, 195, 190)   
PILLAR_R    = (160, 160, 155)   
DISPENSER_L = (245, 185, 30)    
DISPENSER_R = (205, 150, 20)    
DISPENSER_T = (255, 205, 55)    
SCREEN_COL  = (55,  115, 195)   
ASPHALT_TOP = (125, 125, 122)   
ASPHALT_L   = (105, 105, 102)   
ASPHALT_R   = (88,  88,  85)    
MARKA_COL   = (250, 250, 190)   
ISLAND_L    = (205, 202, 196)   
ISLAND_R    = (175, 172, 166)   
ISLAND_TOP  = (218, 215, 209)   
WIN_BG      = (155, 210, 230)   
WIN_FRAME   = (255, 255, 255)   
DOOR_COL    = (100, 160, 200)   
SIGN_BG     = (215, 38,  28)    
SIGN_TEXT   = (255, 232, 50)    
LINE_COL    = (52,  52,  52)    
POLE_COL    = (155, 158, 162)   
PRICE_BG    = (28,  28,  32)    
PRICE_TEXT  = (255, 200, 0)     
GRASS       = (152, 202, 112)   
KERB_L      = (185, 182, 176)   
KERB_R      = (155, 152, 146)   
KERB_TOP    = (200, 197, 191)   
NOZZLE_COL  = (45,  45,  45)    


def render_spbu(screen, cx, cy, scale=1.0):
    def iso(x, y, z):
        scale_x, scale_y = 1.6 * scale, 0.8 * scale
        sx = cx + (x - y) * scale_x
        sy = cy + (x + y) * scale_y - z * scale
        return sx, sy

    def draw_poly(points_3d, color, outline=True):
        pts_2d = [iso(x, y, z) for x, y, z in points_3d]
        pygame.draw.polygon(screen, color, pts_2d)
        if outline:
            pygame.draw.polygon(screen, LINE_COL, pts_2d, int(2 * scale) or 1)

    def draw_block(x1, x2, y1, y2, z1, z2, c_top, c_front, c_side):
        draw_poly([(x1,y1,z2),(x2,y1,z2),(x2,y2,z2),(x1,y2,z2)], c_top)
        draw_poly([(x1,y2,z1),(x2,y2,z1),(x2,y2,z2),(x1,y2,z2)], c_front)
        draw_poly([(x2,y1,z1),(x2,y2,z1),(x2,y2,z2),(x2,y1,z2)], c_side)

    def draw_window_left(x, y, z, w=16, h=20):
        pts = [(x,y,z),(x+w,y,z),(x+w,y,z+h),(x,y,z+h)]
        draw_poly(pts, WIN_BG)
        pygame.draw.line(screen, WIN_FRAME, iso(x+w/2,y,z), iso(x+w/2,y,z+h), int(2 * scale) or 1)
        pygame.draw.line(screen, WIN_FRAME, iso(x,y,z+h/2), iso(x+w,y,z+h/2), int(2 * scale) or 1)

    def draw_window_right(x, y, z, w=16, h=20):
        pts = [(x,y,z),(x,y+w,z),(x,y+w,z+h),(x,y,z+h)]
        draw_poly(pts, WIN_BG)
        pygame.draw.line(screen, WIN_FRAME, iso(x,y+w/2,z), iso(x,y+w/2,z+h), int(2 * scale) or 1)
        pygame.draw.line(screen, WIN_FRAME, iso(x,y,z+h/2), iso(x,y+w,z+h/2), int(2 * scale) or 1)

    def draw_dispenser(x, y, z):
        W, D, H = 14, 10, 38
        draw_block(x, x+W, y, y+D, z, z+H, DISPENSER_T, DISPENSER_L, DISPENSER_R)
        sx, sy, sw, sh = x+2, y+D, W-4, 12
        draw_poly([(sx,sy,z+H-16),(sx+sw,sy,z+H-16),
                   (sx+sw,sy,z+H-4),(sx,sy,z+H-4)], SCREEN_COL)
        pygame.draw.line(screen, (100,160,230),
                         iso(sx+sw/2,sy,z+H-16), iso(sx+sw/2,sy,z+H-4), 1)
        pygame.draw.line(screen, (100,160,230),
                         iso(sx,sy,z+H-10), iso(sx+sw,sy,z+H-10), 1)
        draw_poly([(x,y+D,z+H-2),(x+W,y+D,z+H-2),
                   (x+W,y+D,z+H),(x,y+D,z+H)], SIGN_BG, outline=False)
        n1 = iso(x+W, y+D/2, z+H-8)
        n2 = iso(x+W+5, y+D/2, z+H-14)
        n3 = iso(x+W+5, y+D/2, z+H-22)
        pygame.draw.lines(screen, NOZZLE_COL, False, [n1,n2,n3], int(3 * scale) or 1)
        pygame.draw.circle(screen, NOZZLE_COL, (int(n3[0]),int(n3[1])), int(3 * scale) or 1)

    # 1. RUMPUT SEKITAR
    draw_poly([(-80,280,-2),(280,280,-2),(280,-80,-2),(-80,-80,-2)], GRASS)

    # 2. AREA ASPAL
    draw_block(0, 240, 0, 230, -3, 0, ASPHALT_TOP, ASPHALT_L, ASPHALT_R)

    for i in range(7):
        py = 15 + i * 28
        pygame.draw.line(screen, MARKA_COL, iso(0, py,1), iso(0,py+14,1), int(3 * scale) or 1)
        pygame.draw.line(screen, MARKA_COL, iso(240,py,1), iso(240,py+14,1), int(3 * scale) or 1)

    # 3. BACK KERB
    draw_block(-5, 245, -10,  0,  -3, 4, KERB_TOP, KERB_L, KERB_R)

    # 4. PRICE SIGN
    pole_x, pole_y = -25, 55
    pygame.draw.line(screen, POLE_COL, iso(pole_x, pole_y, -2), iso(pole_x, pole_y, 95), int(5 * scale) or 1)
    draw_poly([(pole_x-22,pole_y,65),(pole_x+22,pole_y,65),
               (pole_x+22,pole_y,95),(pole_x-22,pole_y,95)], PRICE_BG)
    pygame.draw.line(screen, POLE_COL, iso(pole_x-22,pole_y,79), iso(pole_x+22,pole_y,79), int(1 * scale) or 1)
    font_sm = pygame.font.SysFont("Arial", int(9 * scale), bold=True)
    for label, zl in [("PERTALITE", 88), ("PERTAMAX", 72)]:
        ts = font_sm.render(label, True, PRICE_TEXT)
        ts = pygame.transform.rotate(ts, -26.5)
        tc = iso(pole_x, pole_y, zl)
        screen.blit(ts, ts.get_rect(center=(int(tc[0]), int(tc[1]))))

    # 5. MINI-MART (Diperkecil di bagian kiri agar tiang kanan tetap di atap)
    draw_poly([(170,100,0),(240,100,0),(240,100,55),(170,100,55)], WALL_L)
    draw_poly([(240,10,0),(240,100,0),(240,100,55),(240,10,55)], WALL_R)
    draw_poly([(170,10,55),(240,10,55),(240,100,55),(170,100,55)], WALL_TOP)

    draw_poly([(170,100,55),(240,100,55),(240,100,65),(170,100,65)], SIGN_BG)
    font_big = pygame.font.SysFont("Arial", int(14 * scale), bold=True)
    txt = font_big.render("SPBU", True, SIGN_TEXT)
    txt = pygame.transform.rotate(txt, -26.5)
    jcx, jcy = iso(205, 100, 60)
    screen.blit(txt, txt.get_rect(center=(int(jcx), int(jcy))))

    draw_window_left(176, 100, 8, w=18, h=38)
    draw_window_left(198, 100, 8, w=18, h=38)

    draw_poly([(220,100,0),(236,100,0),(236,100,42),(220,100,42)], DOOR_COL)
    pygame.draw.line(screen, WIN_FRAME, iso(228,100,0), iso(228,100,42), int(2 * scale) or 1)
    pygame.draw.circle(screen, (200,200,50), (int(iso(225,100,18)[0]), int(iso(225,100,18)[1])), int(2 * scale) or 1)
    pygame.draw.circle(screen, (200,200,50), (int(iso(231,100,18)[0]), int(iso(231,100,18)[1])), int(2 * scale) or 1)

    draw_window_right(240, 20, 12, w=18, h=22)
    draw_window_right(240, 50, 12, w=18, h=22)
    draw_window_right(240, 75, 12, w=18, h=22)

    # 6. BACK PILLARS
    for tx, ty in [(22,  30)]:
        draw_block(tx-4, tx+4, ty-4, ty+4, 0, 70, PILLAR_L, PILLAR_L, PILLAR_R)
    
    # Tiang penyangga sudut kanan kanopi (berdiri di atas atap mini-mart)
    for tx, ty in [(226, 26)]:
        draw_block(tx-4, tx+4, ty-4, ty+4, 55, 70, PILLAR_L, PILLAR_L, PILLAR_R)

    # 7. ISLANDS & DISPENSERS
    Z_ISLAND = 6
    draw_block(25, 115, 100, 150, 0, Z_ISLAND, ISLAND_TOP, ISLAND_L, ISLAND_R)
    draw_dispenser(30,  110, Z_ISLAND)
    draw_dispenser(72,  110, Z_ISLAND)

    draw_block(130, 220, 100, 150, 0, Z_ISLAND, ISLAND_TOP, ISLAND_L, ISLAND_R)
    draw_dispenser(135, 110, Z_ISLAND)
    draw_dispenser(177, 110, Z_ISLAND)

    # 8. FRONT PILLARS
    for tx, ty in [(22, 195), (212, 195)]:
        draw_block(tx-4, tx+4, ty-4, ty+4, 0, 70, PILLAR_L, PILLAR_L, PILLAR_R)

    # 9. CANOPY ROOF
    ZK   = 70
    TEBAL = 10
    draw_poly([(10,20,ZK+TEBAL),(230,20,ZK+TEBAL),(230,210,ZK+TEBAL),(10,210,ZK+TEBAL)], ROOF_TOP)
    draw_poly([(10,210,ZK),(230,210,ZK),(230,210,ZK+TEBAL),(10,210,ZK+TEBAL)], ROOF_L)
    draw_poly([(230,20,ZK),(230,210,ZK),(230,210,ZK+TEBAL),(230,20,ZK+TEBAL)], ROOF_R)

    # 10. FRONT KERB
    draw_block(-5, 245, 228, 238, -3, 4, KERB_TOP, KERB_L, KERB_R)


class SPBU:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.scale = 1.0

    def render(self, screen):
        scale = getattr(self, 'scale', 1.0)
        render_spbu(screen, self.x, self.y - 160 * scale, scale=scale)

