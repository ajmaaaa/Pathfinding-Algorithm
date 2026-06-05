class MinHeap:
    def __init__(self):
        self.elements = []
        
    def empty(self):
        return len(self.elements) == 0
        
    def put(self, item, priority):
        # Menyimpan priority, identifier unik (id) agar objek tak diperbandingkan, dan item
        entry = (priority, id(item), item)
        self.elements.append(entry)
        self._sift_up(len(self.elements) - 1)
        
    def get(self):
        if not self.elements:
            raise IndexError("pop from empty heap")
        if len(self.elements) == 1:
            return self.elements.pop()[2]
        
        root = self.elements[0]
        # Pindahkan elemen terakhir ke root dan lakukan sift down
        self.elements[0] = self.elements.pop()
        self._sift_down(0)
        return root[2]
        
    def _sift_up(self, idx):
        child_idx = idx
        while child_idx > 0:
            parent_idx = (child_idx - 1) // 2
            if self.elements[child_idx] < self.elements[parent_idx]:
                self.elements[child_idx], self.elements[parent_idx] = self.elements[parent_idx], self.elements[child_idx]
                child_idx = parent_idx
            else:
                break
                
    def _sift_down(self, idx):
        parent_idx = idx
        n = len(self.elements)
        while True:
            left_idx = 2 * parent_idx + 1
            right_idx = 2 * parent_idx + 2
            smallest_idx = parent_idx
            
            if left_idx < n and self.elements[left_idx] < self.elements[smallest_idx]:
                smallest_idx = left_idx
            if right_idx < n and self.elements[right_idx] < self.elements[smallest_idx]:
                smallest_idx = right_idx
                
            if smallest_idx != parent_idx:
                self.elements[parent_idx], self.elements[smallest_idx] = self.elements[smallest_idx], self.elements[parent_idx]
                parent_idx = smallest_idx
            else:
                break
