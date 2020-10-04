import cv2
import random
import numpy as np
import time
from enum import Enum

class GameState(Enum):
	RUNNING = 0
	WIN = 1
	LOSS = 2
	EXIT = 3

class MineSweeper:

	def __init__(self, xdim, ydim, n_mines):
		self.xdim = xdim
		self.ydim = ydim
		self.n_mines = min(n_mines, xdim * ydim-1)
		self.upscale = 1000 // self.xdim
		self.slowest_refresh = 4.0
		self.fastest_refresh = 1.0
		self.canvas = np.zeros(
			((self.ydim+1) * self.upscale, self.xdim * self.upscale, 3), 
			dtype = np.uint8)
		self.cell_canvas = None
		self.window_name = "Nightmare Minesweeper"
		cv2.namedWindow(self.window_name, cv2.WINDOW_GUI_NORMAL)
		cv2.resizeWindow(self.window_name, 
			self.xdim * self.upscale, (self.ydim+1) * self.upscale)
		cv2.setMouseCallback(self.window_name, self.on_mouse)
		self.replay_game()


	def replay_game(self):
		self.clicks = set()
		self.markings = set()
		self.correct_markings = set()
		self.game_state = GameState.RUNNING
		self.refresh_time = self.slowest_refresh
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
		p = len(self.correct_markings) / self.n_mines
		self.refresh_time = self.slowest_refresh - dt * p

	def resweep(self):
		t0 = time.time()
		self.board = [[0 for _ in range(self.xdim)] 
			for _ in range(self.ydim)]
		self.revealed = [[False for _ in range(self.xdim)] 
			for _ in range(self.ydim)]
		self.marked_mines = [[False for _ in range(self.xdim)] 
			for _ in range(self.ydim)]
		self.place_mines()
		for px, py in self.markings:
			self.marked_mines[py][px] = True
		for px, py in self.clicks:
			self.reveal(px, py)
		self.last_resweep = time.time()
		self.calculate_refresh_time()
		self.draw_board()
		t1 = time.time()

	def place_mines(self):
		for bx, by in self.correct_markings:
			self.board[by][bx] = -1
			for x, y in self.get_neighbors(bx, by):
				if self.board[y][x] != -1:
					self.board[y][x] += 1

		for _ in range(self.n_mines - len(self.correct_markings)):
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
			self.reveal_full_board()
			self.game_state = GameState.LOSS
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

	def reveal_full_board(self):
		for row in range(self.ydim):
			for col in range(self.xdim):
				self.revealed[row][col] = True

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

	def put_text(self, x, y, text, color, font_size = None):
		font = cv2.FONT_HERSHEY_PLAIN
		if font_size is None:
			font_size = 0.05 * self.upscale
		cv2.putText(self.canvas, text, (x, y), font, font_size, color, 2)

	def draw_text(self, row, col):
		text_pos = (int(self.upscale*(col+.3)),int(self.upscale*(row+.8)))
		if not self.marked_mines[row][col]:
			if self.board[row][col] > 0 and self.revealed[row][col]:
				s = str(self.board[row][col])
				self.put_text(*text_pos, s, (0, 255, 0))
			elif self.board[row][col] == -1 and self.revealed[row][col]:
				s = "x"
				self.put_text(*text_pos, s, (0, 0, 255))
		else:
			self.put_text(*text_pos, "B", (0, 0, 255))

	def draw_click(self, row, col):
		text_pos = (int(self.upscale*(col+.1)),int(self.upscale*(row+.9)))
		self.put_text(*text_pos, "x", (255, 255, 255), 0.01 * self.upscale)

	def draw_board(self):
		t0 = time.time()
		for row in range(self.ydim):
			for col in range(self.xdim):
				self.draw_background(row, col)
				if self.marked_mines[row][col] or self.revealed[row][col]:
					self.draw_text(row, col)
				if (col, row) in self.clicks:
					self.draw_click(row, col)
		t1 = time.time()
		self.draw_stats()

	def draw_stats(self):
		self.canvas[self.upscale*self.ydim:,:,:] = 0
		y_pos = int(self.upscale*(self.ydim+.8))
		mine_pos = int(self.upscale*(2+.2))
		click_pos = int(self.upscale*(7+.2))
		n_mines = self.n_mines - len(self.markings)
		self.put_text(mine_pos, y_pos, "B: %d" % n_mines, (0, 0, 255))
		clicks_str = "C: %d" % len(self.clicks)
		self.put_text(click_pos, y_pos, clicks_str, (255, 255, 255))

	def main_loop(self):
		while self.game_state == GameState.RUNNING:
			cv2.imshow(self.window_name,self.canvas)
			if cv2.waitKey(10) & 0xFF == ord("q"):
				self.game_state = GameState.EXIT
				break
			if time.time() - self.last_resweep > self.refresh_time:
				self.resweep()
		if self.game_state != GameState.EXIT:
			self.game_over_loop()

	def draw_text_box(self, text):
		y0, y1 = self.upscale * self.ydim//3, self.upscale * 2*self.ydim//3
		x0, x1 = self.upscale * self.xdim//8, self.upscale * 7*self.ydim//8
		self.canvas[y0:y1,x0:x1,:] //= 3

		font = cv2.FONT_HERSHEY_PLAIN
		textsize = cv2.getTextSize(text, font, 0.1 * self.upscale, 2)[0]
		text_pos = (
			int(self.upscale*(self.xdim/2) - textsize[0] / 2),
			int(self.upscale*(self.ydim/2) + textsize[1] / 2)
		)
		self.put_text(*text_pos, text, (0, 255, 0), 0.1 * self.upscale)

	def draw_loss_screen(self):
		self.draw_text_box("GAME OVER!")

	def draw_win_screen(self):
		self.draw_text_box("GAME WON!")

	def game_over_loop(self):
		if self.game_state == GameState.WIN:
			self.draw_win_screen()
		else:
			self.draw_loss_screen()
		while self.game_state == GameState.LOSS or self.game_state == GameState.WIN:
			cv2.imshow(self.window_name,self.canvas)
			if cv2.waitKey(10) & 0xFF == ord("q"):
				self.game_state = GameState.EXIT
				break

	def left_click(self, cx, cy):
		if not self.revealed[cy][cx] and self.game_state == GameState.RUNNING:
			self.clicks.add((cx, cy))
			self.reveal(cx, cy)
		elif self.game_state != GameState.RUNNING:
			self.replay_game()

	def check_win(self):
		if len(self.correct_markings) == len(self.markings) == self.n_mines:
			self.game_state = GameState.WIN

	def mark_mine(self, cx, cy):
		if not self.revealed[cy][cx] and len(self.markings) < self.n_mines:
			self.marked_mines[cy][cx] = True
			self.markings.add((cx, cy))
			if self.board[cy][cx] == -1:
				self.correct_markings.add((cx, cy))
			else:
				self.reveal_full_board()
				self.game_state = GameState.LOSS
			# print("mark", len(self.correct_markings), len(self.markings))
			self.check_win()

	def unmark_mine(self, cx, cy):
		self.marked_mines[cy][cx] = False
		self.markings.remove((cx, cy))
		if self.board[cy][cx] == -1:
			self.correct_markings.remove((cx, cy))
		# print("unmark", len(self.correct_markings), len(self.markings))
		self.check_win()

	def right_click(self, cx, cy):
		if not self.marked_mines[cy][cx]:
			self.mark_mine(cx, cy)
		else:
			self.unmark_mine(cx, cy)

	def on_mouse(self, event, x, y, flags, param):
		cx = x // self.upscale
		cy = y // self.upscale
		if event == cv2.EVENT_LBUTTONDOWN:
			self.left_click(cx, cy)
			self.draw_board()
		elif event == cv2.EVENT_RBUTTONDOWN and self.game_state == GameState.RUNNING:
			self.right_click(cx, cy)
			self.draw_board()


game = MineSweeper(15, 15, 20)
while game.game_state != GameState.EXIT:
	print("test", game.game_state)
	game.main_loop()