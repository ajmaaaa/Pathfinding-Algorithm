import unittest
from src.core.city_gen import MapGen

class TestMapGen(unittest.TestCase):
    def test_city_generation(self):
        generator = MapGen()
        city = generator.generate()
        
        self.assertIn('nodes', city)
        self.assertIn('edges', city)
        self.assertIn('buildings', city)
        self.assertTrue(len(city['nodes']) > 0)
        self.assertTrue(len(city['edges']) > 0)