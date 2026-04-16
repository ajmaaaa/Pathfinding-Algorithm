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
    
    p1 = (pe['from'].x, pe['from'].y); p2 = (pe['to'].x, pe['to'].y)
    
    if idx > 0: p0 = (path_edges[idx-1]['from'].x, path_edges[idx-1]['from'].y)
    else:       p0 = (p1[0] - (p2[0]-p1[0]), p1[1] - (p2[1]-p1[1])) 
        
    if idx < len(path_edges) - 1: p3 = (path_edges[idx+1]['to'].x, path_edges[idx+1]['to'].y)
    else:                         p3 = (p2[0] + (p2[0]-p1[0]), p2[1] + (p2[1]-p1[1])) 

    return catmull_rom(p0, p1, p2, p3, t)