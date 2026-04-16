import heapq

class MinHeap:
    def __init__(self):
        self.elements = []
        
    def empty(self):
        return len(self.elements) == 0
        
    def put(self, item, priority):
        # Menyimpan priority, identifier unik (id) agar objek tak diperbandingkan, dan item
        heapq.heappush(self.elements, (priority, id(item), item))
        
    def get(self):
        return heapq.heappop(self.elements)[2]