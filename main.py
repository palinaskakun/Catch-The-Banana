import pygame
import random

# Initialize pygame
pygame.init()

# Screen setup
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Catch The Banana")
clock = pygame.time.Clock()
FPS = 60

# Colors
COLOR_BLACK = (0, 0, 0)
COLOR_GREEN = (155, 249, 100)
COLOR_YELLOW = (255, 222, 0)

# Fonts
FONT_SMALL = pygame.font.Font("GalacticaGrid.ttf", 20)
FONT_MAIN = pygame.font.Font("GalacticaGrid.ttf", 30)
FONT_LARGE = pygame.font.Font("yoster.ttf", 80)

# Assets
PLAYER_IMG = pygame.transform.scale(pygame.image.load('minion.png'), (150, 150))
BANANA_IMAGES = [
    pygame.image.load('banana.png'),
    pygame.image.load('banana_facingright.png'),
    pygame.image.load('three_bananas.png'),
    pygame.image.load('three_bananas_facing_right.png'),
]
BACKGROUND_MAIN = pygame.image.load("bg001.png")
BACKGROUND_IMAGES = [
    pygame.transform.scale(pygame.image.load('level1.jpg'), (SCREEN_WIDTH, SCREEN_HEIGHT)),
    pygame.transform.scale(pygame.image.load('level2.jpg'), (SCREEN_WIDTH, SCREEN_HEIGHT)),
    pygame.transform.scale(pygame.image.load('level3.jpg'), (SCREEN_WIDTH, SCREEN_HEIGHT)),
]
pygame.mixer.music.load("min.mp3")
pygame.mixer.music.play(-1)

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


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = PLAYER_IMG
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - self.rect.height)

    def update(self, mouse_x):
        self.rect.x = mouse_x - self.rect.width // 2
        self.rect.clamp_ip(pygame.Rect(0, SCREEN_HEIGHT - self.rect.height, SCREEN_WIDTH, self.rect.height))


# Functions
def draw_text(surface, text, font, color, x, y):
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, (x, y))


# Game Variables
game_mode = "main_menu"
current_level = 1
points = 0
lives = 2
speed = 2
last_enemy_time = 0
time_between_enemies = 400

player = Player()
enemies = pygame.sprite.Group()

# Main Game Loop
running = True
while running:
    screen.fill(COLOR_BLACK)
    mouse_x, mouse_y = pygame.mouse.get_pos()

    if game_mode == "main_menu":
        pygame.mouse.set_visible(True)
        screen.blit(BACKGROUND_MAIN, (0, 0))
        draw_text(screen, "CATCH THE BANANA", FONT_LARGE, COLOR_BLACK, 110, 100)
        draw_text(screen, "Use the mouse to control the minion. Don't drop bananas!", FONT_SMALL, COLOR_BLACK, 190, 200)
        start_button_color = COLOR_GREEN if pygame.Rect(350, 300, 300, 100).collidepoint(mouse_x, mouse_y) else COLOR_YELLOW
        pygame.draw.rect(screen, start_button_color, pygame.Rect(350, 300, 300, 100))
        draw_text(screen, "Press to start", FONT_MAIN, COLOR_BLACK, 385, 315)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.Rect(350, 300, 300, 100).collidepoint(mouse_x, mouse_y):
                    game_mode = "game"
                    current_level = 1
                    points, lives, speed = 0, 2, 2
                    enemies.empty()

    elif game_mode == "game":
        pygame.mouse.set_visible(False)
        screen.blit(BACKGROUND_IMAGES[current_level - 1], (0, 0))

        # Spawn enemies
        if pygame.time.get_ticks() - last_enemy_time > time_between_enemies:
            enemies.add(Enemy(random.choice(BANANA_IMAGES)))
            last_enemy_time = pygame.time.get_ticks()

        # Update
        player.update(mouse_x)
        enemies.update(speed)

        # Handle collisions
        for enemy in pygame.sprite.spritecollide(player, enemies, True):
            points += 1
        for enemy in enemies:
            if enemy.rect.bottom > SCREEN_HEIGHT:  # Check if the banana hits the floor
                lives -= 1
                enemy.kill()

        # Draw
        screen.blit(player.image, player.rect)
        enemies.draw(screen)
        draw_text(screen, f"POINTS: {points}", FONT_MAIN, COLOR_BLACK, 100, 10)
        draw_text(screen, f"LIVES: {lives}", FONT_MAIN, COLOR_BLACK, 800, 10)

        # Check for game over
        if lives <= 0:
            game_mode = "final_screen"

        # Check for level completion
        if points >= 20:
            if current_level < 3:
                game_mode = "level_complete"
            else:
                game_mode = "win_screen"

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    elif game_mode == "level_complete":
        pygame.mouse.set_visible(True)
        screen.blit(BACKGROUND_IMAGES[current_level - 1], (0, 0))
        draw_text(screen, f"Congrats on finishing Level {current_level}!", FONT_LARGE, COLOR_BLACK, 50, 200)
        draw_text(screen, "Are you ready to go to the next one?", FONT_MAIN, COLOR_BLACK, 200, 300)
        yes_button_color = COLOR_GREEN if pygame.Rect(350, 400, 300, 100).collidepoint(mouse_x, mouse_y) else COLOR_YELLOW
        pygame.draw.rect(screen, yes_button_color, pygame.Rect(350, 400, 300, 100))
        draw_text(screen, "YES", FONT_MAIN, COLOR_BLACK, 450, 430)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.Rect(350, 400, 300, 100).collidepoint(mouse_x, mouse_y):
                    current_level += 1
                    lives = 3
                    points = 0
                    game_mode = "game"

    elif game_mode == "win_screen":
        pygame.mouse.set_visible(True)
        screen.blit(BACKGROUND_IMAGES[2], (0, 0))
        draw_text(screen, "CONGRATULATIONS!", FONT_LARGE, COLOR_BLACK, 150, 200)
        draw_text(screen, "You completed all levels!", FONT_MAIN, COLOR_BLACK, 250, 400)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    elif game_mode == "final_screen":
        pygame.mouse.set_visible(True)
        screen.blit(BACKGROUND_MAIN, (0, 0))
        draw_text(screen, "YOU LOST.", FONT_LARGE, COLOR_BLACK, 100, 100)
        draw_text(screen, "Press any key to restart", FONT_MAIN, COLOR_BLACK, 250, 400)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                game_mode = "main_menu"

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()



#<a href="https://www.freepik.com/free-vector/green-alien-planet-with-craters-toxic-smoke_36102456.htm">Image by upklyak on Freepik</a>

#<a href="https://www.freepik.com/free-vector/empty-background-nature-scenery_5875466.htm">Image by brgfx on Freepik</a>

#<a href="https://www.freepik.com/free-vector/empty-nature-scenery_5288814.htm">Image by brgfx on Freepik</a>