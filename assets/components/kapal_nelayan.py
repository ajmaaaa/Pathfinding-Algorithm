import pygame

C_SHIP_RED = (150, 40, 40)
C_SHIP_DARK = (50, 50, 55)
C_SHIP_WHITE = (230, 230, 230)
C_BOX_RED = (200, 50, 50)
C_BOX_BLUE = (50, 80, 200)
C_BOX_GREEN = (50, 150, 80)
C_BOX_ORANGE = (220, 120, 40)

def render_kapal_nelayan(screen, x, y):
    # ---------------------------------------------------------
    # LAYER 3: KAPAL KARGO (The Container Cargo Ship)
    # ---------------------------------------------------------
    sx, sy = x + 10, y - 10 # Titik acuan lokal lambung kapal
    
    # Lambung bawah kapal (Merah)
    pygame.draw.polygon(screen, C_SHIP_RED, [
        (sx + 10, sy + 15), (sx + 170, sy + 15), 
        (sx + 190, sy - 5), (sx + 0, sy - 5)
    ])
    # Lambung atas kapal (Hitam Kelabu)
    pygame.draw.polygon(screen, C_SHIP_DARK, [
        (sx + 0, sy - 5), (sx + 190, sy - 5), 
        (sx + 195, sy - 22), (sx - 5, sy - 22)
    ])
    # Garis hiasan putih di badan kapal
    pygame.draw.line(screen, C_SHIP_WHITE, (sx - 3, sy - 12), (sx + 193, sy - 12), 2)
    
    # Anjungan / Kabin Komando Kapal (Superstructure) di bagian buritan (belakang)
    pygame.draw.rect(screen, C_SHIP_WHITE, (sx + 140, sy - 50, 45, 28))
    pygame.draw.rect(screen, C_SHIP_WHITE, (sx + 148, sy - 65, 30, 15))
    # Kaca jendela kabin
    pygame.draw.rect(screen, (40, 60, 80), (sx + 154, sy - 60, 8, 5))
    pygame.draw.rect(screen, (40, 60, 80), (sx + 166, sy - 60, 8, 5))
    # Cerobong Asap & Pipa Gas Kapal
    pygame.draw.rect(screen, (200, 50, 50), (sx + 168, sy - 80, 8, 15))
    pygame.draw.rect(screen, (30, 30, 30), (sx + 168, sy - 83, 8, 4))

    # Tumpukan Kontainer di Atas Dek Kapal
    # Baris bawah
    pygame.draw.rect(screen, C_BOX_RED, (sx + 15, sy - 37, 35, 15))
    pygame.draw.rect(screen, C_BOX_BLUE, (sx + 53, sy - 37, 35, 15))
    pygame.draw.rect(screen, C_BOX_GREEN, (sx + 91, sy - 37, 35, 15))
    # Baris kedua (Menumpuk di atasnya)
    pygame.draw.rect(screen, C_BOX_ORANGE, (sx + 25, sy - 52, 35, 15))
    pygame.draw.rect(screen, C_BOX_RED, (sx + 65, sy - 52, 35, 15))
    # Detail garis pintu kontainer agar realistis
    for bx in [15, 53, 91, 25, 65]:
        ox = 25 if bx in [25, 65] else 0
        h_offset = 52 if bx in [25, 65] else 37
        pygame.draw.rect(screen, (30, 30, 30), (sx + bx, sy - h_offset, 35, 15), 1)
        pygame.draw.line(screen, (30, 30, 30), (sx + bx + 17, sy - h_offset), (sx + bx + 17, sy - h_offset + 15), 1)