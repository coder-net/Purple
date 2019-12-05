from models.graph import Graph


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ResourseManager(metaclass=Singleton):
    update = set()

    def __init__(self):
        self._graph = None

    @property
    def graph(self):
        return self._graph

    @graph.setter
    def graph(self, graph: Graph):
        self._graph = graph

