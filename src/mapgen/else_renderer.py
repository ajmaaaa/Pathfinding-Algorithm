import pygame
from config import C, RW
from src.ui.hud import get_font

class ElseRenderer:
    def __init__(self, screen, cam):
        self.screen = screen
        self.cam = cam
        
    def _ws(self, wx, wy):
        return self.cam.world_to_screen(wx, wy)

    def draw_pin(self, n, color, lbl):
        sx, sy = self._ws(n.x, n.y)
        sc = self.cam.zoom
        r  = max(8, int(RW*1.12*sc)); pr = max(4, int(r*0.7))
        ov = pygame.Surface((r*4, r*2), pygame.SRCALPHA)
        pygame.draw.ellipse(ov,(0,0,0,46),(r//2,r//2,r,r//3)); self.screen.blit(ov,(sx-r,sy-r//4))
        pygame.draw.circle(self.screen, color, (sx, sy-int(r*0.6)), pr)
        pygame.draw.circle(self.screen, C['white'], (sx, sy-int(r*0.6)), pr, max(2,int(4*sc)))
        pts = [(sx-int(pr*0.27), sy-int(r*0.6)), (sx+int(pr*0.27), sy-int(r*0.6)), (sx, sy+int(r*0.3))]
        pygame.draw.polygon(self.screen, color, pts)
        if sc > 0.12:
            fnt = get_font(max(8,int(pr*0.65)), bold=True)
            t   = fnt.render(lbl, True, C['white'])
            self.screen.blit(t, (sx-t.get_width()//2, sy-int(r*0.6)-t.get_height()//2))