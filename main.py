import pygame
import random

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
FPS = 60
FONT_MAIN = pygame.font.Font("GalacticaGrid.ttf", 30)
FONT_LARGE = pygame.font.Font("yoster.ttf", 80)

# Colors
COLOR_BLACK = (0, 0, 0)
COLOR_GREEN = (155, 249, 100)
COLOR_YELLOW = (255, 222, 0)

# Assets
PLAYER_IMG = pygame.transform.scale(pygame.image.load('minion.png'), (150, 150))
BANANA_IMAGES = [
    pygame.image.load('banana.png'),
    pygame.image.load('banana_facingright.png'),
    pygame.image.load('three_bananas.png'),
    pygame.image.load('three_bananas_facing_right.png'),
]
BACKGROUND_IMG = pygame.image.load("bg001.png")
pygame.mixer.music.load("min.mp3")
pygame.mixer.music.play(-1)

# Screen setup
screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
pygame.display.set_caption("Catch The Banana")
clock = pygame.time.Clock()

# Classes
class Enemy(pygame.sprite.Sprite):
    def __init__(self, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = -self.rect.height

    def update(self, speed):
        self.rect.y += speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

# Game Functions
def draw_text(surface, text, font, color, x, y):
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, (x, y))

def handle_collision(player_rect, enemies_group, points, lives):
    for enemy in pygame.sprite.spritecollide(player_rect, enemies_group, True):
        points += 1
    return points, lives - sum(1 for enemy in enemies_group if enemy.rect.top > SCREEN_HEIGHT)

# Game Variables
game_mode = "main_menu"
player_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150]
points = 0
lives = 10
speed = 2
last_enemy_time = 0
time_between_enemies = 400

enemies = pygame.sprite.Group()

# Main Game Loop
running = True
while running:
    screen.blit(BACKGROUND_IMG, (0, 0))
    mouse_x, mouse_y = pygame.mouse.get_pos()
    player_rect = pygame.Rect(mouse_x, SCREEN_HEIGHT - 150, PLAYER_IMG.get_width(), PLAYER_IMG.get_height())

    if game_mode == "main_menu":
        # Draw UI
        draw_text(screen, "CATCH THE BANANA", FONT_LARGE, COLOR_BLACK, 110, 100)
        draw_text(screen, "Use the mouse to control the minion. Don't drop bananas!", FONT_MAIN, COLOR_BLACK, 190, 200)
        start_button_color = COLOR_GREEN if pygame.Rect(350, 300, 300, 100).collidepoint(mouse_x, mouse_y) else COLOR_YELLOW
        pygame.draw.rect(screen, start_button_color, pygame.Rect(350, 300, 300, 100))
        draw_text(screen, "Press to start", FONT_MAIN, COLOR_BLACK, 385, 315)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.Rect(350, 300, 300, 100).collidepoint(mouse_x, mouse_y):
                    game_mode = "game"
                    points, lives, speed = 0, 10, 2
                    enemies.empty()

    elif game_mode == "game":
        # Spawn enemies
        if pygame.time.get_ticks() - last_enemy_time > time_between_enemies:
            enemies.add(Enemy(random.choice(BANANA_IMAGES)))
            last_enemy_time = pygame.time.get_ticks()

        # Update and draw enemies
        enemies.update(speed)
        enemies.draw(screen)

        # Handle collisions
        points, lives = handle_collision(player_rect, enemies, points, lives)

        # Draw UI
        draw_text(screen, f"POINTS: {points}", FONT_MAIN, COLOR_BLACK, 100, 10)
        draw_text(screen, f"LIVES: {lives}", FONT_MAIN, COLOR_BLACK, 800, 10)
        screen.blit(PLAYER_IMG, (mouse_x - PLAYER_IMG.get_width() // 2, SCREEN_HEIGHT - 150))

        # Check for game over
        if lives <= 0:
            game_mode = "final_screen"

        # Increase speed
        if points % 5 == 0 and points > 0:
            speed = min(speed + 0.01, 13)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    elif game_mode == "final_screen":
        draw_text(screen, "YOU LOST.", FONT_LARGE, COLOR_BLACK, 250, 200)
        draw_text(screen, "Press any key to restart", FONT_MAIN, COLOR_BLACK, 300, 400)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                game_mode = "main_menu"

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
