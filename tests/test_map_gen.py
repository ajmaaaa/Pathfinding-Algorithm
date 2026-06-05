import unittest
import math
from collections import Counter

from src.core.city_gen import MapGen, ROAD_HALF_WIDTH
# MapEditor is removed; compile_graph is now in MapGen

class TestMapGen(unittest.TestCase):
    def test_city_generation(self):
        generator = MapGen(123)
        entities = generator.generate()
        
        # memastikan generator menghasilkan daftar objek
        self.assertTrue(isinstance(entities, list))
        self.assertTrue(len(entities) > 0)
        
        # memastikan komponen utama kota berhasil dibuat
        types = [e.__class__.__name__ for e in entities]
        self.assertIn('Pulau', types)
        self.assertIn('RoadSegment', types)
        self.assertIn('BasePlatform', types)

    def test_generated_roads_compile_to_one_component(self):
        generator = MapGen(321)
        entities = generator.generate()
        city = generator.compile_graph()

        # membangun struktur adjacency graph
        adjacency = {node: set() for node in city["nodes"]}
        for a, b in city["edges"]:
            adjacency[a].add(b)
            adjacency[b].add(a)

        # DFS untuk memastikan seluruh node saling terhubung
        start = next(iter(adjacency))
        seen = {start}
        stack = [start]
        while stack:
            node = stack.pop()
            for other in adjacency[node]:
                if other not in seen:
                    seen.add(other)
                    stack.append(other)

        # semua node harus dapat dijangka
        self.assertEqual(len(seen), len(adjacency))

        # membatasi jumlah jalan buntu (dead-end)
        self.assertLessEqual(sum(1 for edges in adjacency.values() if len(edges) == 1), 6)

    def test_generator_keeps_reference_layout_rules(self):
        generator = MapGen(444)
        entities = generator.generate()
        counts = Counter(e.__class__.__name__ for e in entities)

        # validasi jumlah objek agar sesuai aturan desain peta
        self.assertEqual(counts["Pulau"], 1)
        self.assertTrue(2 <= counts["Roundabout"] <= 4)
        self.assertGreaterEqual(counts["BasePlatform"], 6)
        self.assertGreaterEqual(counts["RoadSegment"], 7)
        self.assertLessEqual(counts["RoadSegment"], 75)
        self.assertGreaterEqual(counts["PohonPinus"] + counts["PohonBulat"], 120)
        self.assertLessEqual(counts["PohonPinus"] + counts["PohonBulat"], 4500)
        self.assertLessEqual(len(entities), 5000)

        # memastikan jumlah vegetasi masih dalam batas wajar
        island = next(e for e in entities if e.__class__.__name__ == "Pulau")

        # luas pulau harus lebih besar dari total area jalan
        road_area = generator._road_length() * 20.0
        island_area = math.pi * island.rad_c * island.rad_r
        self.assertGreater(island_area, road_area)

        # objek selain jalan harus memiliki jarak aman dari jalan raya
        for x, y, _radius, component_type in generator.occupied:
            if component_type in ("Platform", "Roundabout", "Lampu", "PohonPinus", "PohonBulat"):
                continue
            self.assertGreaterEqual(generator._min_dist_to_roads(x, y), ROAD_HALF_WIDTH + 14)

    def test_different_seeds_change_road_shape(self):
        signatures = []
        # seed berbeda harus menghasilkan layout jalan berbeda
        for seed in (11, 12, 13):
            generator = MapGen(seed)
            generator.generate()
            sample = tuple(
                (round(road.x1), round(road.y1), round(road.x2), round(road.y2))
                for road in generator.roads[:8]
            )
            signatures.append(sample)

        self.assertGreater(len(set(signatures)), 1)
