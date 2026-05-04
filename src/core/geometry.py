def quadratic_bezier(p0, p1, p2, t):
    # Rumus Bezier Curve Kuadratik khusus untuk sudut (Sangat Ringan)
    x = (1 - t)**2 * p0[0] + 2 * (1 - t) * t * p1[0] + t**2 * p2[0]
    y = (1 - t)**2 * p0[1] + 2 * (1 - t) * t * p1[1] + t**2 * p2[1]
    return x, y

def get_smooth_path_coord(path_edges, prog):
    if not path_edges: return None, None
    if prog <= path_edges[0]['start']: return path_edges[0]['from'].x, path_edges[0]['from'].y
    if prog >= path_edges[-1]['end']: return path_edges[-1]['to'].x, path_edges[-1]['to'].y
    
    idx = 0
    for i, pe in enumerate(path_edges):
        if pe['start'] <= prog <= pe['end']:
            idx = i; break
            
    pe = path_edges[idx]
    
    # Pencegahan error jika panjang edge 0
    if pe['end'] == pe['start']:
        return pe['to'].x, pe['to'].y
        
    t = (prog - pe['start']) / (pe['end'] - pe['start'])
    
    p1 = (pe['from'].x, pe['from'].y)
    p2 = (pe['to'].x, pe['to'].y)
    
    # SMOOTH_FACTOR: Menentukan seberapa lebar radius tikungan 
    # (0.25 berarti mobil mulai belok di 25% jarak ujung jalan)
    SMOOTH_FACTOR = 0.25 
    
    if t < SMOOTH_FACTOR and idx > 0:
        # 1. TIKUNGAN KELUAR (Berada di awal ruas jalan)
        prev_pe = path_edges[idx-1]
        p0 = (prev_pe['from'].x, prev_pe['from'].y)
        
        # Tarik titik kontrol bezier 25% dari simpang
        start_curve = (p0[0] + (p1[0]-p0[0])*(1-SMOOTH_FACTOR), p0[1] + (p1[1]-p0[1])*(1-SMOOTH_FACTOR))
        end_curve = (p1[0] + (p2[0]-p1[0])*SMOOTH_FACTOR, p1[1] + (p2[1]-p1[1])*SMOOTH_FACTOR)
        
        u = 0.5 + (t / SMOOTH_FACTOR) * 0.5
        return quadratic_bezier(start_curve, p1, end_curve, u)
        
    elif t > (1 - SMOOTH_FACTOR) and idx < len(path_edges) - 1:
        # 2. TIKUNGAN MASUK (Berada di akhir ruas jalan)
        next_pe = path_edges[idx+1]
        p3 = (next_pe['to'].x, next_pe['to'].y)
        
        start_curve = (p1[0] + (p2[0]-p1[0])*(1-SMOOTH_FACTOR), p1[1] + (p2[1]-p1[1])*(1-SMOOTH_FACTOR))
        end_curve = (p2[0] + (p3[0]-p2[0])*SMOOTH_FACTOR, p2[1] + (p3[1]-p2[1])*SMOOTH_FACTOR)
        
        u = (t - (1 - SMOOTH_FACTOR)) / SMOOTH_FACTOR * 0.5
        return quadratic_bezier(start_curve, p2, end_curve, u)
        
    else:
        # 3. JALAN LURUS (Super ringan untuk CPU)
        x = p1[0] + (p2[0] - p1[0]) * t
        y = p1[1] + (p2[1] - p1[1]) * t
        return x, y