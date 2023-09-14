import pygame
import pygame_menu
from pygame_menu.examples import create_example_window
from collections import deque

pygame.init()

pygame.display.set_caption("2048 Gravity mode")
window = pygame.display.set_mode((1533, 840))
clock = pygame.time.Clock()
gameStat = 0 #0: main, 1: play, 2: result
firstPlay = True

objects = []

class pyButton():
    def __init__(self, x, y, width, height, buttonText = 'Button', onclickFunction = None, onePress = False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.onclickFunction = onclickFunction
        self.onePress = onePress
        self.alreadyPressed = False
        
        self.fillColors = {
            'normal': '#ffbbbb',
            'hover': '#aa6666',
            'pressed': '#663333',
        }
        
        self.buttonSurface = pygame.Surface((self.width, self.height))
        self.buttonRect = pygame.Rect(self.x, self.y, self.width, self.height)
    
    def enableButton(self):
        objects.append(self)
    
    def process(self):
        mousePos = pygame.mouse.get_pos()
        self.buttonSurface.fill(self.fillColors['normal'])
        if self.buttonRect.collidepoint(mousePos):
            self.buttonSurface.fill(self.fillColors['hover'])
            if pygame.mouse.get_pressed(num_buttons=3)[0]:
                self.buttonSurface.fill(self.fillColors['pressed'])
                if self.onePress:
                    self.onclickFunction()
                elif not self.alreadyPressed:
                    self.onclickFunction()
                    self.alreadyPressed = True
            else:
                self.alreadyPressed = False
        self.buttonSurface.blit(self.buttonSurf, [self.buttonRect.width/2-self.buttonSurf.get_rect().width/2, self.buttonRect.height/2-self.buttonSurf.get_rect().height/2])
        window.blit(self.buttonSurface, self.buttonRect)

def clickEvent():
    global gameStat
    gameStat = (gameStat+1)%3
    return 0

window.fill((255, 255, 255))
pygame.display.flip()
balls = deque()

run = True
while run:
    clock.tick(100)
    if gameStat == 0:
        if firstPlay:
            button = pyButton(666, 650, 200, 100, 'Start', clickEvent)
            button.enableButton()
            
        for obj in objects:
            obj.process()        
    pygame.display.flip()