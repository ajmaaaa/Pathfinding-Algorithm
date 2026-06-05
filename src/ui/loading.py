import pygame
import threading
import math
from config import get_system_theme
from src.ui.hud import get_font

def show_loading_screen(screen, generate_func=None):
    theme = get_system_theme()
    
    if generate_func is None:
        pygame.event.pump()
        W, H = screen.get_size()
        
        if theme == 'dark':
            bg_color = (15, 23, 42)      # Slate 900
            card_bg = (30, 41, 59)       # Slate 800
            card_border = (51, 65, 85)   # Slate 700
            text_color = (241, 245, 249) # Slate 100
            text_dim = (148, 163, 184)   # Slate 400
            accent = (96, 165, 250)      # Light Blue
        else:
            bg_color = (248, 250, 252)   # Slate 50
            card_bg = (255, 255, 255)    # White
            card_border = (226, 232, 240) # Slate 200
            text_color = (15, 23, 42)    # Slate 900
            text_dim = (100, 116, 139)   # Slate 500
            accent = (37, 99, 235)       # Blue 600
            
        screen.fill(bg_color)
        
        card_w, card_h = 420, 260
        card_x = (W - card_w) // 2
        card_y = (H - card_h) // 2
        
        for i in range(6):
            shadow_surf = pygame.Surface((card_w + i*2, card_h + i*2), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surf, (0, 0, 0, 8 - i), (0, 0, card_w + i*2, card_h + i*2), border_radius=18 + i)
            screen.blit(shadow_surf, (card_x - i, card_y - i + 2))
            
        pygame.draw.rect(screen, card_bg, (card_x, card_y, card_w, card_h), border_radius=16)
        pygame.draw.rect(screen, card_border, (card_x, card_y, card_w, card_h), 2, border_radius=16)
        
        spinner_r = 28
        spinner_cx = W // 2
        spinner_cy = card_y + 70
        pygame.draw.circle(screen, card_border, (spinner_cx, spinner_cy), spinner_r, 4)
        
        arc_rect = pygame.Rect(spinner_cx - spinner_r, spinner_cy - spinner_r, spinner_r * 2, spinner_r * 2)
        pygame.draw.arc(screen, accent, arc_rect, math.radians(45), math.radians(225), 5)
        
        title_font = get_font(18, bold=True)
        text_title = title_font.render("Menyiapkan Kota", True, text_color)
        screen.blit(text_title, (W // 2 - text_title.get_width() // 2, card_y + 130))
        
        desc_font = get_font(11, bold=False)
        desc_text = desc_font.render("Membangun jalan & gedung prosedur...", True, text_dim)
        screen.blit(desc_text, (W // 2 - desc_text.get_width() // 2, card_y + 165))
        
        line_w = 120
        line_x = W // 2 - line_w // 2
        line_y = card_y + 205
        pygame.draw.rect(screen, card_border, (line_x, line_y, line_w, 4), border_radius=2)
        pygame.draw.rect(screen, accent, (line_x + 30, line_y, 60, 4), border_radius=2)
        
        pygame.display.flip()
        return None
        
    # Threaded mode: compile map in background, keep GUI responsive at 10 FPS
    result = [None]
    exception = [None]
    
    def worker():
        try:
            result[0] = generate_func()
        except Exception as e:
            exception[0] = e
            
    thread = threading.Thread(target=worker)
    thread.daemon = True
    thread.start()
    
    clock = pygame.Clock()
    angle = 0.0
    
    while thread.is_alive():
        dt = clock.tick(10)  # 10 FPS to prevent GIL contention
        angle = (angle + dt * 0.18) % 360
        pulse = math.sin(pygame.time.get_ticks() * 0.003) * 0.5 + 0.5
        
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                import sys
                sys.exit()
                
        W, H = screen.get_size()
        
        if theme == 'dark':
            bg_color = (15, 23, 42)      # Slate 900
            card_bg = (30, 41, 59)       # Slate 800
            card_border = (51, 65, 85)   # Slate 700
            text_color = (241, 245, 249) # Slate 100
            text_dim = (148, 163, 184)   # Slate 400
            accent = (96, 165, 250)      # Light Blue
        else:
            bg_color = (248, 250, 252)   # Slate 50
            card_bg = (255, 255, 255)    # White
            card_border = (226, 232, 240) # Slate 200
            text_color = (15, 23, 42)    # Slate 900
            text_dim = (100, 116, 139)   # Slate 500
            accent = (37, 99, 235)       # Blue 600
            
        screen.fill(bg_color)
        
        card_w, card_h = 420, 260
        card_x = (W - card_w) // 2
        card_y = (H - card_h) // 2
        
        for i in range(6):
            shadow_surf = pygame.Surface((card_w + i*2, card_h + i*2), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surf, (0, 0, 0, 8 - i), (0, 0, card_w + i*2, card_h + i*2), border_radius=18 + i)
            screen.blit(shadow_surf, (card_x - i, card_y - i + 2))
            
        pygame.draw.rect(screen, card_bg, (card_x, card_y, card_w, card_h), border_radius=16)
        pygame.draw.rect(screen, card_border, (card_x, card_y, card_w, card_h), 2, border_radius=16)
        
        spinner_r = 28
        spinner_cx = W // 2
        spinner_cy = card_y + 70
        pygame.draw.circle(screen, card_border, (spinner_cx, spinner_cy), spinner_r, 4)
        
        arc_rect = pygame.Rect(spinner_cx - spinner_r, spinner_cy - spinner_r, spinner_r * 2, spinner_r * 2)
        start_rad = math.radians(angle)
        end_rad = math.radians(angle + 120)
        pygame.draw.arc(screen, accent, arc_rect, start_rad, end_rad, 5)
        
        title_font = get_font(18, bold=True)
        text_title = title_font.render("Menyiapkan Kota", True, text_color)
        screen.blit(text_title, (W // 2 - text_title.get_width() // 2, card_y + 130))
        
        desc_font = get_font(11, bold=False)
        pulse_alpha = int(120 + pulse * 135)
        
        desc_text = desc_font.render("Membangun jalan & gedung prosedur...", True, text_dim)
        desc_surf = pygame.Surface(desc_text.get_size(), pygame.SRCALPHA)
        desc_surf.blit(desc_text, (0, 0))
        desc_surf.fill((255, 255, 255, pulse_alpha), special_flags=pygame.BLEND_RGBA_MULT)
        
        screen.blit(desc_surf, (W // 2 - desc_text.get_width() // 2, card_y + 165))
        
        line_w = 120
        line_x = W // 2 - line_w // 2
        line_y = card_y + 205
        pygame.draw.rect(screen, card_border, (line_x, line_y, line_w, 4), border_radius=2)
        
        active_w = int(line_w * (0.3 + 0.4 * math.sin(pygame.time.get_ticks() * 0.005 + 1.0)))
        active_x = line_x + (line_w - active_w) // 2
        pygame.draw.rect(screen, accent, (active_x, line_y, active_w, 4), border_radius=2)
        
        pygame.display.flip()
        
    if exception[0] is not None:
        raise exception[0]
        
    return result[0]