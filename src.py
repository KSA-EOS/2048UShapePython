import pygame
import pygame_menu
from pygame_menu.examples import create_example_window
from collections import deque
import time
import random
import math

pygame.init()

screenX, screenY = 1200, 700
PI = math.pi

pygame.display.set_caption("2048 Gravity mode")
window = pygame.display.set_mode((screenX, screenY))
clock = pygame.time.Clock()

font = pygame.font.Font("C:/Users/cjhpr/OneDrive/바탕 화면/한과영/2023 SAF/사랑방정식/font/BinggraeSamanco.ttf", 70)
sysfont = pygame.font.SysFont("arial", 30)

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
    
    def process (self):
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

def dist(x1, y1, x2, y2):
    return ((x1-x2)**2+(y1-y2)**2)**0.5

window.fill((255, 255, 255))
pygame.display.flip()
balls = deque()

radius = screenY*0.3
g, multiple = 9.8, 7

rdm = 0.5-random.random()
if rdm < 0:
    leftRight = -1
else:
    leftRight = 1
leftRight = -1
ballX, ballY, ballNumber = screenX/2+leftRight*radius, 0, 2
plusAngle = math.atan(30/radius)
startBallY = 0
x, y = 0, 0
startTime, elapseIntTime = 0, 0
score = 0

playStage = 0 #0: Waiting, 1: Setting ball height, 2: dropping, 3: finding equilibrium

def sortBalls():
    L = deque()
    for i in range(len(balls)):
        L.append(balls[i][2])
    L = sorted(L)
    if len(L)%2 == 0:
        for i in range(len(L)//2):
            balls[i][2] = L[i*2]
            balls[len(L)-1-i][2] = L[i*2+1]
    else:
        balls[len(L)//2][2] = L[0]
        for i in range(len(L)//2):
            balls[i][2] = L[i*2+1]
            balls[len(L)-1-i][2] = L[(i+1)*2]

run = True
while run:
    clock.tick(100)
            
    if gameStat == 0:
        if firstPlay:
            firstPlay = False
            button = pyButton(screenX/2-50, screenY-100, 100, 50, 'Start', clickEvent)
            button.enableButton()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            
        for obj in objects:
            obj.process()
        
        pygame.display.flip()
    
    elif gameStat == 1:
        if firstPlay:
            firstPlay = False
            startTime = time.time()
        
        window.fill((255, 255, 255))
        
        multiplySurf = sysfont.render(str(int(multiple)), True, (255, 255, 255))
        
        multiplySurface = pygame.Surface((100, 40))
        multiplyRect = pygame.Rect(0, 0, 100, 40)
        
        multiplySurface.blit(multiplySurf, [50-multiplySurf.get_rect().width/2, 20-multiplySurf.get_rect().height/2])
        window.blit(multiplySurface, multiplyRect)        
        
        pygame.draw.line(window, (0,0,0), [screenX/2-radius-33, screenY*0.25], [screenX/2-radius-33, screenY*0.65], 3)
        pygame.draw.line(window, (0,0,0), [screenX/2+radius+33, screenY*0.25], [screenX/2+radius+33, screenY*0.65], 3)
        pygame.draw.arc(window, (0,0,0), [screenX/2-radius-34, screenY*0.35-33, screenY*0.6+68, screenY*0.6+66], PI, PI*2, 3)
        
        pygame.draw.line(window, (0,0,0), [screenX/2-radius+33, screenY*0.25], [screenX/2-radius+33, screenY*0.65], 3)
        pygame.draw.line(window, (0,0,0), [screenX/2+radius-33, screenY*0.25], [screenX/2+radius-33, screenY*0.65], 3)
        pygame.draw.arc(window, (0,0,0), [screenX/2-radius+32, screenY*0.35+33, screenY*0.6-64, screenY*0.6-66], PI, PI*2, 3)
        
        for ball in balls:
            pygame.draw.circle(window, (255, 0, 0), (ball[0], ball[1]), 30)
            ballsText = font.render(str(ball[2]), True, (0, 0, 0))
            ballsTextRect = ballsText.get_rect()
            
            ballsTextRect.centerx = ball[0]
            ballsTextRect.centery = ball[1]
            window.blit(ballsText, ballsTextRect)
        
        if playStage == 0:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if dist(ballX, ballY, pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]) <= 30:
                        playStage = 1
            multiple = 15+10*math.sin(time.time()-startTime)
        
        elif playStage == 1:
            multiple = 15+10*math.sin(time.time()-startTime)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                elif event.type == pygame.MOUSEBUTTONUP:
                    playStage = 2
                    startTime, elapseIntTime = time.time(), 0
                    startBallY = ballY
            if len(balls) == 0:
                y = max(0, min(pygame.mouse.get_pos()[1], screenY*0.65))
            else:
                y = max(0, min(pygame.mouse.get_pos()[1], min(screenY*0.65, balls[-(leftRight+1)//2][1]-100)))
            ballY = y
        
        elif playStage == 2:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    
            if len(balls) == 0:
                if ballY < screenY*0.65:
                    ballY = int(startBallY + 0.5*g*multiple*(time.time()-startTime)**3)
                    if elapseIntTime < int(time.time()-startTime):
                        ballNumber *= 2
                        elapseIntTime = int(time.time()-startTime)
                elif ballY < screenY*0.95:
                    ballY = int(startBallY + 0.5*g*multiple*(time.time()-startTime)**3)
                    if elapseIntTime < int(time.time()-startTime):
                        ballNumber *= 2
                        elapseIntTime = int(time.time()-startTime)
                    
                    if ballY > screenY*0.95:
                        ballY = screenY*0.95
                    h = ballY - screenY*0.65
                    ballX = screenX/2+leftRight*((radius)**2-h**2)**0.5
                else:
                    if leftRight == 1:
                        balls.append([ballX, ballY, ballNumber])
                    else:
                        balls.appendleft([ballX, ballY, ballNumber])
                    ballX = screenX/2+leftRight*radius
                    ballY = screenY*0.1
                    ballNumber = 2
                    startTime, elapseIntTime = time.time(), 0
                    playStage = 3
            
            elif balls[-(leftRight+1)//2][1] > screenY*0.65:
                y = int(startBallY + 0.5*g*multiple*(time.time()-startTime)**3)
                if ballY < screenY*0.65 or radius <= y-screenY*0.65:
                    x = ballX
                    if elapseIntTime < int(time.time()-startTime):
                        ballNumber *= 2
                        elapseIntTime = int(time.time()-startTime)
                elif dist(ballX, ballY, balls[-(leftRight+1)//2][0], balls[-(leftRight+1)//2][1]) > 65:
                    if elapseIntTime < int(time.time()-startTime):
                        ballNumber *= 2
                        elapseIntTime = int(time.time()-startTime)
                    h = y - screenY*0.65
                    x = screenX/2+leftRight*(((radius)**2-h**2)**0.5)
                    
                if dist(x, y, balls[-(leftRight+1)//2][0], balls[-(leftRight+1)//2][1]) < 85:
                    angle = math.atan(abs(balls[-(leftRight+1)//2][0]-screenX/2)/(balls[-(leftRight+1)//2][1]-screenY*0.65))
                    angle += 2*plusAngle
                    ballX = screenX/2 + leftRight*radius*math.sin(angle)
                    ballY = screenY*0.65 + radius*math.cos(angle)
                    
                    if leftRight == 1:
                        balls.append([ballX, ballY, ballNumber])
                    else:
                        balls.appendleft([ballX, ballY, ballNumber])
                    ballX = screenX/2+leftRight*radius
                    ballY = screenY*0.1
                    ballNumber = 2
                    startTime, elapseIntTime = time.time(), 0
                    playStage = 3
                else:
                    ballX = x
                    ballY = y
                if ballY > 1000:
                    pygame.quit()
            
            else:
                if dist(ballX, ballY, balls[-(leftRight+1)//2][0], balls[-(leftRight+1)//2][1]) > 65:
                    ballY = int(startBallY + 0.5*g*multiple*(time.time()-startTime)**3)
                    if elapseIntTime < int(time.time()-startTime):
                        ballNumber *= 2
                        elapseIntTime = int(time.time()-startTime)
                else:
                    if leftRight == 1:
                        balls.append([ballX, balls[-(leftRight+1)//2][1]-60, ballNumber])
                    else:
                        balls.appendleft([ballX, balls[-(leftRight+1)//2][1]-60, ballNumber])
                    ballX = screenX/2+leftRight*radius
                    ballY = screenY*0.1
                    ballNumber = 2
                    startTime, elapseIntTime = time.time(), 0
                    playStage = 3
        
        else:
            rdm = 0.5-random.random()
            if rdm < 0:
                leftRight = -1
            else:
                leftRight = 1
            ballX = screenX/2 + leftRight*radius
            playStage = 0
            startTime = time.time()
        
        while (len(balls) >=2) and (balls[-2][2] == balls[-1][2] or balls[0][2] == balls[1][2]):
            if len(balls) >= 2 and balls[-2][2] == balls[-1][2]:
                balls.pop()
                balls[-1][2] *=2
                score += balls[-1][2]
            if len(balls) >= 2 and balls[0][2] == balls[1][2]:
                balls.popleft()
                balls[0][2] *= 2
                score += balls[0][2]
            
        if len(balls) >= 1 and (balls[-1][1] < screenY*0.25 or balls[0][1] < screenY*0.25):
            gameStat = 2
        
        if len(balls) > 0:
            if len(balls)%2 == 1:
                k = len(balls)//2
                balls[k][0], balls[k][1] = screenX/2, screenY*0.95
                for i in range(k-1, -1, -1):
                    mulAngle = plusAngle * (k-i) * 2
                    if mulAngle > PI/2:
                        balls[i][0] = screenX/2 - radius
                        balls[i][1] = balls[i+1][1]-(3600-(balls[i][0]-balls[i+1][0])**2)**0.5
                    else:
                        balls[i][0] = screenX/2 - radius * math.sin(mulAngle)
                        balls[i][1] = screenY*0.65 + radius * math.cos(mulAngle)
                for i in range(k+1, len(balls)):
                    mulAngle = plusAngle * (i-k) * 2
                    if mulAngle > PI/2:
                        balls[i][0] = screenX/2 + radius
                        balls[i][1] = balls[i-1][1]-(3600-(balls[i][0]-balls[i-1][0])**2)**0.5
                    else:
                        balls[i][0] = screenX/2 + radius * math.sin(mulAngle)
                        balls[i][1] = screenY*0.65 + radius * math.cos(mulAngle)
            else:
                k = len(balls)//2
                balls[k-1][0], balls[k-1][1] = screenX/2 - radius*math.sin(plusAngle), screenY*0.65 + radius * math.cos(plusAngle)
                balls[k][0], balls[k][1] = screenX/2 + radius*math.sin(plusAngle), screenY*0.65 + radius * math.cos(plusAngle)
                for i in range(k-2, -1, -1):
                    mulAngle = plusAngle * ((k-1-i)*2 + 1)
                    if mulAngle > PI/2:
                        balls[i][0] = screenX/2 - radius
                        balls[i][1] = balls[i+1][1]-(3600-(balls[i][0]-balls[i+1][0])**2)**0.5
                    else:
                        balls[i][0] = screenX/2 - radius * math.sin(mulAngle)
                        balls[i][1] = screenY*0.65 + radius * math.cos(mulAngle)
                for i in range(k+1, len(balls)):
                    mulAngle = plusAngle * ((i-k) * 2 + 1)
                    if mulAngle > PI/2:
                        balls[i][0] = screenX/2 + radius
                        balls[i][1] = balls[i-1][1]-(3600-(balls[i][0]-balls[i-1][0])**2)**0.5
                    else:
                        balls[i][0] = screenX/2 + radius * math.sin(mulAngle)
                        balls[i][1] = screenY*0.65 + radius * math.cos(mulAngle)
        
        pygame.draw.circle(window, (255, 0, 0), (ballX, ballY), 30)
        
        ballText = font.render(str(ballNumber), True, (0, 0, 0))
        ballTextRect = ballText.get_rect()
        
        ballTextRect.centerx = ballX
        ballTextRect.centery = ballY
        window.blit(ballText, ballTextRect)
        
        pygame.draw.circle(window, (0,0,0), (screenX/2, screenY*0.95), 3)
        
        pygame.display.flip()
    
    else:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                
        window.fill((255, 255, 255))
        
        mainText = font.render("Game Over️", True, (255, 0, 0))
        mainRect = mainText.get_rect()
        mainRect.centerx = screenX/2
        mainRect.centery = screenY/2
        window.blit(mainText, mainRect)
        
        scoreText = font.render("Score:" + str(score), True, (0, 0, 0))
        scoreRect = scoreText.get_rect()
        scoreRect.centerx = screenX/2
        scoreRect.centery = screenY*0.75
        window.blit(scoreText, scoreRect)
        
        pygame.display.flip()

pygame.quit()