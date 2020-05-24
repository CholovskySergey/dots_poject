import pygame as pg
import os
from network import Network
from game import Game, Dot
import tkinter as tk
from tkinter import messagebox

pg.init()

width = 600
height = 600 - 5 + 50
GOVER = "Game is over"
WINNER = "Congratulations!"
TIE = "LOL, no winner"
DELIM = "   "


def set_point(win, point, color):
    pg.draw.circle(win, color, point, 3)
    pg.display.update()


def redraw(win, game):
    for dot in game.dots:
        if dot.color != (0, 0, 0) and not dot.isDead:
            set_point(win, (dot.x, dot.y), dot.color)
        if dot.color != (0, 0, 0) and dot.isDead:
            x, y, z = dot.color
            col = (x // 2, y // 2, z // 2)
            set_point(win, (dot.x, dot.y), col)
    if len(game.circles) != 0:
        for circle in game.circles:
            color = (0, 0, 0)
            a, b = circle[0]
            dot = Dot(a, b)
            for c in game.dots:
                if c == dot:
                    color = c.color
            pg.draw.polygon(win, color, circle, 1)


def label(win, str, color, a, b, c, d):
    font = pg.font.SysFont('Consolas', 16)
    rect = (a, b, c, d)
    pg.draw.rect(win, color, rect)
    text = font.render(str, True, (0, 0, 0))
    text_rect = text.get_rect()
    text_rect.center = (a + c / 2, b + d / 2)
    win.blit(text, text_rect)
    pg.display.update()


def pos_in_rect(x1, y1, x2, y2, pos):
    return x1 <= pos[0] and x2 >= pos[0] and y1 <= pos[1] and y2 >= pos[1]


def menu_screen(n):
    win = pg.display.set_mode((width, height))
    win.fill((255, 255, 255))
    pg.display.set_caption("Точки")

    run = True
    clock = pg.time.Clock()
    while run:
        clock.tick(60)

        playX, playY, playWidth, playHeight = 100, 100, 400, 100
        label(win, "Click to play", (255, 0, 255), playX, playY, playWidth, playHeight)

        # regX, regY, regWidth, regHeight = 100, 220, 400, 100
        # label(win, "Registration", (255, 0, 255), regX, regY, regWidth, regHeight)
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                pg.quit()
                run = False
            if event.type == pg.MOUSEBUTTONDOWN:
                pos = pg.mouse.get_pos()
                print(pos)
                if pos_in_rect(playX, playY, playX + playWidth, playY + playHeight, pos):
                    print(n.send("ready"))
                    playground(win, n)
                    run = False
        pg.display.update()


def playground(win, n):
    path = os.getcwd()
    note_sheet = pg.image.load(path + '\sheet.jpg')
    win.blit(note_sheet, (0, 50))

    label(win, "You 0", (128, 128, 128), 10, 10, 280, 40)
    label(win, "0 Opponent", (128, 128, 128), 310, 10, 280, 40)

    pg.display.update()

    # game = n.send("get")
    name1 = 'You'
    name2 = 'Opponent'

    n.set_p()
    player = n.get_player()

    run = True
    while run:
        try:
            pg.time.delay(60)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    exit()
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    pos = pg.mouse.get_pos()
                    if pos_in_rect(512, 26, 593, 107, pos):
                        n.send("concede")
                        return
                        # menu_screen(n)
                    else:
                        n.send(pos)

            game = n.send("get")

            if game.login2 != '':
                if player == 0:
                    name1 = game.login1
                    name2 = game.login2
                else:
                    name2 = game.login1
                    name1 = game.login2
            if game.winner != -1:
                MSG = GOVER
                if game.winner == player:
                    MSG = MSG + DELIM + WINNER
                if game.winner == 3:
                    MSG = MSG + DELIM + TIE
                label(win, MSG, (255, 255, 255), width / 2 - 150, height / 2 - 50, 300, 100)
                pg.time.delay(2000)

                redraw(win, n.send("concede"))
                return

            if player == 0:
                label(win, name1 + ' ' + str(game.p1Score), game.p1Color, 10, 10, 280, 40)
                label(win, str(game.p2Score) + ' ' + name2, game.p2Color, 310, 10, 280, 40)
            else:
                label(win, name1 + ' ' + str(game.p2Score), game.p2Color, 10, 10, 280, 40)
                label(win, str(game.p1Score) + ' ' + name2, game.p1Color, 310, 10, 280, 40)

            redraw(win, game)
        except:
            pass


if __name__ == '__main__':
    n = Network()

    master = tk.Tk()
    tk.Label(master, text="Login").grid(row=0)
    tk.Label(master, text="Password").grid(row=1)

    e1 = tk.Entry(master)
    e2 = tk.Entry(master, show='*')

    master.title('Dots')

    e1.grid(row=0, column=1)
    e2.grid(row=1, column=1)
    is_second = 0

    def enter_login():
        login = e1.get()
        password = e2.get()
        string = 'log' + '\a' + login + '\a' + password +'\a'
        is_valid = n.send(string)
        if is_valid == 1:
            master.destroy()
        elif is_valid == 0:
            messagebox.showerror("Error", "Wrong password, try again")
        elif is_valid == -1:
            messagebox.showerror("Error", "Current user is active")
        elif is_valid == -2:
            messagebox.showerror("Error", "User is unregistered")
        global is_second
        is_second = 1

    def enter_reg():
        login = e1.get()
        password = e2.get()
        string = 'reg' + '\a' + login + '\a' + password
        is_valid = n.send(string)
        if is_valid:
            master.destroy()
        else:
            messagebox.showerror("Error", "User with this login already exists")
        global is_second
        is_second = 1

    # enter_login
    tk.Button(master, text='Enter', command=enter_login).grid(row=3, column=1, sticky=tk.W, pady=4)
    tk.Button(master, text='Registration', command=enter_reg).grid(row=4, column=1, sticky=tk.W, pady=4)
    print(is_second)
    master.mainloop()

    while True:
        menu_screen(n)

