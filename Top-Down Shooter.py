import pygame
import os
import random
import math
pygame.init()

Screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
fps = 60
clock = pygame.time.Clock()
pygame.display.set_caption("The Rithmatist Prototype Game")

game_running = True
current_location = "start_menu"
while game_running:
    clock.tick(60)
    
    for event in pygame.event.get():
    
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = False
    
        if event.type == pygame.QUIT:
            run = False
            
    Screen.fill((100, 100, 100))
    
    pygame.display.update()
    
    pygame.quit()