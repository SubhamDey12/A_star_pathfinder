import pygame
from queue import PriorityQueue

normal_block_color = (108,212,212)
visited_color = (255, 0, 0)
visiting_color = (0, 255, 0)
blockage_color = (0, 0, 0)
start_color = (255, 165 ,0)
end_color = (204, 255, 229)
path_color = (128, 0, 128)
block_edge_color = (128, 128, 128)


#Creating the output interface

size = 1000
win = pygame.display.set_mode((size,size))
pygame.display.set_caption("Pathfinder Visualizer using A*")


class block :
	def __init__(self, row, col, size, total_rows):
		self.row = row
		self.col = col
		self.x = row * size
		self.y = col * size
		self.color = normal_block_color
		self.neighbors = []
		self.size = size
		self.total_rows = total_rows
	
	def get_location(self):
		return self.row, self.col

	def is_visited(self):
		return self.color == visited_color

	def is_just_visiting(self):
		return self.color == visiting_color

	def is_blockage(self):
		return self.color == blockage_color

	def is_start(self):
		return self.color == start_color

	def is_end(self):
		return self.color == end_color

	def reset(self):
		self.color = normal_block_color

	def make_start(self):
		self.color = start_color
	
	def make_end(self):
		self.color = end_color

	def make_visited(self):
		self.color = visited_color

	def make_visiting(self):
		self.color = visiting_color

	def make_blockage(self):
		self.color = blockage_color

	def make_path(self):
		self.color = path_color

	def draw(self, win):
		pygame.draw.rect(win, self.color, (self.x, self.y, self.size, self.size))

	def update_neighbors(self, grid):
		self.neighbors = []
		if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_blockage(): # DOWN
			self.neighbors.append(grid[self.row + 1][self.col])

		if self.row > 0 and not grid[self.row - 1][self.col].is_blockage(): # UP
			self.neighbors.append(grid[self.row - 1][self.col])

		if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_blockage(): # RIGHT
			self.neighbors.append(grid[self.row][self.col + 1])

		if self.col > 0 and not grid[self.row][self.col - 1].is_blockage(): # LEFT
			self.neighbors.append(grid[self.row][self.col - 1]) 

def create_block(rows, size):
	grid = []
	gap = size // rows
	for i in range(rows):
		grid.append([])
		for j in range(rows):
			current_spot = block(i, j, gap, rows)
			grid[i].append(current_spot)
	return grid	

def draw_block(win, rows, size):
	gap = size // rows
	for i in range(rows):
		pygame.draw.line(win, block_edge_color, (0, i * gap), (size, i * gap))
		pygame.draw.line(win, block_edge_color, (i * gap, 0), (i * gap, size))

def draw_with_details(win, grid, rows, size):
	win.fill(normal_block_color)
	for row in grid:
		for current_spot in row:
			current_spot.draw(win)
	draw_block(win, rows, size)
	pygame.display.update()


#To take the mouse click as input

def clicked(pos, rows, size):
	gap = size // rows
	x, y = pos
	row = x // gap
	col = y // gap
	return row, col


#Algorithm

def h(p1, p2):
	x1, y1 = p1
	x2, y2 = p2
	return abs(x2 - x1) + abs(y2 - y1)

def create_path(whose_neighbour, current_block, draw):
	while current_block in whose_neighbour:
		current_block = whose_neighbour[current_block]
		current_block.make_path()
		draw()


def algorithm(draw, grid, start, end):
	count = 0
	storage = PriorityQueue()
	storage.put((0,count,start))
	whose_neighbour = {}
	g_score = {spot: float("inf") for row in grid for spot in row}
	g_score[start] = 0
	f_score = {spot: float("inf") for row in grid for spot in row}
	f_score[start] = h(start.get_location(), end.get_location())
	visited_checker = {start}

	while not storage.empty():
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()

		current_block = storage.get()[2]
		visited_checker.remove(current_block)

		if current_block == end:
			create_path(whose_neighbour, end, draw)
			end.make_end()
			return True
		for neighbor in current_block.neighbors:
			temp_g_score = g_score[current_block] + 1

			if temp_g_score < g_score[neighbor]:
				whose_neighbour[neighbor] = current_block
				g_score[neighbor] = temp_g_score
				f_score[neighbor] = temp_g_score + h(neighbor.get_location(), end.get_location())
				if neighbor not in visited_checker:
					count += 1
					storage.put((f_score[neighbor], count, neighbor))
					visited_checker.add(neighbor)
					neighbor.make_visiting()
		draw()

		if current_block != start:
			current_block.make_visited()

	return False

#Main Function

def main(win, size):
	ROWS = 50
	grid = create_block(ROWS, size)
	start = None
	end = None
	loop_runner = True
	while loop_runner:
		draw_with_details(win, grid, ROWS, size)
		for event in pygame.event.get():

			if event.type == pygame.QUIT:
				loop_runner = False

			if pygame.mouse.get_pressed()[0]: # LEFT
				pos = pygame.mouse.get_pos()
				row, col = clicked(pos, ROWS, size)
				current_spot = grid[row][col]

				if not start and current_spot != end:
					start = current_spot
					start.make_start()
				
				elif not end and current_spot != start:
					end = current_spot
					end.make_end()
				
				elif current_spot != end and current_spot != start:
					current_spot.make_blockage()

			elif pygame.mouse.get_pressed()[2]: # RIGHT
				pos = pygame.mouse.get_pos()
				row, col = clicked(pos, ROWS, size)
				current_spot = grid[row][col]
				current_spot.reset()
				if current_spot == start:
					start = None
				elif current_spot == end:
					end = None

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE and start and end:
					for row in grid:
						for current_spot in row:
							current_spot.update_neighbors(grid)

					algorithm(lambda: draw_with_details(win, grid, ROWS, size), grid, start, end)


	pygame.quit()
main(win, size)

