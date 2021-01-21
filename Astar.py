import pygame
import math
from queue import PriorityQueue



WIDTH = 800
WIN = pygame.display.set_mode((WIDTH, WIDTH))  #creating the display which is square
pygame.display.set_caption("A* visualizer")  #name for the window

RED = (255, 0, 0)    #defining the colors
GREEN = (0, 255, 0)
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165 ,0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

class Spot:    #creating a class for the small boxes
    def __init__(self, row, col, width, total_rows):
        self.row=row
        self.col=col
        self.x=row*width
        self.y=col*width
        self.color=WHITE
        self.neighbors = []
        self.width=width
        self.total_rows=total_rows
    
    def get_pos(self):    #gets the position of a spot
        return self.row, self.col
    
    def is_closed(self):   
        return self.color == RED

    def is_open(self):     #
        return self.color == GREEN
    
    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == ORANGE
    
    def is_end(self):
        return self.color == TURQUOISE

    def reset(self):   #resets the spot to white
        self.color = WHITE
    
    def make_closed(self):   #if its a path covered during tracing, it will be red
        self.color = RED

    def make_open(self):  #creates the imaginary boundary for the currently drawn spots
        self.color = GREEN
    
    def make_barrier(self):  #on drawing the barrier, its black
        self.color = BLACK

    def make_start(self):   #start node is orange
        self.color = ORANGE
    
    def make_end(self):    #end node is turquoise
        self.color = TURQUOISE
    
    def make_path(self):  #the shortest path is traced with purple
        self.color = PURPLE

    def draw(self,win):  #draws on a spot 
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):  #stores the neighbor spots of the current spot
        self.neighbors = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():  #DOWN
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():  #UP
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():  #RIGHT
            self.neighbors.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():  #LEFT
            self.neighbors.append(grid[self.row][self.col - 1])
    
    def __lt__(self,other):
        return False

def h(p1, p2):  #heuristic for the A* i.e. keeping track of the distance left. we use manhattan distance or L-distance.
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def reconstruct_path(came_from, current, draw):   #it traces the paths according to the algorithm
	while current in came_from:
		current = came_from[current]
		current.make_path()
		draw()

def algorithm(draw, grid, start, end):  #implements the A* algorithm
    count = 0   #two keep track of when a node was inserted so that if two nodes have the same f-score, then we put the one at first which was taken before
    open_set = PriorityQueue()
    open_set.put((0,count,start))  #(f-score, count, current)
    came_from = {}
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score = {spot: float("inf") for row in grid for spot in row}
    f_score[start] = h(start.get_pos(), end.get_pos())

    open_set_hash = {start}  #stores the nodes of the priority queue, as we cannot remove items from PQ, we will use this to keep track of what was removed

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        
        current = open_set.get()[2]  #taking only the node part from the PQ, that has the minimum f_score(speciality of PQ)
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            start.make_start()
            return True
            
        
        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1
            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count+=1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()
        draw()

        if current != start:
            current.make_closed()
    
    return False




def make_grid(rows, width):  #storing the spots in a data structure
    grid = []
    gap = width//rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            spot = Spot(i, j, gap, rows)
            grid[i].append(spot)
    
    return grid

def draw_grid(win, rows, width):  #for the grid lines
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i*gap), (width, i*gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j*gap, 0), (j*gap, width))

def draw(win, grid, rows, width):
    win.fill(WHITE)

    for row in grid:
        for spot in row:
            spot.draw(win)  #draw method for spot class that draws the rectangle
    
    draw_grid(win, rows, width)  #now draw the lines
    pygame.display.update()

def get_clicked_pos(pos, rows, width):    #gets position of the spot we click on
    gap = width // rows
    y, x = pos

    row = y // gap
    col = x // gap

    return row, col

def main(win, width):   #main function to detects clicks and presses to draw accordingly
    ROWS = 50   #we can change this
    grid = make_grid(ROWS, width)

    start = None
    end = None
    run = True

    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():   #for any event we perform like clicking etc.
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]:  #left mouse clicked
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                if not start and spot != end:
                    start = spot
                    start.make_start()

                if not end and spot != start:
                    end = spot
                    end.make_end()

                elif spot!=end and spot!=start:
                    spot.make_barrier()

            elif pygame.mouse.get_pressed()[2]:  #right mouse clicked
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                spot.reset()
                if spot == start:
                    start = None
                if spot == end:
                    end = None
                
            if event.type == pygame.KEYDOWN:  #a key is pressed
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)
                    
                    algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)

                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)

    pygame.quit()

main(WIN, WIDTH)

            







