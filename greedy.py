# coding:utf-8

import msvcrt
import random
import setup
import qlearn
import config as cfg
import queue
import importlib

importlib.reload(setup)
importlib.reload(qlearn)


def pick_random_location():
    while 1:
        x = random.randrange(world.width)
        y = random.randrange(world.height)
        cell = world.get_cell(x, y)
        if not (cell.wall or len(cell.agents) > 0):
            return cell


class Guard(setup.Agent):
    def __init__(self, filename):
        self.cell = None
        self.dir = 0;
        self.guardWin = 0
        self.color = cfg.guard_color
        f = open(filename)
        lines = f.readlines()
        lines = [x.rstrip() for x in lines]
        self.fh = len(lines)
        self.fw = max([len(x) for x in lines])
        self.grid_list = [[1 for x in range(self.fw)] for y in range(self.fh)]
        self.move = [(1, 0), (0, 0), (0, 1), (0, -1)]

        for y in range(self.fh):
            line = lines[y]
            for x in range(min(self.fw, len(line))):
                t = 1 if (line[x] == 'X') else 0
                self.grid_list[y][x] = t

    # using BFS algorithm to move quickly to target.
    def bfs_move(self, target):
        if self.cell == target:
            return

        for n in self.cell.neighbors:
            if n == target:
                self.cell = target  # if next move can go towards target
                return

        best_move = None
        best_dir = None
        q = queue.Queue()
        start = (self.cell.y, self.cell.x, self.dir)
        end = (target.y, target.x)
        q.put(start)
        step = 1
        V = {}
        preV = {}
        V[(start[0], start[1], start[2])] = 1

        while not q.empty():
            grid = q.get()

            for i in range(4):
                if self.move[i][0] == 0:
                    ny, nx, ndir = grid[0], grid[1], (grid[2] + self.move[i][1]) % 4
                else:
                    ndir = grid[2]
                    ny, nx = grid[0], grid[1]
                    if ndir == 0:
                        ny += 1
                    elif ndir == 1:
                        nx += 1
                    elif ndir == 2:
                        ny -= 1
                    elif ndir == 3:
                        nx -= 1
                if nx < 0 or ny < 0 or nx > (self.fw-1) or ny > (self.fh-1):
                    continue
                if self.get_value(V, (ny, nx, ndir)) or self.grid_list[ny][nx] == 1:  # has visit or is wall.
                    continue

                preV[(ny, nx, ndir)] = self.get_value(V, (grid[0], grid[1], grid[2]))
                if ny == end[0] and nx == end[1]:
                    V[(ny, nx, ndir)] = step + 1
                    seq = []
                    last = V[(ny, nx, ndir)]
                    while last > 1:
                        k = [key for key in V if V[key] == last]
                        seq.append(k[0])
                        assert len(k) == 1
                        last = preV[(k[0][0], k[0][1], k[0][2])]
                    seq.reverse()
                    best_move = world.grid[seq[0][0]][seq[0][1]]
                    best_dir = seq[0][2]

                q.put((ny, nx, ndir))
                step += 1
                V[(ny, nx, ndir)] = step

        if best_move is not None:
            self.cell = best_move
            self.dir = best_dir
        else:
            dir = random.randrange(4)
            self.go_direction(dir)

    def get_value(self, mdict, key):
        try:
            return mdict[key]
        except KeyError:
            return 0

    def update(self):
        if self.cell != thief.cell:
            self.bfs_move(thief.cell)

class Escape(setup.Agent):
    def __init__(self):
        self.color = cfg.escape_color

    def update(self):
        pass


class Thief(setup.Agent):
    def __init__(self):
        self.ai = None
        self.ai = qlearn.QLearn(actions=range(4), alpha=0.1, gamma=0.9, epsilon=0.1)
        self.guardWin = 0
        self.thiefWin = 0
        self.lastState = None
        self.lastAction = None
        self.color = cfg.thief_color

    def update(self):
        state = self.calculate_state()
        reward = cfg.MOVE_REWARD

        if self.cell == guard.cell:
            self.guardWin += 1
            reward = cfg.CAUGHT
            if self.lastState is not None:
                self.ai.learn(self.lastState, self.lastAction, state, reward)
            self.lastState = None
            self.cell = world.get_cell(1,1)
            guard.cell = pick_random_location()
            return

        if self.cell == escape.cell:
            self.thiefWin += 1
            reward = cfg.ESCAPE
            if self.lastState is not None:
                self.ai.learn(self.lastState, self.lastAction, state, reward)
            self.lastState = None
            self.cell = world.get_cell(1,1)
            guard.cell = pick_random_location()
            self.escapeReward = cfg.ESCAPE
            escape.cell = world.get_cell(world.width - 2,world.height - 2)

        if self.lastState is not None:
            self.ai.learn(self.lastState, self.lastAction, state, reward)

        # choose a new action and execute it
        action = self.ai.choose_action(state)
        self.lastState = state
        self.lastAction = action
        self.go_direction(action)

    def calculate_state(self):
        def cell_value(cell):
            # 3 if caught, 2 if finish, 1 if there is wall,0 if none
            if guard.cell is not None and (cell.x == guard.cell.x and cell.y == guard.cell.y):
                return 3
            elif escape.cell is not None and (cell.x == escape.cell.x and cell.y == escape.cell.y):
                return 2
            else:
                return 1 if cell.wall else 0

        dirs = [(-1, 0), (0, -1), (0, 1), (1, 0)]
        return tuple([cell_value(world.get_relative_cell(self.cell.x + dir[0], self.cell.y + dir[1])) for dir in dirs])

if __name__ == '__main__':
    thief = Thief()
    guard = Guard(filename='resources/world.txt')
    escape = Escape()
    world = setup.World(filename='resources/world.txt')

    world.add_agent(thief, cell = world.get_cell(1,1))
    world.add_agent(escape, cell = world.get_cell(world.width - 2,world.height - 2))
    world.add_agent(guard, cell = pick_random_location())

    world.display.activate()
    world.display.speed = cfg.speed

    while 1:
        world.update(thief.thiefWin, thief.guardWin)
        if msvcrt.kbhit():
            break
    world.agents[0].ai.memorize()
