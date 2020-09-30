import cv2
import random
import numpy as np
import time

class MineSweeper:

	def __init__(self, xdim, ydim, n_bombs):
		self.xdim = xdim
		self.ydim = ydim
		self.n_bombs = min(n_bombs, xdim * ydim-1)
		self.upscale = 1000 // self.xdim
		self.clicks = set()
		self.markings = set()
		self.correct_markings = set()
		self.slowest_refresh = 4.0
		self.fastest_refresh = 1.0
		self.refresh_time = self.slowest_refresh
		self.game_over = False
		self.canvas = np.zeros(
			((self.ydim+1) * self.upscale, self.xdim * self.upscale, 3), 
			dtype = np.uint8)
		self.cell_canvas = None
		cv2.namedWindow('sweeper', cv2.WINDOW_GUI_NORMAL)
		cv2.resizeWindow('sweeper', 
			self.xdim * self.upscale, (self.ydim+1) * self.upscale)
		cv2.setMouseCallback('sweeper', self.on_mouse)
		self.resweep()

	def get_neighbors(self, x, y):
		neighbors = [(x-i, y-j) for i in range(-1, 2) 
			for j in range(-1, 2) if i != 0 or j != 0]
		# neighbors.remove((x, y))
		# print(neighbors)
		valid = lambda x: 0 <= x[0] < self.xdim and 0 <= x[1] < self.ydim
		filtered = filter(valid, neighbors)
		return filtered

	def calculate_refresh_time(self):
		dt = self.slowest_refresh - self.fastest_refresh
		p = len(self.correct_markings) / self.n_bombs
		self.refresh_time = self.slowest_refresh - dt * p

	def resweep(self):
		t0 = time.time()
		self.board = [[0 for _ in range(self.xdim)] 
			for _ in range(self.ydim)]
		self.revealed = [[False for _ in range(self.xdim)] 
			for _ in range(self.ydim)]
		self.marked_bombs = [[False for _ in range(self.xdim)] 
			for _ in range(self.ydim)]
		self.place_bombs()
		for px, py in self.markings:
			self.marked_bombs[py][px] = True
		for px, py in self.clicks:
			self.reveal(px, py)
		self.last_resweep = time.time()
		self.calculate_refresh_time()
		self.draw_board()
		t1 = time.time()
		# print(t1-t0)

	def place_bombs(self):
		for bx, by in self.correct_markings:
			self.board[by][bx] = -1
			for x, y in self.get_neighbors(bx, by):
				if self.board[y][x] != -1:
					self.board[y][x] += 1

		for _ in range(self.n_bombs - len(self.correct_markings)):
			while True:
				rx = random.randint(0, self.xdim-1)
				ry = random.randint(0, self.ydim-1)
				if (self.board[ry][rx] != -1 
					and (rx, ry) not in self.clicks
					and (rx, ry) not in self.markings):
					break

			self.board[ry][rx] = -1
			for x, y in self.get_neighbors(rx, ry):
				if self.board[y][x] != -1:
					self.board[y][x] += 1
		# self.print_board()

	def print_board(self):
		for row in self.board:
			print(" ".join(map(lambda x: "%2d" % x, row)))

	def reveal(self, x, y):
		# print("revealing", x, y)
		if self.board[y][x] == -1:
			print("GAME LOST!")
			self.game_over = True
		visited = set((x, y))
		stack = [(x, y)]
		while stack:
			# print(stack)
			px, py = stack.pop()
			# visited.add((px, py))
			if self.board[py][px] == 0:
				for neighbor in self.get_neighbors(px, py):
					if neighbor not in visited:
						stack.append(neighbor)
						visited.add(neighbor)
			if (px, py) not in self.markings:
				self.revealed[py][px] = True


	def get_cell(self):
		if self.cell_canvas is not None:
			return self.cell_canvas
		self.cell_canvas = np.zeros(
			(self.upscale, self.upscale, 3), dtype = np.uint8)
		self.cell_canvas[:,:,:] = 150
		self.cell_canvas[0,:,:] = 0
		self.cell_canvas[-1,:,:] = 0
		self.cell_canvas[:,0,:] = 0
		self.cell_canvas[:,-1,:] = 0
		return self.cell_canvas

	def get_dark_cell(self):
		return self.get_cell() // 2

	def draw_background(self, row, col):
		y0, y1 = row*self.upscale, (row+1)*self.upscale
		x0, x1 = col*self.upscale, (col+1)*self.upscale
		if not self.revealed[row][col]:
			self.canvas[y0:y1, x0:x1,:] = self.get_cell()
		else:
			self.canvas[y0:y1, x0:x1,:] = self.get_dark_cell()

	def put_text(self, x, y, text, color):
		font = cv2.FONT_HERSHEY_PLAIN
		font_size = 0.05 * self.upscale
		cv2.putText(self.canvas, text, (x, y), font, font_size, color, 2)

	def draw_text(self, row, col):
		s = ""
		if self.board[row][col] > 0 and self.revealed[row][col]:
			s = str(self.board[row][col])

		text_pos = (int(self.upscale*(col+.3)),int(self.upscale*(row+.8)))
		self.put_text(*text_pos, s, (0, 255, 0))
		if self.marked_bombs[row][col]:
			self.put_text(*text_pos, "B", (0, 0, 255))

	def draw_board(self):
		t0 = time.time()
		for row in range(self.ydim):
			for col in range(self.xdim):
				self.draw_background(row, col)
				if self.marked_bombs[row][col] or self.revealed[row][col]:
					self.draw_text(row, col)
		t1 = time.time()
		self.draw_stats()

	def draw_stats(self):
		self.canvas[self.upscale*self.ydim:,:,:] = 0
		y_pos = int(self.upscale*(self.ydim+.8))
		bomb_pos = int(self.upscale*(2+.2))
		click_pos = int(self.upscale*(7+.2))
		n_bombs = self.n_bombs - len(self.markings)
		self.put_text(bomb_pos, y_pos, "B: %d" % n_bombs, (0, 0, 255))
		clicks_str = "C: %d" % len(self.clicks)
		self.put_text(click_pos, y_pos, clicks_str, (255, 255, 255))

	def main_loop(self):
		while not self.game_over:
			cv2.imshow('sweeper',self.canvas)
			if cv2.waitKey(10) & 0xFF == ord("q"):
				break
			if time.time() - self.last_resweep > self.refresh_time:
				self.resweep()

	def left_click(self, cx, cy):
		if not self.revealed[cy][cx]:
			self.clicks.add((cx, cy))
			self.reveal(cx, cy)

	def check_win(self):
		if len(self.correct_markings) == len(self.markings) == self.n_bombs:
			print("GAME WON!")
			self.game_over = True

	def mark_bomb(self, cx, cy):
		if not self.revealed[cy][cx] and len(self.markings) < self.n_bombs:
			self.marked_bombs[cy][cx] = True
			self.markings.add((cx, cy))
			if self.board[cy][cx] == -1:
				self.correct_markings.add((cx, cy))
			# print("mark", len(self.correct_markings), len(self.markings))
			self.check_win()

	def unmark_bomb(self, cx, cy):
		self.marked_bombs[cy][cx] = False
		self.markings.remove((cx, cy))
		if self.board[cy][cx] == -1:
			self.correct_markings.remove((cx, cy))
		# print("unmark", len(self.correct_markings), len(self.markings))
		self.check_win()

	def right_click(self, cx, cy):
		if not self.marked_bombs[cy][cx]:
			self.mark_bomb(cx, cy)
		else:
			self.unmark_bomb(cx, cy)

	def on_mouse(self, event, x, y, flags, param):
		cx = x // self.upscale
		cy = y // self.upscale
		if event == cv2.EVENT_LBUTTONDOWN:
			self.left_click(cx, cy)
			self.draw_board()
		elif event == cv2.EVENT_RBUTTONDOWN:
			self.right_click(cx, cy)
			self.draw_board()


game = MineSweeper(15, 15, 20)
game.main_loop()