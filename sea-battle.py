from random import randint

import time


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Out of playing board!"


class BoardUsedException(BoardException):
    def __str__(self):
        return "Already shot at this position!"


class BoardWrongShipException(BoardException):
    pass


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'Dot ({self.x}, {self.y})'



class WarShip:
    def __init__(self, position, lives, orient):
        self.size = lives
        self.position = position
        self.orient = orient
        self.lives = lives

    @property
    def hull(self):
        ship_hull = []

        for i in range(self.size):
            st_x = self.position.x
            st_y = self.position.y

            if self.orient == 0:
                st_x += i

            elif self.orient == 1:
                st_y += i

            ship_hull.append(Dot(st_x, st_y))

        return ship_hull

    def shooten(self, shot):
        return shot in self.hull


class Board:
    def __init__(self, size=6, hide=False):
        self.size = size
        self.hide = hide

        self.field = [["o"] * size for _ in range(size)]

        self.count = 0

        self.occupied = []
        self.ships = []

    def add_ship(self, ship):
        for d in ship.hull:
            if self.out(d) or d in self.occupied:
                raise BoardWrongShipException()
        for d in ship.hull:
            self.field[d.x][d.y] = "■"
            self.occupied.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.hull:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.occupied:
                    if verb:
                        self.field[cur.x][cur.y] = "·"
                    self.occupied.append(cur)

    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i+1} | " + " | ".join(row) + " |"

        if self.hide:
            res = res.replace("■", "o")
        return res

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.occupied:
            raise BoardUsedException()

        self.occupied.append(d)

        for ship in self.ships:
            if ship.shooten(d):
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return True
                else:
                    print("Корабль ранен!")
                    return True

        self.field[d.x][d.y] = "·"
        print("Мимо!")
        return False

    def begin(self):
        self.occupied = []

    def defeat(self):
        return self.count == len(self.ships)


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        time.sleep(3)
        d = Dot(randint(0,5), randint(0, 5))
        print(f"Ход компьютера: {d.x+1} {d.y+1}")
        return d


class User(Player):
    def ask(self):
        while True:
            coords = input("Ваш ход: ").split()

            if len(coords) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = coords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)



class Game:
    def __init__(self, size=6):
        self.lens = [3, 2, 2, 1, 1, 1, 1]
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hide = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_dispos()
        return board

    def random_dispos(self):
        board = Board(size=self.size)
        attempts = 0
        for l in self.lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = WarShip(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def greet(self):
        print("     -------------------")
        print("       Приветсвуем вас  ")
        print("           в игре       ")
        print("         морской бой    ")
        print("     -------------------")
        print("      формат ввода: x y ")
        print("      x - номер строки  ")
        print("      y - номер столбца ")

    def print_boards(self):
        print("-" * 27)
        print("     Доска пользователя:", self.us.board, sep="\n")
        print("-" * 27)
        print("     Доска компьютера:", self.ai.board, sep="\n")

    def loop(self):
        num = 0
        while True:
            self.print_boards()
            if num % 2 == 0:
                print("-" * 20)
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.defeat():
                self.print_boards()
                print("-" * 20)
                print("Пользователь выиграл!")
                break

            if self.us.board.defeat():
                self.print_boards()
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()



g = Game()
g.start()