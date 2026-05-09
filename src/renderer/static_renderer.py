import math
import os
import pygame
from config import C, RIBBON_H, RW, LP


class StaticRenderer:
    def __init__(self, screen, cam):
        self.screen, self.cam = screen, cam
        self.W, self.H = screen.get_width(), screen.get_height() - RIBBON_H
        self.show_graph = False
        self._asset_dir = None
        self._sea_assets, self._sea_scaled = {}, {}
        self._water_tile = self._water_tile_size = None
        self._setup_sea_assets()
        self._setup_sea_decorations()

    def _ws(self, wx, wy):
        return self.cam.world_to_screen(wx, wy)

    def _get_color(self, key, fallback):
        try:
            return C.get(key, fallback)
        except AttributeError:
            try:
                return C[key]
            except Exception:
                return fallback

    def _find_asset(self, names):
        base = os.path.dirname(os.path.abspath(__file__))
        folders = [
            os.path.join(base, "..", "..", "assets"), os.path.join(base, "..", "..", "asset"),
            os.path.join(os.getcwd(), "assets"), os.path.join(os.getcwd(), "asset"),
            os.path.join(base, "..", "..", "assets", "sea"), os.path.join(base, "..", "..", "asset", "sea"),
            os.path.join(os.getcwd(), "assets", "sea"), os.path.join(os.getcwd(), "asset", "sea"),
            os.path.join(base, "assets"), os.path.join(base, "asset"),
            os.path.join(base, "assets", "sea"), os.path.join(base, "asset", "sea"),
            os.path.join(base, "..", "assets"), os.path.join(base, "..", "asset"),
            os.path.join(base, "..", "assets", "sea"), os.path.join(base, "..", "asset", "sea"), base,
        ]
        for folder in map(os.path.abspath, folders):
            for name in names:
                path = os.path.join(folder, name)
                if os.path.exists(path):
                    self._asset_dir = folder
                    return path
        return None

    def _fit_surface(self, surf, max_w, max_h):
        w, h = surf.get_size()
        if w <= 0 or h <= 0:
            return surf
        r = max(0.02, min(max_w / float(w), max_h / float(h)))
        size = (max(1, int(w * r)), max(1, int(h * r)))
        return surf.convert_alpha() if size == (w, h) else pygame.transform.smoothscale(surf, size).convert_alpha()

    def _remove_edge_background(self, surf, tolerance=42):
        surf = surf.convert_alpha()
        w, h = surf.get_size()
        if w <= 2 or h <= 2:
            return surf
        corners = [surf.get_at(p) for p in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1))]
        bg = tuple(sum(getattr(c, k) for c in corners) // 4 for k in ("r", "g", "b"))
        limit, visited, stack = tolerance * 3, bytearray(w * h), []

        def add(x, y):
            idx = y * w + x
            if visited[idx]:
                return
            visited[idx] = 1
            col = surf.get_at((x, y))
            if sum(abs(v - b) for v, b in zip((col.r, col.g, col.b), bg)) <= limit:
                stack.append((x, y))

        for x in range(w):
            add(x, 0); add(x, h - 1)
        for y in range(h):
            add(0, y); add(w - 1, y)
        while stack:
            x, y = stack.pop()
            r, g, b, _ = surf.get_at((x, y))
            surf.set_at((x, y), (r, g, b, 0))
            if x > 0: add(x - 1, y)
            if x < w - 1: add(x + 1, y)
            if y > 0: add(x, y - 1)
            if y < h - 1: add(x, y + 1)
        return surf

    def _crop_alpha(self, surf, padding=2):
        w, h = surf.get_size()
        min_x, min_y, max_x, max_y = w, h, -1, -1
        for y in range(h):
            for x in range(w):
                if surf.get_at((x, y)).a > 8:
                    min_x, min_y = min(min_x, x), min(min_y, y)
                    max_x, max_y = max(max_x, x), max(max_y, y)
        if max_x < min_x or max_y < min_y:
            return surf
        min_x, min_y = max(0, min_x - padding), max(0, min_y - padding)
        max_x, max_y = min(w - 1, max_x + padding), min(h - 1, max_y + padding)
        return surf.subsurface(pygame.Rect(min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)).copy()

    def _load_sprite_asset(self, path, max_w, max_h, tolerance=42):
        try:
            surf = pygame.image.load(path).convert_alpha()
            return self._crop_alpha(self._remove_edge_background(self._fit_surface(surf, max_w, max_h), tolerance), 2)
        except Exception:
            return None

    def _setup_sea_assets(self):
        self._sea_assets, self._sea_scaled = {}, {}
        self._water_tile = self._water_tile_size = None
        items = {
            "fish_orange": (["fish_orange.jpg", "fish_orange.jpg", "fish.jpg", "ikan.jpg", "ikan.jpg"], 180, 120, 48),
            "fish_purple": (["fish_purple.jpg", "fish_purple.jpg", "fish_ungu.jpg", "fish_ungu.jpg", "ikan_ungu.jpg", "ikan_ungu.jpg"], 180, 120, 48),
            "shark_fin": (["shark_fin.jpg", "shark_fin.jpg", "sirip.jpg", "sirip.jpg", "fin.jpg", "fin.jpg", "shark.jpg", "shark.jpg", "image(277).jpg"], 135, 95, 58),
            "boat": (["boat.jpg", "boat.jpg", "kapal.jpg", "kapal.jpg", "sailboat.jpg", "sailboat.jpg", "image(278).jpg"], 210, 160, 48),
        }
        for key, (names, mw, mh, tol) in items.items():
            path = self._find_asset(names)
            img = self._load_sprite_asset(path, mw, mh, tol) if path else None
            if img:
                self._sea_assets[key] = img
                if key == "fish_orange":
                    self._sea_assets["fish"] = img

    def _get_scaled_asset(self, key, scale=1.0, flip=False):
        src = self._sea_assets.get(key)
        if src is None:
            return None
        scale = max(0.05, float(scale))
        ck = (key, round(scale, 2), bool(flip))
        if ck in self._sea_scaled:
            return self._sea_scaled[ck]
        w, h = src.get_size()
        try:
            img = pygame.transform.smoothscale(src, (max(1, int(w * scale)), max(1, int(h * scale)))).convert_alpha()
            if flip:
                img = pygame.transform.flip(img, True, False)
            self._sea_scaled[ck] = img
            return img
        except Exception:
            return None

    def _draw_asset_sprite(self, key, x, y, scale=1.0, flip=False, anchor="center"):
        img = self._get_scaled_asset(key, scale, flip)
        if img is None:
            return False
        rect = img.get_rect()
        rect.midbottom = (int(x), int(y)) if anchor == "midbottom" else rect.midbottom
        if anchor != "midbottom":
            rect.center = (int(x), int(y))
        self.screen.blit(img, rect)
        return True

    def _get_shadow_asset(self, key, scale=1.0, flip=False, alpha=82):
        src = self._get_scaled_asset(key, scale, flip)
        if src is None:
            return None
        ck = ("shadow", key, round(float(scale), 2), bool(flip), int(alpha))
        if ck not in self._sea_scaled:
            shadow = src.copy().convert_alpha()
            shadow.fill((12, 36, 48, 150), special_flags=pygame.BLEND_RGBA_MULT)
            shadow.set_alpha(alpha)
            self._sea_scaled[ck] = shadow
        return self._sea_scaled[ck]

    def _draw_shadow_asset_sprite(self, key, x, y, scale=1.0, flip=False, alpha=82):
        img = self._get_shadow_asset(key, scale, flip, alpha)
        if img is None:
            return False
        w, h = img.get_size()
        ck = ("shadow_flat", key, round(float(scale), 2), bool(flip), int(alpha), max(1, int(h * 0.72)))
        if ck not in self._sea_scaled:
            self._sea_scaled[ck] = pygame.transform.smoothscale(img, (w, ck[-1])).convert_alpha()
        self.screen.blit(self._sea_scaled[ck], self._sea_scaled[ck].get_rect(center=(int(x), int(y))))
        return True

    def _draw_water_texture_asset(self, t):
        size = (self.W, self.H)
        if self._water_tile is None or self._water_tile_size != size:
            surf = pygame.Surface(size, pygame.SRCALPHA).convert_alpha()
            w, h = size
            for i in range(22):
                rx, ry = (i * 137) % max(1, w), (i * 91) % max(1, h)
                rect = pygame.Rect(rx - (120 + (i * 29) % 190) // 2, ry - (32 + (i * 17) % 72) // 2, 120 + (i * 29) % 190, 32 + (i * 17) % 72)
                pygame.draw.ellipse(surf, (5, 61, 112, 14 + (i % 4) * 5), rect)
            for i in range(26):
                y_base, amp, freq, phase = int((i + 0.5) * h / 26), 5 + (i % 5), 0.010 + (i % 4) * 0.0025, i * 0.83
                pts = [(int(x), int(y_base + math.sin(x * freq + phase) * amp + math.sin(x * 0.027 + phase * 1.7) * 2)) for x in range(-40, w + 41, 24)]
                pygame.draw.lines(surf, (190, 236, 255, 34 + (i % 3) * 12), False, pts, 1)
            for i in range(34):
                x0, y0, length, amp = (i * 101) % (w + 160) - 80, (i * 73) % max(1, h), 70 + (i * 19) % 120, 5 + (i % 7)
                pts = [(int(x0 + length * k / 6), int(y0 + math.sin(k * 1.35 + i * 0.61) * amp)) for k in range(7)]
                pygame.draw.lines(surf, (84, 190, 226, 34), False, pts, 1)
                if i % 4 == 0:
                    pygame.draw.lines(surf, (25, 122, 180, 22), False, [(x, y + 3) for x, y in pts], 1)
            self._water_tile, self._water_tile_size = surf, size
        self.screen.blit(self._water_tile, (0, RIBBON_H))

    def _setup_sea_decorations(self):
        self._dolphins, self._small_fish, self._fins, self._boats, self._bubbles = [], [], [], [], []
        clamp = lambda v, lo, hi: max(lo, min(hi, v))
        px = lambda rx: int(clamp(rx, 0.02, 0.98) * self.W)
        py = lambda ry: RIBBON_H + int(clamp(ry, 0.04, 0.98) * self.H)
        fish = [
            (0.08, 0.10, 0.36, 10, 1, "orange", 0.0), (0.27, 0.17, 0.34, 9, -1, "purple", 0.7),
            (0.61, 0.11, 0.37, 10, 1, "orange", 1.4), (0.88, 0.23, 0.33, 9, -1, "purple", 2.1),
            (0.16, 0.31, 0.35, 9, 1, "purple", 2.8), (0.38, 0.39, 0.32, 8, -1, "orange", 3.4),
            (0.66, 0.33, 0.35, 9, 1, "purple", 4.1), (0.90, 0.42, 0.33, 8, -1, "orange", 4.8),
            (0.12, 0.52, 0.36, 9, 1, "orange", 5.2), (0.30, 0.60, 0.34, 8, -1, "purple", 5.9),
            (0.53, 0.48, 0.37, 10, 1, "orange", 6.3), (0.78, 0.57, 0.33, 8, -1, "purple", 6.9),
            (0.06, 0.73, 0.35, 9, 1, "purple", 7.4), (0.24, 0.84, 0.33, 8, -1, "orange", 8.1),
            (0.49, 0.76, 0.36, 9, 1, "purple", 8.9), (0.72, 0.86, 0.33, 8, -1, "orange", 9.5),
            (0.92, 0.94, 0.34, 9, 1, "purple", 10.2), (0.43, 0.93, 0.31, 8, -1, "orange", 10.8),
        ]
        fins = [(0.10, 0.19, 0.62, 10, 1, 0.1), (0.36, 0.28, 0.56, 8, -1, 0.8), (0.70, 0.18, 0.64, 11, 1, 1.4), (0.88, 0.38, 0.52, 7, -1, 2.0), (0.19, 0.52, 0.58, 9, 1, 2.6), (0.55, 0.62, 0.54, 8, -1, 3.3), (0.78, 0.76, 0.60, 10, 1, 4.1), (0.30, 0.86, 0.50, 7, -1, 4.9)]
        boats = [(0.12, 0.16, 0.78, 7, 1, 0.2), (0.48, 0.27, 0.72, 6, -1, 1.0), (0.82, 0.14, 0.82, 7, 1, 1.7), (0.20, 0.46, 0.74, 6, -1, 2.4), (0.61, 0.58, 0.80, 7, 1, 3.1), (0.86, 0.73, 0.70, 6, -1, 3.8)]
        for rx, ry, s, speed, d, kind, phase in fish:
            self._small_fish.append({"x": px(rx), "y": py(ry), "s": s, "speed": speed, "dir": d, "kind": kind, "phase": phase})
        for rx, ry, s, speed, d, phase in fins:
            self._fins.append({"x": px(rx), "y": py(ry), "s": s, "speed": speed, "dir": d, "phase": phase})
        for rx, ry, s, speed, d, phase in boats:
            self._boats.append({"x": px(rx), "y": py(ry), "s": s, "speed": speed, "dir": d, "phase": phase})
        for i in range(90):
            self._bubbles.append({"x": (i * 67) % max(1, self.W), "y": py(((i * 37) % 90) / 100.0), "r": 1 + (i % 3), "phase": i * 0.31, "speed": 5 + (i % 5)})

    def _refresh_screen_size(self):
        w, h = self.screen.get_width(), self.screen.get_height() - RIBBON_H
        if (w, h) != (self.W, self.H):
            self.W, self.H = w, h
            self._sea_scaled.clear()
            self._water_tile = self._water_tile_size = None
            self._setup_sea_decorations()

    def _mirror_points(self, points, cx, flip):
        return [(cx - (x - cx), y) for x, y in points] if flip else points

    def _draw_sea_texture(self, t):
        top, bot, foam = self._get_color("sea_top", (84, 186, 228)), self._get_color("sea_bottom", (23, 119, 187)), (105, 196, 228)
        for yy in range(0, self.H, 14):
            r = yy / max(1, self.H - 1)
            col = tuple(int(top[i] * (1 - r) + bot[i] * r) for i in range(3))
            pygame.draw.line(self.screen, col, (0, RIBBON_H + yy), (self.W, RIBBON_H + yy), 14)
        self._draw_water_texture_asset(t)
        for b in self._bubbles:
            x = b["x"] + math.sin(b["phase"]) * 8
            y = b["y"] - ((b["phase"] * 11) % 55)
            if y < RIBBON_H + 8:
                y += self.H - 15
            pygame.draw.circle(self.screen, foam, (int(x), int(y)), b["r"], 1)

    def _draw_cartoon_fish(self, x, y, s, kind="orange", flip=False):
        key, alpha = ("fish_purple" if kind == "purple" and self._sea_assets.get("fish_purple") else "fish_orange"), (58 if kind == "purple" else 72)
        if self._draw_shadow_asset_sprite(key, x, y, s, flip, alpha) or self._draw_shadow_asset_sprite("fish", x, y, s, flip, alpha):
            return
        shadow = pygame.Surface((max(2, int(54 * s)), max(2, int(30 * s))), pygame.SRCALPHA).convert_alpha()
        cx, cy, dark, mid = shadow.get_width() // 2, shadow.get_height() // 2, (8, 34, 48, 76), (15, 55, 72, 48)
        pygame.draw.ellipse(shadow, dark, pygame.Rect(int(cx - 18 * s), int(cy - 8 * s), int(30 * s), int(16 * s)))
        tail = [(cx + 10 * s, cy), (cx + 24 * s, cy - 9 * s), (cx + 22 * s, cy + 9 * s)] if not flip else [(cx - 10 * s, cy), (cx - 24 * s, cy - 9 * s), (cx - 22 * s, cy + 9 * s)]
        pygame.draw.polygon(shadow, dark, tail)
        pygame.draw.ellipse(shadow, mid, pygame.Rect(int(cx - 13 * s), int(cy - 5 * s), int(20 * s), int(10 * s)), 1)
        self.screen.blit(shadow, shadow.get_rect(center=(int(x), int(y))))

    def _draw_shark_fin(self, x, y, s, flip=False, phase=0.0):
        if self._draw_asset_sprite("shark_fin", x, y, s, flip):
            pygame.draw.arc(self.screen, (218, 246, 255), pygame.Rect(int(x - 35 * s), int(y + 17 * s), int(70 * s), int(13 * s)), 0.1, math.pi - 0.1, 1)
            return
        dark, shadow, hi, water, foam, wiggle = (42, 47, 51), (18, 21, 24), (92, 98, 103), (57, 143, 199), (218, 246, 255), math.sin(phase) * 2 * s
        fin = [(x - 36 * s, y + 19 * s), (x - 19 * s, y - 18 * s), (x + 28 * s, y - 48 * s), (x + 12 * s, y + 19 * s)]
        shade = [(x + 4 * s, y + 18 * s), (x + 28 * s, y - 48 * s), (x + 12 * s, y + 19 * s)]
        line = [(x - 25 * s, y + 8 * s), (x - 11 * s, y - 17 * s), (x + 14 * s, y - 35 * s), (x - 6 * s, y - 11 * s)]
        splash = [(x - 48 * s, y + 21 * s + wiggle), (x - 25 * s, y + 14 * s), (x + 2 * s, y + 18 * s), (x + 35 * s, y + 13 * s - wiggle), (x + 52 * s, y + 21 * s), (x + 34 * s, y + 27 * s), (x - 24 * s, y + 29 * s)]
        fin, shade, line, splash = [self._mirror_points(p, x, flip) for p in (fin, shade, line, splash)]
        pygame.draw.polygon(self.screen, water, splash)
        pygame.draw.lines(self.screen, foam, False, splash[:4], max(1, int(2 * s)))
        pygame.draw.polygon(self.screen, dark, fin)
        pygame.draw.polygon(self.screen, shadow, shade)
        pygame.draw.line(self.screen, hi, (int(line[0][0]), int(line[0][1])), (int(line[-1][0]), int(line[-1][1])), max(1, int(3 * s)))

    def _draw_boat(self, x, y, s, flip=False, phase=0.0):
        if self._draw_asset_sprite("boat", x, y, s, flip):
            return
        hull, hull_dark, mast, sail, sail_blue, flag = (240, 175, 76), (196, 125, 46), (58, 61, 70), (226, 241, 248), (41, 163, 220), (221, 41, 56)
        bob = math.sin(phase) * 2 * s
        hp = [(x - 36 * s, y + 18 * s + bob), (x + 34 * s, y + 18 * s + bob), (x + 24 * s, y + 33 * s + bob), (x - 28 * s, y + 33 * s + bob)]
        hp = self._mirror_points(hp, x, flip)
        pygame.draw.polygon(self.screen, hull, hp)
        pygame.draw.lines(self.screen, hull_dark, True, hp, max(1, int(2 * s)))
        pygame.draw.line(self.screen, hull_dark, (int(x - 28 * s), int(y + 24 * s + bob)), (int(x + 28 * s), int(y + 24 * s + bob)), max(1, int(2 * s)))
        pygame.draw.line(self.screen, mast, (int(x), int(y - 40 * s + bob)), (int(x), int(y + 18 * s + bob)), max(1, int(4 * s)))
        tri = self._mirror_points([(x, y - 35 * s + bob), (x + 28 * s, y - 8 * s + bob), (x, y + 2 * s + bob)], x, flip)
        flg = self._mirror_points([(x, y - 40 * s + bob), (x + 12 * s, y - 36 * s + bob), (x, y - 32 * s + bob)], x, flip)
        stripe = self._mirror_points([(x, y - 7 * s + bob), (x + 21 * s, y - 11 * s + bob), (x + 21 * s, y - 5 * s + bob), (x, y - 2 * s + bob)], x, flip)
        pygame.draw.polygon(self.screen, sail, tri)
        pygame.draw.polygon(self.screen, flag, flg)
        pygame.draw.polygon(self.screen, sail_blue, stripe)

    def _draw_sea_decorations(self, t):
        for f in self._small_fish:
            d = f["dir"]
            x = (f["x"] + t * f["speed"] * d) % (self.W + 80)
            y = f["y"] + math.sin(t * 2.0 + f["phase"]) * 4
            self._draw_cartoon_fish(x, y, f["s"], f["kind"], d > 0)
        for sf in self._fins:
            d = sf["dir"]
            x = (sf["x"] + t * sf["speed"] * d) % (self.W + 120)
            y = sf["y"] + math.sin(t * 1.5 + sf["phase"]) * 3
            self._draw_shark_fin(x, y, sf["s"], d < 0, t * 2.0 + sf["phase"])
        for b in self._boats:
            d = b["dir"]
            x = (b["x"] + t * b["speed"] * d) % (self.W + 180)
            y = b["y"] + math.sin(t * 0.8 + b["phase"]) * 2
            self._draw_boat(x, y, b["s"], d < 0, t * 1.3 + b["phase"])

    def draw_bg(self):
        self._refresh_screen_size()
        pygame.draw.rect(self.screen, C["bg"], (0, RIBBON_H, self.W, self.H))
        t = pygame.time.get_ticks() * 0.001
        self._draw_sea_texture(t)
        self._draw_sea_decorations(t)

    def draw_edges_layer(self, edges, color, width, dash=False, hidden_edges=None):
        w, r, drawn = max(1, int(width)), max(1, int(width) // 2), set()
        for e in edges:
            if hidden_edges and id(e) in hidden_edges:
                continue
            p1, p2 = self._ws(e[0].x, e[0].y), self._ws(e[1].x, e[1].y)
            if max(p1[0], p2[0]) < -r * 2 or min(p1[0], p2[0]) > self.W + r * 2 or max(p1[1], p2[1]) < RIBBON_H - r * 2 or min(p1[1], p2[1]) > self.H + RIBBON_H + r * 2:
                continue
            if dash:
                total = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
                if total < 2:
                    continue
                dx, dy, pos, drawing, dl = (p2[0] - p1[0]) / total, (p2[1] - p1[1]) / total, 0, True, max(4, int(RW * 0.4 * self.cam.zoom))
                while pos < total:
                    if drawing:
                        end = min(pos + dl, total)
                        pygame.draw.line(self.screen, color, (p1[0] + dx * pos, p1[1] + dy * pos), (p1[0] + dx * end, p1[1] + dy * end), w)
                    pos += dl; drawing = not drawing
                continue
            for node, p in ((e[0], p1), (e[1], p2)):
                if id(node) not in drawn:
                    pygame.draw.circle(self.screen, color, p, r)
                    drawn.add(id(node))
            if p1 != p2:
                a = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
                dx, dy = r * math.sin(a), -r * math.cos(a)
                pygame.draw.polygon(self.screen, color, [(p1[0] + dx, p1[1] + dy), (p2[0] + dx, p2[1] + dy), (p2[0] - dx, p2[1] - dy), (p1[0] - dx, p1[1] - dy)])

    def draw_map(self, city):
        sc, edges, rbs, hidden = self.cam.zoom, city["edges"], city["roundabouts"], city.get("hidden_edges", set())
        self.draw_edges_layer(edges, C["grass"], LP * sc, hidden_edges=hidden)
        self.draw_edges_layer(edges, C["road_outer"], RW * 1.6 * sc, hidden_edges=hidden)
        for rb in rbs:
            sx, sy = self._ws(rb.x, rb.y)
            ro = int(RW * 1.5 * sc)
            if ro >= 2:
                pygame.draw.circle(self.screen, C["road_outer"], (sx, sy), ro + max(1, int(RW * 0.2 * sc)))
        self.draw_edges_layer(edges, C["road_inner"], RW * sc, hidden_edges=hidden)
        for rb in rbs:
            sx, sy = self._ws(rb.x, rb.y)
            ro, ri = int(RW * 1.5 * sc), int(RW * 0.7 * sc)
            if ro >= 2:
                pygame.draw.circle(self.screen, C["road_inner"], (sx, sy), ro)
                pygame.draw.circle(self.screen, C["rb_grass"], (sx, sy), ri)
                pygame.draw.circle(self.screen, C["road_outer"], (sx, sy), ri, max(1, int(3 * sc)))
        if sc > 0.06:
            self.draw_edges_layer(edges, C["road_line"], max(1, RW * 0.08 * sc), dash=True, hidden_edges=hidden)

    def draw_graph(self, nodes, edges):
        sc = self.cam.zoom
        for e in edges:
            p1, p2 = self._ws(e[0].x, e[0].y), self._ws(e[1].x, e[1].y)
            if max(p1[0], p2[0]) < 0 or min(p1[0], p2[0]) > self.W or max(p1[1], p2[1]) < RIBBON_H or min(p1[1], p2[1]) > self.H + RIBBON_H:
                continue
            pygame.draw.line(self.screen, (0, 255, 255), p1, p2, max(1, int(12 * sc)))
        for n in nodes:
            sx, sy = self._ws(n.x, n.y)
            if sx < 0 or sx > self.W or sy < RIBBON_H or sy > self.H + RIBBON_H:
                continue
            pygame.draw.circle(self.screen, (255, 42, 42), (sx, sy), max(3, int(16 * sc)))
            pygame.draw.circle(self.screen, C["white"], (sx, sy), max(3, int(16 * sc)), max(1, int(4 * sc)))
