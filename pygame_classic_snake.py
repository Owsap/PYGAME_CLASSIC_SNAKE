# Snake Game with Pygame

__author__ = "Owsap"
__copyright__ = "Copyright 2024, Owsap Development"

import sys, pygame
import random

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Misc.
SURFACE_COLOR = BLACK
BLOCK_SIZE = 20
SLIDER_WIDTH = 200

# Game States
STATE_WAIT = 0
STATE_PLAY = 1
STATE_END = 2

# Game Settings
FPS = 10
FOOD_MAX_NUM = 100
FOOD_MIN_NUM = 1
FOOD_NUM = FOOD_MIN_NUM
BOOST_MAX_NUM = 10
BOOST_MIN_NUM = 1
BOOST_NUM = BOOST_MIN_NUM
BOOST_SPAWN_MAX_PROB = 100
BOOST_SPAWN_MIN_PROB = 1
BOOST_SPAWN_PROB = BOOST_SPAWN_MIN_PROB

DEBUG = False

class Snake:
	COLOR = GREEN
	OUTLINE_COLOR = BLACK
	FLASH_COLOR = WHITE

	def __init__(self):
		self.size = 1
		self.positions = [((WINDOW_WIDTH // 2), (WINDOW_HEIGHT // 2))]
		self.direction = random.choice([pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT])
		self.is_flashing = False

	def get_head_position(self):
		return self.positions[0]

	## Change the direction of the snake if valid.
	def turn(self, point):
		if (point == pygame.K_UP and self.direction != pygame.K_DOWN) or \
			(point == pygame.K_DOWN and self.direction != pygame.K_UP) or \
			(point == pygame.K_LEFT and self.direction != pygame.K_RIGHT) or \
			(point == pygame.K_RIGHT and self.direction != pygame.K_LEFT):
			self.direction = point

	## Move the snake and check for collisions.
	def move(self):
		cur = self.get_head_position()
		x, y = cur
		if self.direction == pygame.K_UP:
			y -= BLOCK_SIZE
		elif self.direction == pygame.K_DOWN:
			y += BLOCK_SIZE
		elif self.direction == pygame.K_LEFT:
			x -= BLOCK_SIZE
		elif self.direction == pygame.K_RIGHT:
			x += BLOCK_SIZE
		new = (x, y)
		if new[0] < 0 or new[0] >= WINDOW_WIDTH or new[1] < 0 or new[1] >= WINDOW_HEIGHT or new in self.positions[2:]:
			return False
		else:
			self.positions.insert(0, new)
			if len(self.positions) > self.size:
				self.positions.pop()
			return True

	## Reset the snake to its initial state.
	def reset(self):
		self.size = 1
		self.positions = [((WINDOW_WIDTH // 2), (WINDOW_HEIGHT // 2))]
		self.direction = random.choice([pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT])
		self.is_flashing = False

	## Draw the snake on the surface.
	def draw(self, surface):
		for p in self.positions:
			rect = pygame.Rect((p[0], p[1]), (BLOCK_SIZE, BLOCK_SIZE))
			color = self.FLASH_COLOR if self.is_flashing and (pygame.time.get_ticks() // 100 % 2 == 0) else self.COLOR
			pygame.draw.rect(surface, color, rect)
			pygame.draw.rect(surface, self.OUTLINE_COLOR, rect, 1)

	## Handle key events to control the snake's direction.
	def handle_keys(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
			elif event.type == pygame.KEYDOWN:
				if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
					self.turn(event.key)
				elif event.key == pygame.K_w or event.key == pygame.K_UP:
					self.turn(pygame.K_UP)
				elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
					self.turn(pygame.K_DOWN)
				elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
					self.turn(pygame.K_LEFT)
				elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
					self.turn(pygame.K_RIGHT)
				elif DEBUG and event.key == pygame.K_SPACE:
					self.size += 1

class Food:
	COLOR = RED
	OUTLINE_COLOR = BLACK

	def __init__(self):
		self.position = (0, 0)
		self.spawn()

	## Spawn food at a random position.
	def spawn(self):
		x = random.randint(0, (WINDOW_WIDTH - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
		y = random.randint(0, (WINDOW_HEIGHT - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
		self.position = (x, y)

	## Draw the food on the surface.
	def draw(self, surface):
		rect = pygame.Rect((self.position[0], self.position[1]), (BLOCK_SIZE, BLOCK_SIZE))
		pygame.draw.rect(surface, self.COLOR, rect)
		pygame.draw.rect(surface, self.OUTLINE_COLOR, rect, 1)

class Boost:
	COLOR = YELLOW
	OUTLINE_COLOR = BLACK

	APPEAR_MAX_DURATION = 10 # Seconds
	MAX_DURATION = 3 # Seconds

	def __init__(self):
		self.position = (0, 0)

		self.appear = False
		self.appear_time = 0
		self.appear_duration = 0

		self.active = False
		self.time = 0
		self.duration = 0

	## Spawn boost at a random position.
	def spawn(self):
		x = random.randint(0, (WINDOW_WIDTH - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
		y = random.randint(0, (WINDOW_HEIGHT - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE

		self.position = (x, y)
		self.appear = True
		self.appear_time = pygame.time.get_ticks()
		self.appear_duration = random.randint(3000, self.APPEAR_MAX_DURATION * 1000)

	## Draw the boost on the surface if it is visible.
	def draw(self, surface):
		if self.appear:
			rect = pygame.Rect((self.position[0], self.position[1]), (BLOCK_SIZE, BLOCK_SIZE))
			pygame.draw.rect(surface, self.COLOR, rect)
			pygame.draw.rect(surface, self.OUTLINE_COLOR, rect, 1)

	## Update boost state based on elapsed time.
	def update(self):
		if self.appear and pygame.time.get_ticks() - self.appear_time > self.appear_duration:
			self.appear = False

		if self.active and pygame.time.get_ticks() - self.time > self.duration:
			self.active = False

	## Activate the boost.
	def enable(self):
		self.appear = False

		self.active = True
		self.time = pygame.time.get_ticks()
		self.duration = self.MAX_DURATION * 1000

class Game:
	def __init__(self, surface):
		self.surface = surface

		self.fps = FPS
		self.food_num = FOOD_NUM
		self.boost_num = BOOST_NUM
		self.boost_spawn_prob = BOOST_SPAWN_PROB

		self.snake = Snake()
		self.foods = [Food() for _ in range(self.food_num)]
		self.boosts = [Boost() for _ in range(self.boost_num)]

		self.state = STATE_WAIT
		self.score = 0

	## Reset the game state.
	def reset(self):
		self.snake.reset()
		for food in self.foods:
			food.spawn()
		for boost in self.boosts:
			boost.appear = False

class Slider:
	def __init__(self, x, y, width, min_value, max_value, initial_value, label, font_size = 20):
		self.x = x
		self.y = y
		self.width = width

		self.rect = pygame.Rect(x, y + 20, width, 20)

		self.min_value = min_value
		self.max_value = max_value
		self.value = initial_value

		self.label = label
		self.font_size = font_size

		self.dragging = False
		self.slider_width = 20
		self.handle_rect = pygame.Rect(self.get_handle_position(), y + 20, self.slider_width, 20)

		self.font = pygame.font.Font(pygame.font.get_default_font(), font_size)

	## Calculate the handle's position based on the slider's value.
	def get_handle_position(self):
		return self.rect.x + (self.value - self.min_value) / (self.max_value - self.min_value) * (self.rect.width - self.slider_width)

	## Draw the slider on the surface.
	def draw(self, surface, y):
		self.rect = pygame.Rect(self.x, y + 20, self.width, 20)
		self.handle_rect = pygame.Rect(self.get_handle_position(), y + 20, self.slider_width, 20)
		pygame.draw.rect(surface, WHITE, self.rect, 2)

		self.handle_rect.topleft = (self.get_handle_position(), self.rect.y)
		pygame.draw.rect(surface, GREEN, self.handle_rect)

		label_surface = self.font.render(self.label, True, WHITE)
		label_rect = label_surface.get_rect(midbottom = (self.rect.centerx, self.rect.top - 5))
		surface.blit(label_surface, label_rect)

		value_surface = self.font.render(f"{int(self.value)}", True, WHITE)
		value_rect = value_surface.get_rect(midleft = (self.rect.right + 10, self.rect.centery))
		surface.blit(value_surface, value_rect)

	## Update slider value based on mouse events.
	def update(self, event):
		if event.type == pygame.MOUSEBUTTONDOWN:
			if self.handle_rect.collidepoint(event.pos):
				self.dragging = True
		elif event.type == pygame.MOUSEBUTTONUP:
			if self.dragging:
				self.dragging = False
		elif event.type == pygame.MOUSEMOTION and self.dragging:
			mouse_x = event.pos[0]
			mouse_x = max(self.rect.x, min(mouse_x, self.rect.x + self.rect.width - self.slider_width))
			self.value = self.min_value + (mouse_x - self.rect.x) / (self.rect.width - self.slider_width) * (self.max_value - self.min_value)

## Draw centered text on the surface.
def draw_text(surface, text, size, color, center):
	font = pygame.font.Font(pygame.font.get_default_font(), size)
	text_surface = font.render(text, True, color)
	text_rect = text_surface.get_rect()
	text_rect.center = center
	surface.blit(text_surface, text_rect)

## Draw the score on the surface.
def draw_score(surface, score):
	draw_text(surface, f"Score: {score}", 30, WHITE, (70, 25))

def main():
	pygame.init()

	clock = pygame.time.Clock()
	screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), 0, 32)
	pygame.display.set_caption("Snake Game")
	surface = pygame.Surface(screen.get_size())
	surface = surface.convert()

	game = Game(surface)

	num_foods_slider = Slider((WINDOW_WIDTH - SLIDER_WIDTH) // 2, WINDOW_HEIGHT // 2, SLIDER_WIDTH, FOOD_MIN_NUM, FOOD_MAX_NUM, game.food_num, "Number of Foods")
	num_boosts_slider = Slider((WINDOW_WIDTH - SLIDER_WIDTH) // 2, WINDOW_HEIGHT // 2, SLIDER_WIDTH, BOOST_MIN_NUM, BOOST_MAX_NUM, game.boost_num, "Number of Boosts")
	num_boost_spawn_prob_slider = Slider((WINDOW_WIDTH - SLIDER_WIDTH) // 2, WINDOW_HEIGHT // 2, SLIDER_WIDTH, BOOST_SPAWN_MIN_PROB, BOOST_SPAWN_MAX_PROB, game.boost_spawn_prob, "Boost Appear Probability")

	while True:
		surface.fill(SURFACE_COLOR)

		if game.state == STATE_WAIT:

			## Draw texts
			draw_text(surface, "Snake Game", 50, GREEN, (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
			draw_text(surface, "Press 'ENTER' to Start or 'ESC' To Exit", 30, WHITE, (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 10))

			## Draw sliders
			num_foods_slider.draw(surface, WINDOW_HEIGHT // 2 + 50)
			num_boosts_slider.draw(surface, WINDOW_HEIGHT // 2 + 100)
			num_boost_spawn_prob_slider.draw(surface, WINDOW_HEIGHT // 2 + 150)

			for event in pygame.event.get():
				if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
					pygame.quit()
					sys.exit()

				elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
					game.foods = [Food() for _ in range(int(num_foods_slider.value))]
					game.boosts = [Boost() for _ in range(int(num_boosts_slider.value))]
					game.boost_spawn_prob = int(num_boost_spawn_prob_slider.value)

					game.reset()
					game.state = STATE_PLAY
 
				else:
					num_foods_slider.update(event)
					num_boosts_slider.update(event)
					num_boost_spawn_prob_slider.update(event)

		elif game.state == STATE_PLAY:

			clock.tick(game.fps + 15 if any(boost.active for boost in game.boosts) else game.fps)
			draw_score(surface, game.score)

			# Update Boost Spawn Time
			for boost in game.boosts:
				boost.update()
				if not boost.appear and not boost.active and random.randint(1, 100) <= game.boost_spawn_prob:
					boost.spawn()

			# Handle Snake Keys
			game.snake.handle_keys()
			if not game.snake.move():
				game.state = STATE_END

			# Check for Collisions with Food
			head_pos = game.snake.get_head_position()
			for food in game.foods:
				if head_pos == food.position:
					if any(boost.active for boost in game.boosts):
						game.snake.size += 2
						game.score += 2
					else:
						game.snake.size += 1
						game.score += 1
					food.spawn()

			# Check for Collisions with Boosts
			for boost in game.boosts:
				if head_pos == boost.position and boost.appear:
					boost.enable()

			# Update Snake Flashing
			if any(boost.active for boost in game.boosts):
				game.snake.is_flashing = True
			else:
				game.snake.is_flashing = False

			# Draw Everything
			game.snake.draw(surface)
			for food in game.foods:
				food.draw(surface)
			for boost in game.boosts:
				boost.draw(surface)

		elif game.state == STATE_END:

			# Draw texts
			draw_text(surface, "Game Over", 50, RED, (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
			draw_text(surface, f"Your Score: {game.score}", 30, YELLOW, (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 10))
			draw_text(surface, "Press 'ENTER' to Start or 'ESC' To Exit", 30, WHITE, (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 55))

			# Draw sliders
			num_foods_slider.draw(surface, WINDOW_HEIGHT // 2 + 100)
			num_boosts_slider.draw(surface, WINDOW_HEIGHT // 2 + 155)
			num_boost_spawn_prob_slider.draw(surface, WINDOW_HEIGHT // 2 + 205)

			for event in pygame.event.get():
				if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
					pygame.quit()
					sys.exit()

				elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
					game.foods = [Food() for _ in range(int(num_foods_slider.value))]
					game.boosts = [Boost() for _ in range(int(num_boosts_slider.value))]
					game.boost_spawn_prob = int(num_boost_spawn_prob_slider.value)

					game.reset()
					game.state = STATE_PLAY
 
				else:
					num_foods_slider.update(event)
					num_boosts_slider.update(event)
					num_boost_spawn_prob_slider.update(event)

		else:
			pygame.quit()

		screen.blit(surface, (0, 0))
		pygame.display.update()

if __name__ == "__main__":
	main()
