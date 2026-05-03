import pygame
import random
import math
from config import C, RW
from src.ui.hud import get_font

class ElseRenderer:
    def __init__(self, screen, cam):
        self.screen = screen
        self.cam = cam
        self.decorations = []

        self.cat_img = pygame.image.load('cat.png').convert_alpha()

    def _ws(self, wx, wy):
        return self.cam.world_to_screen(wx, wy)

    def generate_decorations(self, city):  # --- ini tambahan auriel ---
        """Menghasilkan koordinat dekorasi dengan Algoritma Spatial Clearance Optimal"""
        self.decorations = []
        if not city or 'nodes' not in city: return
        
        nodes = city['nodes']
        buildings = city.get('buildings', [])
        roundabouts = city.get('roundabouts', [])
        
        # --- 1. FITUR KHUSUS: PASTI MUNCUL DI TENGAH BUNDARAN ---
        for rb in roundabouts:
            dec_type = random.choice(['flower_patch', 'cat'])
            if dec_type == 'flower_patch':
                color = random.choice([(231, 76, 60), (255, 119, 255), (155, 89, 182)])
                patch = []
                offsets = [(0, 0), (-12, -12), (12, -8), (-8, 12)]
                for i in range(random.randint(2, 4)):
                    ox, oy = offsets[i]
                    patch.append({'wx': rb.x + ox, 'wy': rb.y + oy})
                    
                self.decorations.append({
                    'type': 'flower_patch', 'wx': rb.x, 'wy': rb.y,
                    'patch': patch, 'color': color
                })
            elif dec_type == 'cat':
                self.decorations.append({'type': 'cat', 'wx': rb.x, 'wy': rb.y})

        # --- 2. PENYEBARAN DI RUANG HIJAU (Taman Kota) ---
        attempts = 0
        while len(self.decorations) < 45 and attempts < 2000:
            attempts += 1
            base_node = random.choice(nodes)
            
            radius = random.uniform(50, 250)
            angle = random.uniform(0, math.pi * 2)
            
            bx = base_node.x + math.cos(angle) * radius
            by = base_node.y + math.sin(angle) * radius
            
            aman = True
            
            # Sensor Jalan
            for n in nodes:
                if math.hypot(bx - n.x, by - n.y) < 65:
                    aman = False
                    break
            if not aman: continue
            
            # Sensor Bangunan
            for b in buildings:
                if math.hypot(bx - b['x'], by - b['y']) < 120 * b['scale']:
                    aman = False
                    break
            if not aman: continue
            
            # Sensor Dekorasi Lain
            for dec in self.decorations:
                if math.hypot(bx - dec['wx'], by - dec['wy']) < 120:
                    aman = False
                    break
            if not aman: continue
            
            # LOLOS SENSOR
            dec_type = random.choice(['flower_patch', 'cat'])
            
            if dec_type == 'flower_patch':
                color = random.choice([(231, 76, 60), (255, 119, 255), (155, 89, 182)])
                patch = []
                offsets = [(0, 0), (-35, -25), (35, -15), (-15, 35)]
                for i in range(random.randint(2, 4)):
                    ox, oy = offsets[i]
                    patch.append({'wx': bx + ox, 'wy': by + oy})
                    
                self.decorations.append({
                    'type': 'flower_patch', 'wx': bx, 'wy': by,
                    'patch': patch, 'color': color
                })
            elif dec_type == 'cat':
                self.decorations.append({'type': 'cat', 'wx': bx, 'wy': by})

    def draw_decorations(self):
        sc = self.cam.zoom
        if sc < 0.05: return 
        
        for dec in self.decorations:
            if dec['type'] == 'flower_patch':
                for f in dec['patch']:
                    sx, sy = self._ws(f['wx'], f['wy'])
                    
                    if sx < -50 or sx > self.screen.get_width() + 50 or sy < -50 or sy > self.screen.get_height() + 50:
                        continue
                    
                    radius = max(3, int(12 * sc))
                    stem_len = max(6, int(25 * sc))
                    
                    pygame.draw.line(self.screen, (46, 204, 113), (sx, sy), (sx, sy + stem_len), max(2, int(3 * sc)))
                    pygame.draw.circle(self.screen, dec['color'], (sx, sy - radius), radius)
                    pygame.draw.circle(self.screen, dec['color'], (sx, sy + radius), radius)
                    pygame.draw.circle(self.screen, dec['color'], (sx - radius, sy), radius)
                    pygame.draw.circle(self.screen, dec['color'], (sx + radius, sy), radius)
                    pygame.draw.circle(self.screen, (241, 196, 15), (sx, sy), int(radius * 0.8))

            elif dec['type'] == 'cat':
                sx, sy = self._ws(dec['wx'], dec['wy'])
                
                if sx < -50 or sx > self.screen.get_width() + 50 or sy < -50 or sy > self.screen.get_height() + 50:
                    continue

                # --- RENDER GAMBAR KUCING ---
                base_size = 50
                scaled_size = max(5, int(base_size * sc))
                
                # Skalakan gambar dengan smoothscale agar tidak pecah
                scaled_img = pygame.transform.smoothscale(self.cat_img, (scaled_size, scaled_size))
                
                # Pusatkan gambar persis di titik (sx, sy)
                img_rect = scaled_img.get_rect(center=(sx, sy))
                
                # Tempelkan ke layar
                self.screen.blit(scaled_img, img_rect)

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