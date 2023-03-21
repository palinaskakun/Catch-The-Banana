import pygame
import random

pygame.init()


player = pygame.transform.scale(pygame.image.load('minion.png'), (150, 150))
banana = pygame.image.load('banana.png')
banana_inv = pygame.image.load('banana_facingright.png')
bananas = pygame.image.load('three_bananas.png')
bananas_inv = pygame.image.load('three_bananas_facing_right.png')
background=pygame.image.load("bg001.png")
music = pygame.mixer.music.load("min.mp3")
pygame.mixer.music.play(-1)

#smashed = pygame.transform.scale(pygame.image.load("smash.png"), (120, 120))
#smashies=[smashed]

screen_width = 1000
screen_height = 650

screen = pygame.display.set_mode([screen_width, screen_height])
pygame.display.set_caption("Catch The Banana")
fps_clock = pygame.time.Clock()

is_game_running = True
game_mode = "main_menu"
game_font = pygame.font.Font("GalacticaGrid.ttf", 30)
game_font2 = pygame.font.Font("yoster.ttf", 80)
start_button_rect = pygame.Rect(0, 0, 300, 100)
start_button_rect.center = [screen_width / 2, screen_height / 2]
start_button_color = [155,249,100]

y_pos = 0
is_game_running = True


enemies = []
last_enemy_time = 0
time_between_enemies = 200

x_pos=0
y_pos = screen_height
points = 0
lives=5
speed=4

while is_game_running:
    
    catches = [banana, banana_inv, bananas, bananas_inv]
    
    banana_time = random.randint(50, 200)
    
    if game_mode == "main_menu":
        screen.blit(background, (0,0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_game_running = False
            if event.type == pygame.KEYDOWN: 
                game_mode = "game"
                enemies = []
                last_enemy_time = 0
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if start_button_rect.collidepoint(mouse_x, mouse_y):
                    enemies = []
                    last_enemy_time = 0
                    game_mode = "game"
                    
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if start_button_rect.collidepoint(mouse_x, mouse_y):
            start_button_color = [155,249,100]
        else: 
            start_button_color = [255,222,0] 
        pygame.draw.rect(screen, start_button_color, start_button_rect)
        text = "Press to start"
        start_text = game_font.render(text, True, [0,0,0])
        screen.blit(start_text, [385, 315])
        
        text4="Use the mouse to control the minion. Don't drop bananas!"
        ttext4=pygame.font.Font("GalacticaGrid.ttf", 20).render(text4, True, [0,0,0])
        screen.blit(ttext4, [190, 200])
        
        name = "CATCH THE BANANA"
        name_text = game_font2.render(name, True, [0,0,0])
        screen.blit(name_text, [110, 100])
    
        if ((pygame.time.get_ticks() - last_enemy_time) >
                time_between_enemies):

            image = random.choice(catches) #pick random bananas
            image_catch = (pygame.Rect(random.randint(0, 900), 0, image.get_width(),
                image.get_height()), image)
            enemies.append(image_catch)
            last_enemy_time = pygame.time.get_ticks()

        for image_catch in enemies:
            image_catch[0].top = image_catch[0].top + 6
            screen.blit(image_catch[1], image_catch[0])
            

        pygame.display.flip()
        fps_clock.tick(30)
    
    if game_mode == "game":
        
        floor = pygame.Rect(0, 640, 1000, 5)
        pygame.draw.rect(screen, [0,0,0], floor)
        screen.blit(background, (0,0))
        
        #generates catches
        if ((pygame.time.get_ticks() - last_enemy_time) >
                time_between_enemies):
            catch_image = random.choice(catches)
            catch = (pygame.Rect(random.randint(0, 900), 0,
                                 catch_image.get_width(), catch_image.get_height()), catch_image)
            enemies.append(catch)
            last_enemy_time = pygame.time.get_ticks()

        for enemy in enemies:
            enemy[0].top = enemy[0].top + speed
            screen.blit(enemy[1], enemy[0])

        #controls part
        for event in pygame.event.get(): 
            if event.type == pygame.QUIT:
                print('quit')
                is_game_running = False
            if event.type == pygame.MOUSEMOTION:
                mouse_x, mouse_y = event.pos
                x_pos = mouse_x
              
              
        minion = pygame.Rect(mouse_x, mouse_y, player.get_height(), player.get_width())
        coord = []
        for catch in enemies:
            
            if minion.colliderect(catch[0]):
                points+=1
                enemies.remove(catch)
                
            if catch[0].colliderect(floor):
                
                lives-=1
                enemies.remove(catch)
            
            if lives==0:
                game_mode= "final_screen"
        
        text = "POINTS: " + str(points)
        points_surf = pygame.font.Font("yoster.ttf", 50).render(text, True, [0,0,0])
        screen.blit(points_surf, [100, 0])
        
        text1 = "LIVES: " + str(lives)
        text_lives= pygame.font.Font("yoster.ttf", 50).render(text1, True, [0,0,0])
        screen.blit(text_lives, [600, 0])
        
        if points>= 5 and points%5==0 and speed <=13:
            speed+=0.3
        
        pygame.display.flip()
        screen.blit(player, (mouse_x-player.get_width(), screen_height-150))
        pygame.display.update()

        fps_clock.tick(30)
        
    if game_mode == "final_screen":
        
        screen.blit(background, (0,0))
        lose = "YOU LOST."
        lose_text = pygame.font.Font("yoster.ttf", 150).render(lose, True, [0,0,0])
        screen.blit(lose_text, [100, 100])
        
        
        for event in pygame.event.get(): 
            if event.type == pygame.QUIT:
                print('quit')
                is_game_running = False
            if event.type == pygame.MOUSEMOTION:
                mouse_x, mouse_y = event.pos
                x_pos = mouse_x
            if event.type == pygame.KEYDOWN: 
                game_mode = "game"
                enemies = []
                last_enemy_time = 0
                speed=4
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if start_button_rect.collidepoint(mouse_x, mouse_y):
                    game_mode = "game"
                    enemies = []
                    last_enemy_time = 0
                    speed=4
        points =0
        lives=5
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if start_button_rect.collidepoint(mouse_x, mouse_y):
            start_button_color = [155,249,100]
        else: 
            start_button_color = [255,222,0] 
        pygame.draw.rect(screen, start_button_color, start_button_rect)
        text = "Press to start"
        start_text = game_font.render(text, True, [0,0,0])
        screen.blit(start_text, [370, 300])
        
        pygame.display.flip()


        fps_clock.tick(30)
        

        
