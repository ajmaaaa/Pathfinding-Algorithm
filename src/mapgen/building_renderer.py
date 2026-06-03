import pygame
from config import C, RIBBON_H
from assets.components.component_registry import get_render_fn

class BuildingRenderer:
    def __init__(self, screen, cam):
        self.screen = screen
        self.cam = cam
        self.W = screen.get_width()
        self.H = screen.get_height() - RIBBON_H
        self._surface_cache = {}
        self._scaled_cache = {}

    def _ws(self, wx, wy):
        return self.cam.world_to_screen(wx, wy)

    def _get_cached_surface(self, b_type):
        if b_type in self._surface_cache:
            return self._surface_cache[b_type]
            
        render_fn = get_render_fn(b_type)
        
        # Buat surface transparan besar untuk menangkap hasil render komponen
        temp_w, temp_h = 4000, 4000
        temp_surf = pygame.Surface((temp_w, temp_h), pygame.SRCALPHA)
        cx, cy = 2000, 2000  # Anchor diletakkan di tengah bawah
        
        # Jalankan fungsi render dari registry
        render_fn(temp_surf, cx, cy)
        
        # Crop surface agar pas dengan ukuran aktual gambar (menghapus area kosong)
        rect = temp_surf.get_bounding_rect()
        
        if rect.width == 0 or rect.height == 0:
            # Fallback jika ternyata render kosong
            rect = pygame.Rect(cx-1, cy-1, 2, 2)
            
        cropped = temp_surf.subsurface(rect).copy()
        
        # Hitung titik anchor relatif terhadap gambar yang sudah di-crop
        anchor_x = cx - rect.x
        anchor_y = cy - rect.y
        
        self._surface_cache[b_type] = {
            'surface': cropped,
            'anchor_x': anchor_x,
            'anchor_y': anchor_y
        }
        
        return self._surface_cache[b_type]

    def draw_building(self, b):
        sc  = self.cam.zoom * b['scale']
        if sc < 0.055: return
        sx, sy = self._ws(b['x'], b['y'])
        
        # Bianglala (Ferris Wheel) has real-time animation, so it cannot be cached statically.
        if b['type'].lower() == 'bianglala':
            temp_w, temp_h = 1300, 800
            temp_surf = pygame.Surface((temp_w, temp_h), pygame.SRCALPHA)
            cx, cy = 650, 450
            
            render_fn = get_render_fn(b['type'])
            render_fn(temp_surf, cx, cy)
            
            # Use fixed bounding box crop to avoid expensive get_bounding_rect() call
            rect = pygame.Rect(cx - 580, cy - 405, 1160, 700)
            cropped = temp_surf.subsurface(rect)
            
            anchor_x = 580
            anchor_y = 405
            
            scaled_w = max(1, int(1160 * sc))
            scaled_h = max(1, int(700 * sc))
            
            draw_x = sx - int(anchor_x * sc)
            draw_y = sy - int(anchor_y * sc)
            
            margin = 100
            if (draw_x > self.W + margin or draw_x + scaled_w < -margin or
                draw_y > self.H + RIBBON_H + margin or draw_y + scaled_h < RIBBON_H - margin):
                return
                
            if abs(sc - 1.0) < 0.001:
                scaled_surf = cropped
            else:
                scaled_surf = pygame.transform.smoothscale(cropped, (scaled_w, scaled_h))
                
            self.screen.blit(scaled_surf, (draw_x, draw_y))
            return

        # Ambil surface komponen yang sudah di-cache
        cached = self._get_cached_surface(b['type'])
        base_surf = cached['surface']
        anchor_x = cached['anchor_x']
        anchor_y = cached['anchor_y']
        
        # Hitung ukuran gambar setelah diskalakan zoom
        scaled_w = max(1, int(base_surf.get_width() * sc))
        scaled_h = max(1, int(base_surf.get_height() * sc))
        
        footprint_offset_y = int(b['radius'] * self.cam.zoom)
        
        # Gambar bayangan bawah (shadow) - skip jika tipe bangunan adalah kavling (alas tanah) (DINONAKTIFKAN ATAS PERMINTAAN USER)
        # if not b['type'].lower().startswith('kavling'):
        #     shw_w = max(2, int(160 * sc)); shw_h = max(2, int(40 * sc))
        #     shw = pygame.Surface((shw_w, shw_h), pygame.SRCALPHA)
        #     pygame.draw.ellipse(shw, (0, 0, 0, 38), (0, 0, shw_w, shw_h))
        #     self.screen.blit(shw, (sx - shw_w//2, (sy + footprint_offset_y) - shw_h//2))
        
        # Posisi gambar akhir
        draw_x = sx - int(anchor_x * sc)
        draw_y = sy - int(anchor_y * sc)
        
        # Optimasi Culling: jangan render jika di luar layar
        margin = 100
        if draw_x > self.W + margin or draw_x + scaled_w < -margin: return
        if draw_y > self.H + RIBBON_H + margin or draw_y + scaled_h < RIBBON_H - margin: return
        
        # Skalakan surface dan tampilkan ke layar. Cache per zoom kecil supaya
        # generate map padat tetap ringan saat kamera diam atau bergerak pelan.
        if abs(sc - 1.0) < 0.001:
            scaled_surf = base_surf
        else:
            cache_key = (b['type'], round(sc, 2))
            scaled_surf = self._scaled_cache.get(cache_key)
            if scaled_surf is None or scaled_surf.get_size() != (scaled_w, scaled_h):
                if len(self._scaled_cache) > 220:
                    self._scaled_cache.clear()
                scaled_surf = pygame.transform.smoothscale(base_surf, (scaled_w, scaled_h))
                self._scaled_cache[cache_key] = scaled_surf
            
        self.screen.blit(scaled_surf, (draw_x, draw_y))
