class Dot:
    def __init__(self, a, b):
        self.x = a
        self.y = b
        self.color = (0, 0, 0)
        self.isDead = False

    def __eq__(self, other):
        return abs(self.x - other.x) < 5 and abs(self.y - other.y) < 5


def field():
    raw = [[(round(21.23 * (i + 1)), round(21.23 * (j + 1)) + 50) for i in range(23)] for j in range(27)]
    dots_raw = []
    for i in raw:
        for j in i:
            dots_raw.append(j)
    dots = [Dot(i[0], i[1]) for i in dots_raw]
    return dots


class Game:
    def __init__(self, id, login1):
        self.p1Went = False
        self.p2Went = True
        self.p1Color = (255, 0, 0)
        self.p2Color = (0, 0, 255)
        self.id = id
        self.dots = field()
        self.p1Score = 0
        self.p2Score = 0
        self.circles = []
        self.ready = False
        self.winner = -1
        self.login1 = login1
        self.login2 = ''

    def place_dot(self, player, dot):
        new_dot = Dot(dot[0], dot[1])
        for d in self.dots:
            if d == new_dot and d.color == (0, 0, 0) and not d.isDead:
                if player == 0:
                    d.color = self.p1Color
                    self.p1Went = True
                    self.p2Went = False
                else:
                    d.color = self.p2Color
                    self.p1Went = False
                    self.p2Went = True
                return d
        return Dot(-10, -10)
