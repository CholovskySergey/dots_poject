import socket
import pickle
from _thread import *
from game import Game, Dot
import numpy as np

server = '25.41.111.123'
port = 1487
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    print(str(e))

s.listen(19)
print("Waiting for a connection, Server Started")

connected = set()
games = {}
idCount = 0
user_db = {'user': 'user', 'pwd': 'pwd'}
active_users = {} # login : pair (ip,status)
# status = -1 - sleeping user, -2 - seeking for a game , N of game room - active/


def lee(grid, ax, ay, visited, circle):
    dx = [1, 0, -1, 0]
    dy = [0, 1, 0, -1]

    d = 0
    grid[ay, ax] = 0  # start

    if ax == 0 or ay == 0 or ax == 26 or ay == 22:
        return False

    visited.append((ay, ax))

    result = True

    while True:
        stop = True
        for y in range(27):
            for x in range(23):
                if grid[y, x] == d:
                    for k in range(4):
                        iy = y + dy[k]
                        ix = x + dx[k]
                        if iy >= 0 and iy < 27 and ix >= 0 and ix < 23 and grid[iy, ix] == -2:
                            if iy == 0 or ix == 0 or iy == 26 or ix == 22:
                                result = False
                            stop = False
                            grid[iy, ix] = d + 1
                            visited.append((iy, ix))
        d += 1

        if stop:
            break

    if result:
        for i in range(27):
            for j in range(23):
                if grid[i, j] == -1:

                    test_dots = []
                    if i != 0:
                        test_dots.append(grid[i - 1, j])
                    if i != 26:
                        test_dots.append(grid[i + 1, j])
                    if j != 0:
                        test_dots.append(grid[i, j - 1])
                    if j != 22:
                        test_dots.append(grid[i, j + 1])

                    for element in test_dots:
                        if element == -1:
                            del element

                    temp = [i >= 0 for i in test_dots]

                    if len(test_dots) == 1 and test_dots[0] >= 0:
                        circle.append((i, j))
                    elif len(test_dots) == 2:
                        if sum(temp) == 1:
                            circle.append((i, j))
                    elif len(test_dots) == 3:
                        if sum(temp) == 1 or sum(temp) == 2:
                            circle.append((i, j))
                    elif len(test_dots) == 4:
                        if sum(temp) == 1 or sum(temp) == 2 or sum(temp) == 3:
                            circle.append((i, j))

    return result


def chain(old_vertex):

    mat = np.zeros((27, 23))
    for index in old_vertex:
        mat[index] = 1

    new_vertex = []
    new_vertex.append(old_vertex[0])
    mat[old_vertex[0]] = 0
    x, y = old_vertex[0]

    for k in range(len(old_vertex)):
        if x + 1 != 27 and mat[x + 1, y] == 1:
            mat[x + 1, y] = 0
            new_vertex.append((x+1, y))
        elif x - 1 != -1 and mat[x - 1, y] == 1:
            mat[x - 1, y] = 0
            new_vertex.append((x-1, y))
        elif y + 1 != 23 and mat[x, y + 1] == 1:
            mat[x, y + 1] = 0
            new_vertex.append((x, y + 1))
        elif y - 1 != -1 and mat[x, y - 1] == 1:
            mat[x, y - 1] = 0
            new_vertex.append((x, y - 1))
        elif x + 1 != 27 and y + 1 != 23 and mat[x + 1, y + 1] == 1:
            mat[x + 1, y + 1] = 0
            new_vertex.append((x+1, y+1))
        elif x - 1 != -1 and y + 1 != 23 and mat[x - 1, y + 1] == 1:
            mat[x - 1, y + 1] = 0
            new_vertex.append((x-1, y+1))
        elif x + 1 != 27 and y - 1 != 23 and mat[x + 1, y - 1] == 1:
            mat[x + 1, y - 1] = 0
            new_vertex.append((x + 1, y - 1))
        elif x - 1 != -1 and y - 1 != -1 and mat[x - 1, y - 1] == 1:
            mat[x - 1, y - 1] = 0
            new_vertex.append((x - 1, y - 1))
        x, y = new_vertex[-1]

    return new_vertex


def threaded_client(connection, player, gameId):
    global idCount
    data = ''
    run = True
    while run:
        try:
            data = pickle.loads(connection.recv(2048*32))
            game = games[gameId]
            if not data:
                print("Disconnected")
                break
            elif data == 'player':
                connection.send(pickle.dumps(player))
            elif data == 'concede':
                if player == 0:
                    game.winner = 1
                elif player == 1:
                    game.winner = 0
                run = False
                connection.sendall(pickle.dumps(game))
            elif data != 'get':
                if player == 0 and game.p1Went is False and game.p2Went is True:
                    last_turn = game.place_dot(player, data)
                elif player == 1 and game.p2Went is False and game.p1Went is True:
                    last_turn = game.place_dot(player, data)
                else:
                    last_turn = Dot(-10, -10)
                m = np.array(game.dots)
                m = np.reshape(m, (27, 23))

                if not (last_turn == Dot(-10, -10)):
                    # index = 23 * i + j
                    index = game.dots.index(last_turn)
                    i = index // 23
                    j = index - 23 * i

                    grid = np.zeros((27, 23))
                    for x in range(27):
                        for y in range(23):
                            grid[x, y] = -2
                            if (m[x, y].color == game.p1Color and player == 0 and not m[x, y].isDead) or (
                                    m[x, y].color == game.p2Color and player == 1 and not m[x, y].isDead):
                                grid[x, y] = -1
                    upper_dot = False
                    lower_dot = False
                    left_dot = False
                    right_dot = False

                    visited_upper = []
                    visited_lower = []
                    visited_right = []
                    visited_left = []

                    circle_upper = []
                    circle_lower = []
                    circle_right = []
                    circle_left = []

                    if i != 0:
                        upper_dot = lee(grid.copy(), j, i-1, visited_upper, circle_upper)
                    if i != 26:
                        lower_dot = lee(grid.copy(), j, i+1, visited_lower, circle_lower)
                    if j != 0:
                        left_dot = lee(grid.copy(), j-1, i, visited_left, circle_left)
                    if j != 22:
                        right_dot = lee(grid.copy(), j+1, i, visited_right, circle_right)

                    if upper_dot:
                        old_score = game.p1Score + game.p2Score
                        circle_upper = chain(circle_upper)
                        circle = [(m[index].x, m[index].y) for index in circle_upper]
                        game.circles.append(circle)
                        for index in visited_upper:
                            if player == 0 and m[index].color == game.p2Color and not m[index].isDead:
                                game.p1Score += 1
                                m[index].isDead = True
                            if player == 1 and m[index].color == game.p1Color and not m[index].isDead:
                                game.p2Score += 1
                                m[index].isDead = True
                        if old_score == game.p1Score + game.p2Score:
                            game.circles.pop()

                    if lower_dot:
                        old_score = game.p1Score + game.p2Score
                        circle_lower = chain(circle_lower)
                        circle = [(m[index].x, m[index].y) for index in circle_lower]
                        game.circles.append(circle)
                        for index in visited_lower:
                            if player == 0 and m[index].color == game.p2Color and not m[index].isDead:
                                game.p1Score += 1
                                m[index].isDead = True
                            if player == 1 and m[index].color == game.p1Color and not m[index].isDead:
                                game.p2Score += 1
                                m[index].isDead = True
                        if old_score == game.p1Score + game.p2Score:
                            game.circles.pop()

                    if left_dot:
                        old_score = game.p1Score + game.p2Score
                        circle_left = chain(circle_left)
                        circle = [(m[index].x, m[index].y) for index in circle_left]
                        game.circles.append(circle)
                        for index in visited_left:
                            if player == 0 and m[index].color == game.p2Color and not m[index].isDead:
                                game.p1Score += 1
                                m[index].isDead = True
                            if player == 1 and m[index].color == game.p1Color and not m[index].isDead:
                                game.p2Score += 1
                                m[index].isDead = True
                        if old_score == game.p1Score + game.p2Score:
                            game.circles.pop()

                    if right_dot:
                        old_score = game.p1Score + game.p2Score
                        circle_right = chain(circle_right)
                        circle = [(m[index].x, m[index].y) for index in circle_right]
                        game.circles.append(circle)
                        for index in visited_right:
                            if player == 0 and m[index].color == game.p2Color and not m[index].isDead:
                                game.p1Score += 1
                                m[index].isDead = True
                            if player == 1 and m[index].color == game.p1Color and not m[index].isDead:
                                game.p2Score += 1
                                m[index].isDead = True
                        if old_score == game.p1Score + game.p2Score:
                            game.circles.pop()

                if game.p1Score - game.p2Score > 20:
                    game.winner = 0
                if game.p1Score - game.p2Score < -20:
                    game.winner = 1
                alldotsdead = True
                for i in game.dots:
                    if i.color == (0, 0, 0):
                        alldotsdead = False
                        break
                if alldotsdead:
                    game.winner = 3
                if game.winner != -1:
                    run = False
                    # FINISH SESSION
                    # send_play_agai
                connection.sendall(pickle.dumps(game))
            if data == 'get':
                connection.sendall(pickle.dumps(game))
        except e:
            print("Ooof")
            print(e)
            break


def login(connection, addr):
    log = 0
    name = str()
    try:
        data = pickle.loads(connection.recv(2048 * 32))
        if not data:
            print("Disconnected")
        else:
            req = data.split('\a')
            if req[0] == 'reg':
                try:
                    passd = user_db[req[1]]
                    log = 0
                except:
                    if req[1] != '':
                        user_db[req[1]] = req[2]
                        active_users[req[1]] = (addr, -1)
                        name = req[1]
                        log = 1
                connection.sendall(pickle.dumps(log))
            elif req[0] == 'log':
                try:
                    log = int(user_db[req[1]] == req[2])
                except:
                    log = -2
                if log != -2 and log != 0:
                    try:
                        info = active_users[req[1]]
                        log = -1
                    except:
                        active_users[req[1]] = (addr, -1)
                        name = req[1]
                connection.sendall(pickle.dumps(log))
    except e:
        print("Thread exp")
        print(e)
    return log > 0, name


def login_thread(connection, addr):
    global idCount

    name = ''
    connected = False
    while not connected:
        connected, name = login(connection, addr)

    print(user_db)

    while True:
        try:
            data = pickle.loads(connection.recv(1024))
            print(data)
            if not data:
                print("Disconnected")
                break
            elif data == 'ready':
                idCount += 1
                print(idCount)
                p = 0
                gameId = (idCount - 1) // 2
                print(gameId)
                if idCount % 2 == 1:
                    games[gameId] = Game(gameId, name)
                    print("Creating a new game...")
                    active_users[name] = (addr, -2)
                else:
                    games[gameId].ready = True
                    games[gameId].login2 = name
                    p = 1
                connection.sendall(pickle.dumps(name))
                threaded_client(connection, p, gameId)

                if idCount % 2 == 1:
                    try:
                        del games[gameId]
                    except:
                        pass
                idCount -= 1
        except:
            pass
            # print("Login thread error")

    print('Lost connection')
    connection.close()


while True:
    # if connected:
    connection, adr = s.accept()

    print("Connected to: ", adr)

    start_new_thread(login_thread, (connection, adr))
