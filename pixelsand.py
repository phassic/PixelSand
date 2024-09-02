import pygame
import random
import threading

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1200, 750
UI_HEIGHT = 150

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
WATER_COLOR = (64, 164, 223)
UI_COLOR = (200, 200, 200)
SLIDER_COLOR = (100, 100, 100)
KNOB_COLOR = (50, 50, 50)

# Magic Dust Types
MAGIC_DUST_TYPES = {
    "Star Dust": [(255, 215, 0), (255, 223, 186), (255, 182, 193)],  # Gold and pastel colors
    "Fairy Sparkles": [(75, 0, 130), (123, 104, 238), (216, 191, 216)],  # Purples and pinks
    "Rainbow Mist": [(255, 0, 255), (0, 255, 255), (255, 105, 180)]  # Vibrant neon colors
}

# Additional Sand Colors
ADDITIONAL_SAND_COLORS = [
    # Reds/Pinks/Magentas
    (255, 0, 50),     # Neon Red (Dynamic and bold)
    (255, 51, 0),     # Neon Coral (Energetic and bold)
    (255, 0, 150),    # Neon Pink (Striking and vibrant)
    (255, 40, 200),   # Hot Pink (Playful and fun)
    (255, 51, 153),   # Neon Rose (Vivid and romantic)
    (255, 0, 255),    # Neon Fuchsia (Intense and eye-catching)
    (255, 20, 255),   # Vibrant Magenta (Electric and exciting)
    (255, 80, 255),   # Fuchsia (Vibrant and eye-catching)

    # Oranges/Peaches/Golds
    (255, 90, 0),     # Neon Orange (Bold and lively)
    (255, 150, 0),    # Tangerine (Juicy and energetic)
    (255, 153, 51),   # Neon Peach (Soft yet vivid)
    (255, 180, 0),    # Vibrant Gold (Rich and warm)
    (255, 204, 0),    # Neon Amber (Warm and radiant)

    # Yellows/Limes
    (255, 240, 0),    # Neon Lemon (Bright and cheerful)
    (255, 255, 0),    # Bright Yellow (Sunny and joyful)
    (100, 255, 0),    # Lime Green (Fresh and lively)
    (0, 255, 64),     # Electric Lime (Bright and zesty)

    # Greens/Turquoises/Cyans
    (0, 255, 130),    # Electric Green (Bright and fresh)
    (0, 255, 180),    # Mint Green (Refreshing and cool)
    (0, 255, 240),    # Neon Turquoise (Bright and tropical)
    (0, 255, 255),    # Neon Cyan (Bright and electrifying)
    (0, 240, 255),    # Neon Aqua (Cool and energetic)
    (0, 200, 255),    # Sky Blue (Bright and expansive)

    # Blues/Indigos/Purples
    (0, 130, 255),    # Neon Blue (Bright and captivating)
    (0, 102, 255),    # Neon Royal Blue (Rich and intense)
    (120, 0, 255),    # Vibrant Indigo (Mystical and deep)
    (180, 30, 255),   # Deep Violet (Creative and bold)
    (240, 0, 255),    # Electric Purple (Vivid and striking)
    (255, 102, 204),  # Neon Lavender (Playful and bright)
    (255, 0, 255),    # Ultra Violet (Deep and vibrant)
]
# Initial settings
GRID_SIZE = 5

# Grid dimensions
cols, rows = WIDTH // GRID_SIZE, (HEIGHT - UI_HEIGHT) // GRID_SIZE

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Falling Sand Simulation with Magic Dust')

# Particle types
SAND = 1
WATER = 2
MAGIC_DUST = 3

# Initial gravity and wind settings
gravity_strength = 1
wind_strength = 0

# Current Magic Dust type
current_magic_dust = "Star Dust"
current_sand_color = pygame.Color(0)  # Start with default color
use_dynamic_rainbow_hue = True  # Start with dynamic rainbow hue active
hue = 0  # Initial hue value

# Slider class
class Slider:
    def __init__(self, x, y, width, min_value, max_value, initial_value, label):
        self.x = x
        self.y = y
        self.width = width
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value
        self.label = label
        self.knob_x = self.x + (self.width * (self.value - self.min_value) / (self.max_value - self.min_value))

    def draw(self, surface):
        # Draw line
        pygame.draw.line(surface, SLIDER_COLOR, (self.x, self.y), (self.x + self.width, self.y), 5)
        # Draw knob
        pygame.draw.circle(surface, KNOB_COLOR, (int(self.knob_x), self.y), 10)

        # Draw label
        font = pygame.font.SysFont(None, 24)
        label_surface = font.render(f'{self.label}: {self.value:.1f}', True, BLACK)
        surface.blit(label_surface, (self.x, self.y - 20))

    def update(self, mouse_x):
        if self.x <= mouse_x <= self.x + self.width:
            self.knob_x = mouse_x
            self.value = self.min_value + ((mouse_x - self.x) / self.width) * (self.max_value - self.min_value)

# Particle class
class Particle:
    def __init__(self, x, y, type, color, glued=False):
        self.x = x
        self.y = y
        self.type = type
        self.color = color
        self.glued = glued
        self.color_change_counter = 0
        self.fall_speed = 0.5

    def fall(self, grid):
        if self.glued:
            return  # Skip movement if this particle is glued

        # Gravity effect
        self.fall_speed += gravity_strength * 0.1  # Smooth gravity effect
        target_y = self.y + self.fall_speed

        if target_y >= rows:
            target_y = rows - 1

        if 0 <= target_y < rows:
            direction = 1 if gravity_strength > 0 else -1  # Determine direction based on gravity
            new_y = int(self.y + direction)

            # Check bounds before accessing the grid
            if 0 <= self.x < cols and 0 <= new_y < rows:
                # Randomly apply wind to sand and magic dust
                if self.type in {SAND, MAGIC_DUST} and random.random() < 0.05:
                    wind_direction = random.choice([-1, 1]) * int(wind_strength)
                    new_x = self.x + wind_direction
                    if 0 <= new_x < cols and grid[new_x][self.y] is None:
                        grid[new_x][self.y] = grid[self.x][self.y]
                        grid[self.x][self.y] = None
                        self.x = new_x

                # Water spreads more easily
                spread_chance = 0.2 if self.type == WATER else 0.05

                # Check in the gravity direction
                if grid[self.x][new_y] is None:
                    grid[self.x][new_y] = grid[self.x][self.y]
                    grid[self.x][self.y] = None
                    self.y = new_y
                else:
                    # For water, try to flow left or right
                    if self.type == WATER:
                        # Try to flow left
                        if self.x > 0 and grid[self.x - 1][self.y] is None:
                            grid[self.x - 1][self.y] = grid[self.x][self.y]
                            grid[self.x][self.y] = None
                            self.x -= 1
                        # Try to flow right
                        elif self.x < cols - 1 and grid[self.x + 1][self.y] is None:
                            grid[self.x + 1][self.y] = grid[self.x][self.y]
                            grid[self.x][self.y] = None
                            self.x += 1
                    # Check diagonally left
                    elif self.x > 0 and grid[self.x - 1][new_y] is None and random.random() < spread_chance:
                        grid[self.x - 1][new_y] = grid[self.x][self.y]
                        grid[self.x][self.y] = None
                        self.x -= 1
                        self.y = new_y
                    # Check diagonally right
                    elif self.x < cols - 1 and grid[self.x + 1][new_y] is None and random.random() < spread_chance:
                        grid[self.x + 1][new_y] = grid[self.x][self.y]
                        grid[self.x][self.y] = None
                        self.x += 1
                        self.y = new_y

        # Change color for Magic Dust
        if self.type == MAGIC_DUST:
            self.color_change_counter += 1
            if self.color_change_counter % 5 == 0:  # Change color every 5 ticks
                self.color = random.choice(MAGIC_DUST_TYPES[current_magic_dust])

# Initialize grid
def create_grid():
    return [[None for _ in range(rows)] for _ in range(cols)]

grid = create_grid()

# Create sliders
gravity_slider = Slider(50, HEIGHT - 50, 200, -10, 10, gravity_strength, "Gravity")
wind_slider = Slider(300, HEIGHT - 50, 200, 0, 10, wind_strength, "Wind")
grid_slider = Slider(550, HEIGHT - 50, 200, 2, 20, GRID_SIZE, "Grid Size")

# UI buttons
magic_dust_button = pygame.Rect(850, HEIGHT - 80, 100, 50)
sand_glue_button = pygame.Rect(1000, HEIGHT - 80, 100, 50)
magic_dust_active = False
glue_active = False

# Magic Dust Picker
magic_dust_picker = {
    "Star Dust": pygame.Rect(50, HEIGHT - 120, 100, 40),
    "Fairy Sparkles": pygame.Rect(200, HEIGHT - 120, 100, 40),
    "Rainbow Mist": pygame.Rect(350, HEIGHT - 120, 100, 40)
}

# Sand Color Picker including Dynamic Rainbow Hue
sand_color_picker = [(pygame.Color(0), pygame.Rect(50, HEIGHT - 140, 25, 15.45))]  # Dynamic Rainbow Hue option first
for i, color in enumerate(ADDITIONAL_SAND_COLORS):
    rect = pygame.Rect(90 + i * 40, HEIGHT - 140, 25, 15.45)
    sand_color_picker.append((color, rect))

# Thread to update particles
def update_particles(x_start, x_end):
    for x in range(x_start, x_end):
        for y in range(rows - 1, -1, -1):  # Iterate bottom to top
            particle = grid[x][y]
            if isinstance(particle, Particle):
                particle.fall(grid)

# Main loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if magic_dust_button.collidepoint(event.pos):
                magic_dust_active = not magic_dust_active
            elif sand_glue_button.collidepoint(event.pos):
                glue_active = not glue_active
            for dust_name, rect in magic_dust_picker.items():
                if rect.collidepoint(event.pos):
                    current_magic_dust = dust_name
            for i, (color, rect) in enumerate(sand_color_picker):
                if rect.collidepoint(event.pos):
                    if i == 0:  # If the first button (dynamic rainbow hue) is clicked
                        use_dynamic_rainbow_hue = True
                    else:
                        use_dynamic_rainbow_hue = False
                        current_sand_color = color

    # Handle mouse input
    mouse_buttons = pygame.mouse.get_pressed()
    mouse_x, mouse_y = pygame.mouse.get_pos()

    if mouse_buttons[0]:  # Left mouse button for particles
        grid_x, grid_y = mouse_x // GRID_SIZE, mouse_y // GRID_SIZE
        if 0 <= grid_y < rows:
            if grid_x < cols and grid[grid_x][grid_y] is None:
                if magic_dust_active:
                    grid[grid_x][grid_y] = Particle(grid_x, grid_y, MAGIC_DUST, random.choice(MAGIC_DUST_TYPES[current_magic_dust]), glued=glue_active)
                else:
                    if use_dynamic_rainbow_hue:
                        color = pygame.Color(0)
                        color.hsva = (hue % 360, 100, 100, 100)
                        hue += 1  # Increment hue for the next particle
                    else:
                        color = current_sand_color
                    grid[grid_x][grid_y] = Particle(grid_x, grid_y, SAND, color, glued=glue_active)

    if mouse_buttons[2]:  # Right mouse button for water
        grid_x, grid_y = mouse_x // GRID_SIZE, mouse_y // GRID_SIZE
        if 0 <= grid_y < rows and grid[grid_x][grid_y] is None:
            grid[grid_x][grid_y] = Particle(grid_x, grid_y, WATER, WATER_COLOR)

    # Update sliders if mouse is in UI area
    if mouse_y > HEIGHT - UI_HEIGHT:
        if mouse_buttons[0]:
            if 50 <= mouse_x <= 250 and HEIGHT - 60 <= mouse_y <= HEIGHT - 40:
                gravity_slider.update(mouse_x)
            if 300 <= mouse_x <= 500 and HEIGHT - 60 <= mouse_y <= HEIGHT - 40:
                wind_slider.update(mouse_x)
            if 550 <= mouse_x <= 750 and HEIGHT - 60 <= mouse_y <= HEIGHT - 40:
                grid_slider.update(mouse_x)

    # Update physics parameters from sliders
    gravity_strength = gravity_slider.value
    wind_strength = wind_slider.value
    new_grid_size = int(grid_slider.value)

    # Check if grid size has changed
    if new_grid_size != GRID_SIZE:
        GRID_SIZE = new_grid_size
        cols, rows = WIDTH // GRID_SIZE, (HEIGHT - UI_HEIGHT) // GRID_SIZE
        grid = create_grid()

    # Multithreaded particle updates
    num_threads = 4
    threads = []
    for i in range(num_threads):
        x_start = i * (cols // num_threads)
        x_end = (i + 1) * (cols // num_threads)
        thread = threading.Thread(target=update_particles, args=(x_start, x_end))
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    # Drawing
    screen.fill(BLACK)
    for x in range(cols):
        for y in range(rows):
            if isinstance(grid[x][y], Particle):
                pygame.draw.rect(screen, grid[x][y].color, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))

    # Draw UI
    pygame.draw.rect(screen, UI_COLOR, (0, HEIGHT - UI_HEIGHT, WIDTH, UI_HEIGHT))
    gravity_slider.draw(screen)
    wind_slider.draw(screen)
    grid_slider.draw(screen)

    # Draw Magic Dust button
    pygame.draw.rect(screen, (255, 215, 0) if magic_dust_active else (200, 200, 200), magic_dust_button)
    font = pygame.font.SysFont(None, 24)
    button_label = font.render("Magic Dust", True, BLACK)
    screen.blit(button_label, (magic_dust_button.x + 10, magic_dust_button.y + 15))

    # Draw Sand Glue button
    pygame.draw.rect(screen, (144, 238, 144) if glue_active else (200, 200, 200), sand_glue_button)
    glue_label = font.render("Sand Glue", True, BLACK)
    screen.blit(glue_label, (sand_glue_button.x + 10, sand_glue_button.y + 15))

    # Draw Magic Dust Picker
    for dust_name, rect in magic_dust_picker.items():
        pygame.draw.rect(screen, (255, 223, 186) if current_magic_dust == dust_name else (200, 200, 200), rect)
        dust_label = font.render(dust_name, True, BLACK)
        screen.blit(dust_label, (rect.x + 10, rect.y + 10))

    # Draw Sand Color Picker
    for i, (color, rect) in enumerate(sand_color_picker):
        pygame.draw.rect(screen, color, rect)
        if (use_dynamic_rainbow_hue and i == 0) or (color == current_sand_color and not use_dynamic_rainbow_hue):
            pygame.draw.rect(screen, WHITE, rect, 3)  # Highlight the selected color or dynamic rainbow hue option

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
