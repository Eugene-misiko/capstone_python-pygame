import pygame
import os

WIN = pygame.display.set_mode((900,500))
pygame.display.set_caption("First Game")
FPS = 60
VEL = 5

PLAYER1 = pygame.image.load(os.path.join('assets', 'spaceship_yellow.png'))
PLAYER_1 = pygame.transform.rotate(pygame.transform.scale(PLAYER1, (55, 40)), 90)
PLAYER2 = pygame.image.load(os.path.join('assets', 'spaceship_red.png'))
PLAYER_2 = pygame.transform.rotate(pygame.transform.scale(PLAYER2, (55, 40)),270)

def draw_window(red, yellow):
    WIN.fill((255,255,255))
    WIN.blit(PLAYER_1, (yellow.x, yellow.y))
    WIN.blit(PLAYER_2,(red.x, red.y))
    pygame.display.update() 


def main():
    red = pygame.Rect(700, 300, 55, 40)
    yellow = pygame.Rect(100, 300, 55, 40)
    clock = pygame.time.Clock()
    run = True
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        
        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[pygame.K_a]:#key left
            yellow.x -= VEL
        if keys_pressed[pygame.K_d]:#key right
            yellow.x += VEL
          
                        
                
        draw_window(red, yellow)      

    pygame.quit()  

if __name__ == "__main__":
    main()            
