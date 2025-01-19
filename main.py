import pygame
import random
import os

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
COLOR_WHITE = (255, 255, 255)
COLOR_GREEN = (155, 249, 100)
COLOR_YELLOW = (255, 222, 0)

# Fonts
FONT_SMALL = pygame.font.Font(os.path.join("resources", "GalacticaGrid.ttf"), 20)
FONT_MAIN = pygame.font.Font(os.path.join("resources", "GalacticaGrid.ttf"), 30)
FONT_LARGE = pygame.font.Font(os.path.join("resources", "yoster.ttf"), 80)

# Assets
PLAYER_IMG = pygame.transform.scale(pygame.image.load(os.path.join("resources", "minion.png")), (150, 150))
BANANA_IMAGES = [
    pygame.image.load(os.path.join("resources", "banana.png")),
    pygame.image.load(os.path.join("resources", "banana_facingright.png")),
    pygame.image.load(os.path.join("resources", "three_bananas.png")),
    pygame.image.load(os.path.join("resources", "three_bananas_facing_right.png")),
]
SMASH_IMAGES = [
    pygame.transform.scale(pygame.image.load(os.path.join("resources", "smash.png")), (100, 100)),
    pygame.transform.scale(pygame.image.load(os.path.join("resources", "smashed.png")), (100, 100)),
]
BACKGROUND_MAIN = pygame.image.load(os.path.join("resources", "bg001.png"))
BACKGROUND_IMAGES = [
    pygame.transform.scale(pygame.image.load(os.path.join("resources", "level1.jpg")), (SCREEN_WIDTH, SCREEN_HEIGHT)),
    pygame.transform.scale(pygame.image.load(os.path.join("resources", "level2.jpg")), (SCREEN_WIDTH, SCREEN_HEIGHT)),
    pygame.transform.scale(pygame.image.load(os.path.join("resources", "level3.jpg")), (SCREEN_WIDTH, SCREEN_HEIGHT)),
]
pygame.mixer.music.load(os.path.join("resources", "min.mp3"))
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
def draw_text_centered(surface, text, font, color, center_x, center_y):
    """Draws text centered around the specified coordinates."""
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(center_x, center_y))
    surface.blit(text_surface, text_rect)


def draw_button(surface, text, font, button_color, center_x, center_y, width, height):
    """Draws a centered button with text."""
    button_rect = pygame.Rect(0, 0, width, height)
    button_rect.center = (center_x, center_y)
    pygame.draw.rect(surface, button_color, button_rect)
    draw_text_centered(surface, text, font, COLOR_BLACK, button_rect.centerx, button_rect.centery)
    return button_rect


# Game Variables
game_mode = "main_menu"
current_level = 1
points = 0
lives = 5
speed = 2
last_enemy_time = 0
time_between_enemies = 400
level_targets = [20, 50, 70]  # Points required for Levels 1, 2, 3
dropped_bananas = []  # Store locations of dropped bananas and their corresponding smash images

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
        draw_text_centered(screen, "CATCH THE BANANA", FONT_LARGE, COLOR_BLACK, SCREEN_WIDTH // 2, 100)
        draw_text_centered(screen, "Use the mouse to control the minion. Don't drop bananas!", FONT_SMALL, COLOR_BLACK, SCREEN_WIDTH // 2, 200)

        # Falling bananas for aesthetics
        if pygame.time.get_ticks() % 50 == 0 and len(enemies) < 5:
            enemies.add(Enemy(random.choice(BANANA_IMAGES)))
        enemies.update(1)
        enemies.draw(screen)

        start_button = draw_button(screen, "Press to start", FONT_MAIN, COLOR_GREEN if pygame.Rect(350, 300, 300, 100).collidepoint(mouse_x, mouse_y) else COLOR_YELLOW, SCREEN_WIDTH // 2, 300, 300, 100)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(mouse_x, mouse_y):
                    game_mode = "game"
                    current_level = 1
                    points, lives, speed = 0, 5, 2
                    enemies.empty()

    elif game_mode == "game":
        pygame.mouse.set_visible(False)
        bg_color = COLOR_WHITE if current_level == 2 else COLOR_BLACK
        screen.blit(BACKGROUND_IMAGES[current_level - 1], (0, 0))

        # Draw dropped bananas with smash images
        for smash_pos, smash_image in dropped_bananas:
            screen.blit(smash_image, smash_pos)

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
                smash_y = min(enemy.rect.y, SCREEN_HEIGHT - 100)  # Adjust Y to keep smash image within screen bounds
                dropped_bananas.append(((enemy.rect.x, smash_y), random.choice(SMASH_IMAGES)))
                enemy.kill()


        # Draw
        screen.blit(player.image, player.rect)
        enemies.draw(screen)
        draw_text_centered(screen, f"POINTS: {points}", FONT_MAIN, bg_color, SCREEN_WIDTH // 2, 20)
        draw_text_centered(screen, f"LIVES: {lives}", FONT_MAIN, bg_color, SCREEN_WIDTH - 150, 20)

        # Check for game over
        if lives <= 0:
            game_mode = "final_screen"

        # Check for level completion
        if points >= level_targets[current_level - 1]:
            if current_level < 3:
                game_mode = "level_complete"
            else:
                game_mode = "win_screen"

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    elif game_mode == "level_complete":
        pygame.mouse.set_visible(True)
        bg_color = COLOR_WHITE
        screen.blit(BACKGROUND_IMAGES[current_level - 1], (0, 0))
        draw_text_centered(screen, f"Congrats on finishing Level {current_level}!", FONT_MAIN, bg_color, SCREEN_WIDTH // 2, 200)
        draw_text_centered(screen, "Are you ready to go to the next one?", FONT_MAIN, bg_color, SCREEN_WIDTH // 2, 300)
        next_button = draw_button(screen, "YES", FONT_MAIN, COLOR_GREEN if pygame.Rect(350, 400, 300, 100).collidepoint(mouse_x, mouse_y) else COLOR_YELLOW, SCREEN_WIDTH // 2, 400, 300, 100)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if next_button.collidepoint(mouse_x, mouse_y):
                    current_level += 1
                    lives = 5
                    points = 0
                    dropped_bananas.clear()
                    enemies.empty()  # Clear all bananas before starting the next level
                    game_mode = "game"

    elif game_mode == "win_screen":
        pygame.mouse.set_visible(True)
        screen.blit(BACKGROUND_IMAGES[2], (0, 0))
        draw_text_centered(screen, "CONGRATULATIONS!", FONT_LARGE, COLOR_BLACK, SCREEN_WIDTH // 2, 200)
        draw_text_centered(screen, "You completed all levels!", FONT_MAIN, COLOR_BLACK, SCREEN_WIDTH // 2, 400)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    elif game_mode == "final_screen":
        pygame.mouse.set_visible(True)
        screen.blit(BACKGROUND_MAIN, (0, 0))
        draw_text_centered(screen, "YOU LOST.", FONT_LARGE, COLOR_BLACK, SCREEN_WIDTH // 2, 100)
        draw_text_centered(screen, "Press any key to restart", FONT_MAIN, COLOR_BLACK, SCREEN_WIDTH // 2, 400)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                game_mode = "main_menu"
                dropped_bananas.clear()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()




#<a href="https://www.freepik.com/free-vector/green-alien-planet-with-craters-toxic-smoke_36102456.htm">Image by upklyak on Freepik</a>

#<a href="https://www.freepik.com/free-vector/empty-background-nature-scenery_5875466.htm">Image by brgfx on Freepik</a>

#<a href="https://www.freepik.com/free-vector/empty-nature-scenery_5288814.htm">Image by brgfx on Freepik</a>