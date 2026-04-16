import pygame
from config import C
from src.ui.hud import get_font

def show_loading_screen(screen):
    screen.fill((255,255,255))
    t = get_font(20, True).render("⏳ Membuat Peta...", True, C['txt_dark'])
    screen.blit(t, (screen.get_width()//2 - t.get_width()//2, screen.get_height()//2))
    pygame.display.flip()