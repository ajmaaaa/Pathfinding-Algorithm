def catmull_rom(p0, p1, p2, p3, t):
    t2 = t * t
    t3 = t2 * t
    # Koefisien Catmull-Rom yang lebih stabil
    f1 = -0.5*t3 + t2 - 0.5*t
    f2 =  1.5*t3 - 2.5*t2 + 1.0
    f3 = -1.5*t3 + 2.0*t2 + 0.5*t
    f4 =  0.5*t3 - 0.5*t2
    x = p0[0]*f1 + p1[0]*f2 + p2[0]*f3 + p3[0]*f4
    y = p0[1]*f1 + p1[1]*f2 + p2[1]*f3 + p3[1]*f4
    return x, y

def cubic_bezier(p0, p1, p2, p3, t):
    u = 1.0 - t
    tt = t * t
    uu = u * u
    uuu = uu * u
    ttt = tt * t
    x = uuu*p0[0] + 3*uu*t*p1[0] + 3*u*tt*p2[0] + ttt*p3[0]
    y = uuu*p0[1] + 3*uu*t*p1[1] + 3*u*tt*p2[1] + ttt*p3[1]
    return x, y

def uniform_bspline(points, samples_per_segment=10):
    if len(points) < 4:
        return points[:]

    out = []
    for i in range(len(points) - 3):
        p0, p1, p2, p3 = points[i:i+4]
        for s in range(samples_per_segment):
            t = s / float(samples_per_segment)
            t2 = t * t
            t3 = t2 * t
            x = ((-t3 + 3*t2 - 3*t + 1) * p0[0] +
                 (3*t3 - 6*t2 + 4) * p1[0] +
                 (-3*t3 + 3*t2 + 3*t + 1) * p2[0] +
                 t3 * p3[0]) / 6.0
            y = ((-t3 + 3*t2 - 3*t + 1) * p0[1] +
                 (3*t3 - 6*t2 + 4) * p1[1] +
                 (-3*t3 + 3*t2 + 3*t + 1) * p2[1] +
                 t3 * p3[1]) / 6.0
            out.append((x, y))
    out.append(points[-2])
    return out

def make_curved_edge_points(a, b, bend=0.115, steps=72, use_bspline=False):
    p0 = (a.x, a.y)
    p3 = (b.x, b.y)
    dx = p3[0] - p0[0]
    dy = p3[1] - p0[1]
    dist = max(1.0, (dx*dx + dy*dy) ** 0.5)
    nx = -dy / dist
    ny = dx / dist
    key = int(abs(a.x + b.x) * 0.17 + abs(a.y + b.y) * 0.29)
    sign = 1.0 if key % 2 == 0 else -1.0
    amp = min(175.0, max(36.0, dist * bend)) * sign

    c1 = (p0[0] + dx * 0.38 + nx * amp, p0[1] + dy * 0.38 + ny * amp)
    c2 = (p0[0] + dx * 0.62 + nx * amp, p0[1] + dy * 0.62 + ny * amp)

    if use_bspline:
        controls = [p0, p0, c1, c2, p3, p3]
        pts = uniform_bspline(controls, max(4, steps // 3))
        pts[0] = p0
        pts[-1] = p3
        return pts

    return [cubic_bezier(p0, c1, c2, p3, i / float(steps)) for i in range(steps + 1)]

def polyline_length(points):
    total = 0.0
    for i in range(1, len(points)):
        dx = points[i][0] - points[i-1][0]
        dy = points[i][1] - points[i-1][1]
        total += (dx*dx + dy*dy) ** 0.5
    return total

def point_on_polyline(points, t):
    if not points:
        return None
    if len(points) == 1 or t <= 0:
        return points[0]
    if t >= 1:
        return points[-1]

    total = polyline_length(points)
    if total <= 0:
        return points[0]

    target = total * t
    walked = 0.0
    for i in range(1, len(points)):
        p0 = points[i - 1]
        p1 = points[i]
        seg = ((p1[0] - p0[0])**2 + (p1[1] - p0[1])**2) ** 0.5
        if walked + seg >= target:
            local_t = (target - walked) / max(0.0001, seg)
            return (
                p0[0] + (p1[0] - p0[0]) * local_t,
                p0[1] + (p1[1] - p0[1]) * local_t
            )
        walked += seg
    return points[-1]

def get_smooth_path_coord(path_edges, prog):
    if not path_edges: return None, None
    if prog <= path_edges[0]['start']: return path_edges[0]['from'].x, path_edges[0]['from'].y
    if prog >= path_edges[-1]['end']: return path_edges[-1]['to'].x, path_edges[-1]['to'].y
    
    idx = 0
    for i, pe in enumerate(path_edges):
        if pe['start'] <= prog <= pe['end']:
            idx = i; break
            
    pe = path_edges[idx]
    t = (prog - pe['start']) / (pe['end'] - pe['start'])

    if 'curve' in pe:
        pt = point_on_polyline(pe['curve'], t)
        if pt:
            return pt
    
    p1 = (pe['from'].x, pe['from'].y); p2 = (pe['to'].x, pe['to'].y)
    
    if idx > 0: p0 = (path_edges[idx-1]['from'].x, path_edges[idx-1]['from'].y)
    else:       p0 = (p1[0] - (p2[0]-p1[0]), p1[1] - (p2[1]-p1[1])) 
        
    if idx < len(path_edges) - 1: p3 = (path_edges[idx+1]['to'].x, path_edges[idx+1]['to'].y)
    else:                         p3 = (p2[0] + (p2[0]-p1[0]), p2[1] + (p2[1]-p1[1])) 

    return catmull_rom(p0, p1, p2, p3, t)

def find_closest_road_point(wx, wy, edges, edge_curves=None):
    import math
    best_dist = float('inf')
    best_pt = None
    best_edge = None
    
    for e in edges:
        u, v = e[0], e[1]
        curve = None
        if edge_curves:
            curve = edge_curves.get(id(e))
        if not curve:
            curve = [(u.x, u.y), (v.x, v.y)]
            
        r_start = get_roundabout_clip_distance(u, v) if getattr(u, 'is_roundabout', False) else 0.0
        r_end = get_roundabout_clip_distance(v, u) if getattr(v, 'is_roundabout', False) else 0.0
        
        # Ensure curve direction matches u -> v
        if curve:
            if math.hypot(curve[0][0] - v.x, curve[0][1] - v.y) < 1.0:
                curve = list(reversed(curve))
                
        clipped = _clip_polyline(curve, r_start, r_end)
        if len(clipped) < 2:
            continue
            
        for i in range(1, len(clipped)):
            p0, p1 = clipped[i-1], clipped[i]
            dx = p1[0] - p0[0]
            dy = p1[1] - p0[1]
            seg_len2 = dx*dx + dy*dy
            if seg_len2 < 0.0001:
                dist = math.hypot(wx - p0[0], wy - p0[1])
                if dist < best_dist:
                    best_dist = dist
                    best_pt = p0
                    best_edge = e
                continue
                
            t = ((wx - p0[0])*dx + (wy - p0[1])*dy) / seg_len2
            t_clamped = max(0.0, min(1.0, t))
            px = p0[0] + t_clamped * dx
            py = p0[1] + t_clamped * dy
            dist = math.hypot(wx - px, wy - py)
            if dist < best_dist:
                best_dist = dist
                best_pt = (px, py)
                best_edge = e
                
    return best_pt, best_edge

def get_roundabout_clip_distance(rb, neighbor):
    import math
    dx = neighbor.x - rb.x
    dy = neighbor.y - rb.y
    L = math.hypot(dx, dy)
    if L < 0.0001:
        return 140.25
    return L * 140.25 / math.sqrt(dx*dx + 4.0 * dy*dy)

def _clip_polyline(curve, r_start, r_end):
    import math
    if len(curve) < 2:
        return curve
    
    lens = [0.0]
    for i in range(1, len(curve)):
        p0, p1 = curve[i-1], curve[i]
        lens.append(lens[-1] + math.hypot(p1[0] - p0[0], p1[1] - p0[1]))
    
    total_len = lens[-1]
    if total_len <= 0.0001:
        return curve
        
    if total_len <= r_start + r_end:
        split_t = r_start / (r_start + r_end) if r_start + r_end > 0 else 0.5
        t_start = max(0.0, split_t - 0.01)
        t_end = min(1.0, split_t + 0.01)
        p0, p1 = curve[0], curve[-1]
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        return [(p0[0] + dx * t_start, p0[1] + dy * t_start), (p0[0] + dx * t_end, p0[1] + dy * t_end)]

    start_pt = None
    start_idx = 1
    for i in range(1, len(curve)):
        if lens[i] >= r_start:
            p0, p1 = curve[i-1], curve[i]
            seg_len = lens[i] - lens[i-1]
            t = (r_start - lens[i-1]) / seg_len if seg_len > 0 else 0.0
            start_pt = (p0[0] + t * (p1[0] - p0[0]), p0[1] + t * (p1[1] - p0[1]))
            start_idx = i
            break
            
    target_end_dist = total_len - r_end
    end_pt = None
    end_idx = 0
    for i in range(1, len(curve)):
        if lens[i] >= target_end_dist:
            p0, p1 = curve[i-1], curve[i]
            seg_len = lens[i] - lens[i-1]
            t = (target_end_dist - lens[i-1]) / seg_len if seg_len > 0 else 0.0
            end_pt = (p0[0] + t * (p1[0] - p0[0]), p0[1] + t * (p1[1] - p0[1]))
            end_idx = i - 1
            break
            
    if start_pt is None or end_pt is None:
        return curve
        
    res = [start_pt]
    for idx in range(start_idx, end_idx + 1):
        res.append(curve[idx])
    res.append(end_pt)
    return res

def split_curve_at_point(curve, pt):
    import math
    if len(curve) < 2:
        return curve[:], curve[:]
    
    px, py = pt
    best_dist = float('inf')
    best_idx = 1
    best_proj = curve[0]
    
    for i in range(1, len(curve)):
        p0, p1 = curve[i-1], curve[i]
        dx = p1[0] - p0[0]
        dy = p1[1] - p0[1]
        seg_len2 = dx*dx + dy*dy
        if seg_len2 < 0.0001:
            dist = math.hypot(px - p0[0], py - p0[1])
            if dist < best_dist:
                best_dist = dist
                best_idx = i
                best_proj = p0
            continue
            
        t = ((px - p0[0])*dx + (py - p0[1])*dy) / seg_len2
        t_clamped = max(0.0, min(1.0, t))
        proj_x = p0[0] + t_clamped * dx
        proj_y = p0[1] + t_clamped * dy
        dist = math.hypot(px - proj_x, py - proj_y)
        if dist < best_dist:
            best_dist = dist
            best_idx = i
            best_proj = (proj_x, proj_y)
            
    part1 = list(curve[:best_idx])
    if math.hypot(part1[-1][0] - best_proj[0], part1[-1][1] - best_proj[1]) > 0.01:
        part1.append(best_proj)
    else:
        part1[-1] = best_proj
        
    part2 = [best_proj]
    for j in range(best_idx, len(curve)):
        part2.append(curve[j])
        
    return part1, part2

