import math

def euclidean_distance(n1, n2):
    """Menghitung jarak lurus (Euclidean) sebagai fungsi heuristik A*"""
    return math.hypot(n1.x - n2.x, n1.y - n2.y)