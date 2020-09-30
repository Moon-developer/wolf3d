class Map:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.map = None

        # CALL
        self.generate_map()

    def generate_map(self):
        MAP = """
        XXXXXXXXXXXXXXXXXXXXXXXX
        X                      X
        X                      X
        X          X           X
        X          X           X
        XXXXXXXXXXXX           X
        X                      X
        X        4444          X
        X222222  4             X
        X     2  4         XXXXX
        X  1  2  4             X
        X  1  2  4             X
        X  1  2  4             X
        X  1     4             X
        X  1333334             X
        X                      X
        XXXXXXXX               X
        X      X               X
        X   X  X               X
        X   X  X               X
        X  XXXXX               X
        X                      X
        X                      X
        XXXXXXXXXXXXXXXXXXXXXXXX
        """.replace("\n", "")
        self.map = MAP

    def get_map(self):
        return self.map


class MapGenerator:

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.maps = []

    def generate_maps(self, num: int = 1):
        for i in range(num):
            mp = Map(self.width, self.height)
            self.maps.append(mp.get_map())

    def get_map(self, index):
        return self.maps[index]