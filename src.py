import pygame
import pygame_menu
from pygame_menu.examples import create_example_window
from collections import deque
import time

pygame.init()

pygame.display.set_caption("2048 Gravity mode")
window = pygame.display.set_mode((1533, 840))
clock = pygame.time.Clock()

font = pygame.font.Font("C:/Users/cjhpr/OneDrive/바탕 화면/한과영/2023 SAF/사랑방정식/font/BinggraeSamanco.ttf", 70)

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
        
        self.buttonSurf = font.render(buttonText, True, (20, 20, 20))
    
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

def clearObj():
    objects = []

def clickEvent():
    global gameStat, firstPlay
    firstPlay = True
    gameStat = (gameStat+1)%3
    clearObj()
    return 0

window.fill((255, 255, 255))
pygame.display.flip()
balls = deque()

ballX, ballY, ballNumber = 800, 0, 2
g, multiple = 9.8, 10
startTime, elapseIntTime = 0, 0

run = True
while run:
    clock.tick(100)
    if gameStat == 0:
        if firstPlay:
            firstPlay = False
            button = pyButton(666, 650, 200, 100, 'Start', clickEvent)
            button.enableButton()
            
        for obj in objects:
            obj.process()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        
        pygame.display.flip()
    elif gameStat == 1:
        if firstPlay:
            firstPlay = False
            startTime = time.time()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        
        window.fill((255, 255, 255))
        
        ballY = 0.5*g*multiple*(time.time()-startTime)**3
        if elapseIntTime < int(time.time()-startTime):
            ballNumber *= 2
            elapseIntTime = int(time.time()-startTime)
        if ballY > 840:
            startTime = time.time()
            elapseIntTime = 0
            ballY = 0
        pygame.draw.circle(window, (255, 0, 0), (ballX, ballY), 30)
        
        ballText = font.render(str(ballNumber), True, (0, 0, 0))
        ballTextRect = ballText.get_rect()
        
        ballTextRect.centerx = ballX
        ballTextRect.centery = ballY
        
        window.blit(ballText, ballTextRect)
        
        pygame.display.flip()