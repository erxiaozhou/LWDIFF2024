class TestedCasesPaths:
    def __init__(self, num_limit = 20000):
        self.tested_paths = set()
        self.num_limit = num_limit

    def add(self, path):
        path = str(path)
        if len(self.tested_paths) == self.num_limit:
            self.tested_paths.pop()
        self.tested_paths.add(path)
        assert len(self.tested_paths) <= self.num_limit

    def __contains__(self, path):
        path = str(path)
        return path in self.tested_paths
        
    def __len__(self):
        return len(self.tested_paths)
