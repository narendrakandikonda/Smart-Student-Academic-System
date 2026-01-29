class StudentGraph:
    def __init__(self):
        self.graph = {}

    def add_student(self, roll):
        if roll not in self.graph:
            self.graph[roll] = []

    def add_friendship(self, a, b):
        self.graph[a].append(b)
        self.graph[b].append(a)

    def get_graph(self):
        return self.graph