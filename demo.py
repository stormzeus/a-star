import pygame
import math
from queue import PriorityQueue
import tkinter as tk
from tkinter import messagebox

WIDTH = 500
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption('A*')

# set colors
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)


class Spot:
    def __init__(self, row, col, width, tot_rows):
        self.row = row
        self.col = col
        self.x = row*width
        self.y = col*width
        self.color = WHITE
        self.neighbours = []
        self.width = width
        self.total_rows = tot_rows

    def get_pos(self):   # get the current coordinate of the spot
        return self.row, self.col

    def is_closed(self):   # check if the current spot has already been explored
        return self.color == RED

    def is_open(self):      # check if the current spot can be explored
        return self.color == GREEN

    def is_obstacle(self):   # check if the current spot is an onbstacle
        return self.color == BLACK

    def is_start(self):       # check if the current spot is the start point
        return self.color == ORANGE

    def is_end(self):          # check if the current spot is the end point 
        return self.color == TURQUOISE

    def reset(self):   #     # reset the select spot
        self.color = WHITE

    def make_closed(self):    # mark the spot as already explored
        self.color = RED

    def make_open(self):       # add the currently explored open spot to neighbours list
        self.color = GREEN

    def make_obstacle(self):   # make an obstacle spot
        self.color = BLACK

    def make_start(self):       # choose the start spot
        self.color = ORANGE

    def make_end(self):         #choose the end spot
        self.color = TURQUOISE

    def make_path(self):        # mark the path from start to end
        self.color = PURPLE

    def draw(self, win):        # initialize the GUI window
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbours(self, grid):   # add the visited open neighbours to a list
        self.neighbors = []
        # DOWN
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_obstacle():
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_obstacle():  # UP
            self.neighbors.append(grid[self.row - 1][self.col])

        # RIGHT
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_obstacle():
            self.neighbors.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].is_obstacle():  # LEFT
            self.neighbors.append(grid[self.row][self.col - 1])

    def __lt__(self, other):
        return False

 
def h(p1, p2):    #  define the heuristic function
    x1, y1 = p1
    x2, y2 = p2
    return abs(x2-x1)+abs(y2-y1)


def reconstruct_path(came_from, current, draw):  # make the path from the end spot to the start spot
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()


def error_msgbox():
    root = tk.Tk()
    root.withdraw()
    tk.messagebox.showerror(message='NO PATH FOUND')
    root.destroy()


def success_box():
    root = tk.Tk()
    root.withdraw()
    tk.messagebox.showinfo(message='PATH FOUND')
    root.destroy()


def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score = {spot: float("inf") for row in grid for spot in row}
    f_score[start] = h(start.get_pos(), end.get_pos())

    open_set_hash = {start}

    while not open_set.empty():    # perform the A* algorithm
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:    # check if the spot has reached the end and recreate the path to start spot
            reconstruct_path(came_from, end, draw)
            end.make_end()
            success_box()
            return True

        for neighbor in current.neighbors:     # update the heuristic for each spot and move closer to the end goal
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()

        draw()

        if current != start:
            current.make_closed()
    error_msgbox()
    return False

 
def make_grid(rows, width):     # make grid 
    grid = []
    gap = width//rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            spot = Spot(i, j, gap, rows)
            grid[i].append(spot)
    return grid


def draw_grid(win, rows, width):   # draw grid lines on the GUI window
    gap = width//rows
    for i in range(rows+1):
        pygame.draw.line(win, GREY, (0, i*gap), (width, i*gap))
    for j in range(rows+1):
        pygame.draw.line(win, GREY, (j*gap+1, 0), (j*gap+1, width))


def draw(win, grid, rows, width):   # make each spot white
    win.fill(WHITE)
    for row in grid:
        for spot in row:
            spot.draw(win)

    draw_grid(win, rows, width)
    pygame.display.update()


def get_clicked_pos(pos, rows, width):   # get the position of the clicked points (start, goal and obstacle)
    gap = width//rows
    y, x = pos
    row = y//gap
    col = x//gap
    return row, col


def main(win, width):
    ROWS = 50
    grid = make_grid(ROWS, width)

    start = None
    end = None
    run = True
    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if pygame.mouse.get_pressed()[0]:    
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                if not start and spot != end:   # create the starting point
                    start = spot
                    spot.make_start()
                elif not end and spot != start: # create the end point
                    end = spot
                    spot.make_end()
                elif spot != start and spot != end:     #draw the obstacle
                    spot.make_obstacle()

            elif pygame.mouse.get_pressed()[2]:   # reset the clicked point to WHITE on right click
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                spot.reset()
                if spot == start:
                    start = None
                elif spot == end:
                    end = None
            if event.type == pygame.KEYDOWN:    # start the algorithm on pressing the SPACE key
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbours(grid)

                    algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)

                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)

    pygame.quit()


main(WIN, WIDTH)
