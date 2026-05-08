class Node:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.edges = []
        self.is_roundabout = False
        self.eval_step = float('inf')
        self.disc_step = float('inf')

    def __lt__(self, other):
        return self.eval_step < other.eval_step


class Edge:
    def __init__(self, node_a, node_b):
        self.node_a = node_a
        self.node_b = node_b
        self.cost = self._distance(node_a, node_b)

    def _distance(self, node_a, node_b):
        dx = node_a.x - node_b.x
        dy = node_a.y - node_b.y
        return (dx * dx + dy * dy) ** 0.5

    def get_other(self, node):
        if node is self.node_a:
            return self.node_b
        if node is self.node_b:
            return self.node_a
        return None

    def __getitem__(self, index):
        if index == 0:
            return self.node_a
        if index == 1:
            return self.node_b
        raise IndexError("Edge hanya memiliki index 0 dan 1")


class Graph:
    def __init__(self):
        self.nodes = []
        self.edges = []

    def add_node(self, x, y, is_roundabout=False):
        node = Node(x, y)
        node.is_roundabout = is_roundabout
        self.nodes.append(node)
        return node

    def add_edge(self, node_a, node_b, bidirectional=True):
        edge = Edge(node_a, node_b)

        self.edges.append(edge)
        node_a.edges.append(edge)

        if bidirectional:
            node_b.edges.append(edge)

        return edge

    def distance(self, node_a, node_b):
        dx = node_a.x - node_b.x
        dy = node_a.y - node_b.y
        return (dx * dx + dy * dy) ** 0.5

    def reset_steps(self):
        for node in self.nodes:
            node.eval_step = float('inf')
            node.disc_step = float('inf')

    def nearest_node(self, x, y):
        if not self.nodes:
            return None

        nearest = self.nodes[0]
        nearest_distance = self.distance(nearest, Node(x, y))

        for node in self.nodes:
            current_distance = self.distance(node, Node(x, y))

            if current_distance < nearest_distance:
                nearest = node
                nearest_distance = current_distance

        return nearest

    def astar(self, start_node, goal_node):
        self.reset_steps()

        open_set = [start_node]
        came_from = {}
        cost_so_far = {}

        start_node.disc_step = 0
        start_node.eval_step = self.distance(start_node, goal_node)
        cost_so_far[start_node] = 0

        while open_set:
            current = self.get_lowest_eval_node(open_set)

            if current is goal_node:
                return self.reconstruct_path(came_from, current)

            open_set.remove(current)

            for edge in current.edges:
                neighbor = edge.get_other(current)

                if neighbor is None:
                    continue

                new_cost = cost_so_far[current] + edge.cost

                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    came_from[neighbor] = current

                    neighbor.disc_step = new_cost
                    neighbor.eval_step = new_cost + self.distance(neighbor, goal_node)

                    if neighbor not in open_set:
                        open_set.append(neighbor)

        return []

    def get_lowest_eval_node(self, open_set):
        lowest_node = open_set[0]

        for node in open_set:
            if node.eval_step < lowest_node.eval_step:
                lowest_node = node

        return lowest_node

    def reconstruct_path(self, came_from, current):
        path = [current]

        while current in came_from:
            current = came_from[current]
            path.append(current)

        path.reverse()
        return path