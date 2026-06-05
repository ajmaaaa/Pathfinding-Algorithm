import unittest
from unittest.mock import Mock
from src.core.graph import Node
from src.core.app import App
from src.algorithm.pathfinder import run_astar_anim

class TestAStar(unittest.TestCase):
    def test_astar_finds_path(self):
        n1 = Node(0, 0)
        n2 = Node(100, 0)
        n3 = Node(200, 0)
        e1 = [n1, n2]
        n1.edges.append(e1); n2.edges.append(e1)
        e2 = [n2, n3]
        n2.edges.append(e2); n3.edges.append(e2)
        
        se, pe, dist, ms, steps = run_astar_anim(n1, n3, [n1, n2, n3])
        self.assertTrue(len(pe) > 0)
        self.assertEqual(pe[0]['from'], n1)
        self.assertEqual(pe[-1]['to'], n3)

    def test_run_astar_no_duplicate_edges(self):
        app = App.__new__(App)
        
        u = Node(0, 0)
        v = Node(100, 0)
        edge = (u, v)
        u.edges.append(edge)
        v.edges.append(edge)
        
        app.city = {
            'nodes': [u, v],
            'edges': [edge],
            'edge_curves': {}
        }
        
        start_node = Node(50, 0)
        app.start_node = start_node
        app.start_edge = edge
        
        app.end_node = v
        app.end_edge = None
        
        app.ribbon = Mock()
        app._update_play_ui = Mock()
        app.is_playing = False
        app.anim_progress = 0.0
        app.total_anim_steps = 0.0
        app.search_edges_anim = []
        app.final_path_anim = []
        app.auto_cam = 'free'
        app.ribbon_h = 100
        
        app._run_astar()
        
        # Verify no duplicate edges in start_node.edges
        self.assertEqual(len(start_node.edges), 2)
        self.assertEqual(len(set(start_node.edges)), 2)
        
        # Verify graph is restored to original state
        self.assertEqual(app.city['nodes'], [u, v])
        self.assertEqual(app.city['edges'], [edge])
        self.assertEqual(u.edges, [edge])
        self.assertEqual(v.edges, [edge])

    def test_run_astar_same_edge_no_duplicate_edges(self):
        app = App.__new__(App)
        
        u = Node(0, 0)
        v = Node(100, 0)
        edge = (u, v)
        u.edges.append(edge)
        v.edges.append(edge)
        
        app.city = {
            'nodes': [u, v],
            'edges': [edge],
            'edge_curves': {}
        }
        
        start_node = Node(30, 0)
        end_node = Node(70, 0)
        
        app.start_node = start_node
        app.start_edge = edge
        app.end_node = end_node
        app.end_edge = edge
        
        app.ribbon = Mock()
        app._update_play_ui = Mock()
        app.is_playing = False
        app.anim_progress = 0.0
        app.total_anim_steps = 0.0
        app.search_edges_anim = []
        app.final_path_anim = []
        app.auto_cam = 'free'
        app.ribbon_h = 100
        
        app._run_astar()
        
        # Verify start_node and end_node edges
        self.assertEqual(len(start_node.edges), 2)
        self.assertEqual(len(set(start_node.edges)), 2)
        
        self.assertEqual(len(end_node.edges), 2)
        self.assertEqual(len(set(end_node.edges)), 2)
        
        # Verify graph is restored to original state
        self.assertEqual(app.city['nodes'], [u, v])
        self.assertEqual(app.city['edges'], [edge])
        self.assertEqual(u.edges, [edge])
        self.assertEqual(v.edges, [edge])