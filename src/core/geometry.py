import math

def get_smooth_path_coord(path_edges, prog):
    """
    Kini mobil secara harfiah "membaca" titik aspal yang sudah
    digambar melengkung oleh city_gen, sehingga mustahil mobil 
    keluar jalur / bergerak patah-patah!
    """
    if not path_edges: return None, None
    if prog <= path_edges[0]['start']: return path_edges[0]['from'].x, path_edges[0]['from'].y
    if prog >= path_edges[-1]['end']: return path_edges[-1]['to'].x, path_edges[-1]['to'].y
    
    idx = 0
    for i, pe in enumerate(path_edges):
        if pe['start'] <= prog <= pe['end']:
            idx = i; break
            
    pe = path_edges[idx]
    t = (prog - pe['start']) / (pe['end'] - pe['start'])
    
    n1 = pe['from']
    n2 = pe['to']
    
    # Cari jalur asli di Node
    edge_data = None
    for e in n1.edges:
        if (e[0] is n2 and e[1] is n1) or (e[0] is n1 and e[1] is n2):
            edge_data = e
            break
            
    # Menyusuri lengkungan titik aspal
    if edge_data and len(edge_data) > 2:
        visual_pts = edge_data[2]
        
        pts = visual_pts
        if edge_data[1] is n1: 
            pts = list(reversed(visual_pts))
            
        full_pts = [{'x': n1.x, 'y': n1.y}] + pts + [{'x': n2.x, 'y': n2.y}]
        
        total_segments = len(full_pts) - 1
        exact_pos = t * total_segments
        
        seg_idx = int(exact_pos)
        seg_t = exact_pos - seg_idx
        
        if seg_idx >= total_segments:
            return n2.x, n2.y
            
        pA = full_pts[seg_idx]
        pB = full_pts[seg_idx + 1]
        
        # Interpolasi Linear antar titik aspal
        x = pA['x'] + (pB['x'] - pA['x']) * seg_t
        y = pA['y'] + (pB['y'] - pA['y']) * seg_t
        return x, y
        
    x = n1.x + (n2.x - n1.x) * t
    y = n1.y + (n2.y - n1.y) * t
    return x, y
