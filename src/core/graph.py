class Node:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.edges = []
        self.is_roundabout = False
        self.eval_step = float('inf')
        self.disc_step = float('inf')