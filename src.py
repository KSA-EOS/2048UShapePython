import pygame
import pygame_menu
from pygame_menu.examples import create_example_window
from collections import deque
import time
import random
import math

pygame.init()

screenX, screenY = 1400, 700
PI = math.pi

pygame.display.set_caption("2048 Gravity mode")
window = pygame.display.set_mode((screenX, screenY))
clock = pygame.time.Clock()

sysfont = pygame.font.SysFont("arial", 40)

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
            'normal': '#dddddd',
            'hover': '#aaaaaa',
            'pressed': '#888888',
        }
        
        self.buttonSurface = pygame.Surface((self.width, self.height))
        self.buttonRect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        self.buttonSurf = sysfont = pygame.font.SysFont("arial", 40).render(buttonText, True, (20, 20, 20))
    
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
    global objects
    objects = []

def clickEvent():
    global gameStat, firstPlay
    if (gameStat == 0 and len(nameTxt) == 5):
        firstPlay = True
        gameStat = 1
        clearObj()
    elif gameStat != 0:
        firstPlay = True
        gameStat = 0
        clearObj()
    return 0

def dist(x1, y1, x2, y2):
    return ((x1-x2)**2+(y1-y2)**2)**0.5

####################################### Ranking ################################################

scoreList = []

def init(scoreList):
    #global scoreList
    L = len(scoreList)
    for i in range(L):
        scoreList.pop()
        
    f = open("data.txt", 'r', encoding="UTF-8")
    #저장방식: 이름, 결과치
    
    for line in f:
        name1, score1 = line.split()
        scoreList.append((name1, score1))
    
    temp = sorted(scoreList, key = lambda x : -int(x[1]))
    for i in range(len(scoreList)):
        scoreList[i] = temp[i]
    print("Initial complete")
    print("scoreboard:")
    for i in range(len(scoreList)):
        print(scoreList[i][0], scoreList[i][1])
    
    f.close()
    return

def writeNew(scoreList):
    #global scoreList
    f = open("data.txt", 'w+', encoding="UTF-8")
    for i in range(len(scoreList)):
        line = scoreList[i][0] + " " + str(scoreList[i][1]) + "\n"
        f.write(line)
    print("Rewrite Complete")
    f.close()
    return

def addNew(scoreList, name1, score1):
    #global scoreList
    scoreNames = list(map(lambda x: x[0], scoreList))
    if name1 in scoreNames:
        idx = scoreNames.index(name1)
        scoreList[idx] = (name1, str(max(score1, int(scoreList[idx][1]))))
    else:
        scoreList.append((name1, score1))
    print("New Element Added", scoreList)
    writeNew(scoreList)
    init(scoreList)
    return

f = open("data.txt", 'a+', encoding="UTF-8")
f.close()

init(scoreList)
print(scoreList)

############################### Important Variables ###########################################

window.fill((255, 255, 255))
pygame.display.flip()
balls = deque()

radius = screenY*0.3
g, multiple = 10, 10
multiples = [0.1]*1 + [0.5]*2 + [1] * 5 + [2] * 5 + [5] * 7 + [10] * 7 + [15] * 7 + [20] * 5 + [50] * 5 + [100]*2 + [1000] * 1

rdm = 0.5-random.random()
if rdm < 0:
    leftRight = -1
else:
    leftRight = 1
leftRight = -1
ballX, ballY, ballNumber = screenX/2+leftRight*radius, screenY*0.1, 2
plusAngle = math.atan(30/radius)
startBallY = 0
x, y = 0, 0
startTime, elapseIntTime = 0, 0
mergeRestTime = 0
score = 0
colors = [(255, 173, 173), (255, 214, 165), (253, 255, 182), (202, 255, 191), (155, 246, 255), (160, 196, 255), (189, 178, 255), (255, 198, 255), (230, 210, 210)]
collide = False

#items
sortItem, sortItemLeft = False, 3
visualizeItem, visualizeItemLeft = False, 3

playStage = 0 #0: Waiting, 1: Setting ball height, 2: dropping, 3: visual delay effect of 0.1s
color_value = 0

nameTxt = ""

################################## Game Functions ###############################################

def determineBallNumber():
    if len(balls) == 0:
        return 2
    ballNumbers = list(map(lambda x: x[2], balls))
    minBall = min(ballNumbers)
    maxBall = max(ballNumbers)
    range1, range2 = 0, 0
    if maxBall/minBall < 4:
        if maxBall >= 8:
            range1, range2 = maxBall//4, maxBall//2
        else:
            range1, range2 = 2, 8
    else:
        range1, range2 = minBall, minBall * 4
    s = random.randrange(1, 4)
    if s == 1:
        return range1
    elif s == 3:
        return range2
    else:
        return range1*2

def mergeBalls():
    global score
    
    print(balls)
    if len(balls)<2:
        return
    
    while len(balls) >= 2:
        changedLeft = False
        changedRight = False
        i = len(balls)//2
        while i > 0:
            if balls[i][2] == balls[i-1][2]:
                balls[i][2] *= 2
                score += balls[i][2]
                del balls[i-1]
                changedLeft = True
                print("merged:", i-1, i, balls)
                break
            i -= 1
        
        if len(balls) < 2:
            break
        
        i = len(balls)//2
        while i<len(balls)-1:
            if balls[i][2] == balls[i+1][2]:
                balls[i][2] *= 2
                score += balls[i][2]
                del balls[i+1]
                changedRight = True
                print("merged:", i, i+1, balls)
                break
            i += 1
        
        if not changedLeft and not changedRight:
            break
    
    print(balls)

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
        balls[len(L)//2][2] = L[-1]
        for i in range(len(L)//2):
            balls[i][2] = L[i*2]
            balls[len(L)-1-i][2] = L[i*2+1]
    
    mergeBalls()

def rainbow_color(value):
    step = (value // 64) % 6
    pos = value % 64

    if step == 0:
        return (255, pos, 0)
    if step == 1:
        return (255-pos, 255, 0)
    if step == 2:
        return (0, 255, pos)
    if step == 3:
        return (0, 255-pos, 255)
    if step == 4:
        return (pos, 0, 255)
    if step == 5:
        return (255, 0, 255-pos)

################################ Run #######################################

run = True
while run:
    clock.tick(100)
    
    ### Start ###
    
    if gameStat == 0:
        #window.fill( rainbow_color(color_value) )
        #color_value = (color_value + 1) % (256 * 6)
        window.fill((255, 255, 255))
        
        if firstPlay:
            firstPlay = False
            button = pyButton(screenX/2-50, screenY-100, 100, 50, 'Start', clickEvent)
            button.enableButton()
            nameTxt = ""
            balls = deque()
            score = 0
            sortItem, sortItemLeft = False, 3
            visualizeItem, visualizeItemLeft = False, 3            
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    nameTxt = nameTxt[:-1]
                elif event.key != pygame.K_RETURN:
                    nameTxt += event.unicode
                    print(nameTxt)
        
        try:
            meetingT = int(nameTxt)
        except:
            nameTxt = nameTxt[:-1]
        
        if len(nameTxt) > 5:
            nameTxt = nameTxt[:-1]
        
        nameText = pygame.font.SysFont("arial", 50).render("Your Number: " + nameTxt, True, (0, 0, 0))
        nameRect = nameText.get_rect()
        nameRect.centerx = screenX/2
        nameRect.centery = screenY*0.78
        window.blit(nameText, nameRect)
        
        for obj in objects:
            obj.process()
        
        ranking = pygame.font.SysFont("impact", 80).render("Gravity 2048!!", True, (0, 0, 0))
        rect = ranking.get_rect()
        rect.centerx = screenX/2
        rect.centery = screenY*0.1
        window.blit(ranking, rect)
        
        lm = min(5, len(scoreList))
        jds = ["st", "nd", "rd", "th", "th"]
        for i in range(lm):
            ranking = pygame.font.SysFont("comic sans", 35).render(str(i+1)+ jds[i] +": " + scoreList[i][0] + " - " + scoreList[i][1] + " points", True, (20, 20, 20))
            rect = ranking.get_rect()
            rect.centerx = screenX/2
            rect.centery = screenY*0.25+40*i
            window.blit(ranking, rect)
        
        info = pygame.font.SysFont("arial", 20).render("If you are KSA student, enter your student number (ex: 24-001 => 24001)", True, (0, 0, 0))
        rect = info.get_rect()
        rect.centerx = screenX/2
        rect.centery = screenY*0.58
        window.blit(info, rect)
        info = pygame.font.SysFont("arial", 20).render("If you are not a student, check the list and enter any 5-digit number STARTING WITH 8 which isn't there", True, (0, 0, 0))
        rect = info.get_rect()
        rect.centerx = screenX/2
        rect.centery = screenY*0.58 + 25
        window.blit(info, rect)
        info = pygame.font.SysFont("arial", 20).render("and write your name & number there. (ex: 80001)", True, (0, 0, 0))
        rect = info.get_rect()
        rect.centerx = screenX/2
        rect.centery = screenY*0.58 + 45
        window.blit(info, rect)
        info = pygame.font.SysFont("arial", 20).render("If you play this game again, the score will be saved as the max score you earned.", True, (0, 0, 0))
        rect = info.get_rect()
        rect.centerx = screenX/2
        rect.centery = screenY*0.58 + 70
        window.blit(info, rect)          
        
        pygame.display.flip()
    
    ### Game Window ###
    
    elif gameStat == 1:
        if firstPlay:
            firstPlay = False
            startTime = time.time()
        
        window.fill((255, 255, 255))
        
        multiplySurf = sysfont.render("g=10*"+str(multiple)+"px/s^3", True, (255, 255, 255))
        
        multiplySurface = pygame.Surface((300, 40))
        multiplyRect = pygame.Rect(0, 0, 300, 40)
        
        multiplySurface.blit(multiplySurf, [150-multiplySurf.get_rect().width/2, 20-multiplySurf.get_rect().height/2])
        window.blit(multiplySurface, multiplyRect)        
        
        pygame.draw.line(window, (0,0,0), [screenX/2-radius-33, screenY*0.20], [screenX/2-radius-33, screenY*0.60], 3)
        pygame.draw.line(window, (0,0,0), [screenX/2+radius+33, screenY*0.20], [screenX/2+radius+33, screenY*0.60], 3)
        pygame.draw.arc(window, (0,0,0), [screenX/2-radius-34, screenY*0.30-33, screenY*0.6+68, screenY*0.6+66], PI, PI*2, 3)
        
        pygame.draw.line(window, (0,0,0), [screenX/2-radius+33, screenY*0.20], [screenX/2-radius+33, screenY*0.60], 3)
        pygame.draw.line(window, (0,0,0), [screenX/2+radius-33, screenY*0.20], [screenX/2+radius-33, screenY*0.60], 3)
        pygame.draw.arc(window, (0,0,0), [screenX/2-radius+32, screenY*0.30+33, screenY*0.6-64, screenY*0.6-66], PI, PI*2, 3)
        
        sortSurf = pygame.font.SysFont("arial", 20).render("[S] Sort Item Left: "+str(sortItemLeft), True, (0,0,0))
        rect = sortSurf.get_rect()
        rect.centerx = screenX-rect.width/2-20
        rect.centery = 30
        window.blit(sortSurf, rect)
        
        sortSurf = pygame.font.SysFont("arial", 20).render("[V] Range Visuallize Item Left: "+str(visualizeItemLeft), True, (0,0,0))
        rect = sortSurf.get_rect()
        rect.centerx = screenX-rect.width/2-20
        rect.centery = 60
        window.blit(sortSurf, rect)        
        
        mainText = pygame.font.SysFont("arial", 45).render("Score: "+str(score), True, (30, 0, 0))
        mainRect = mainText.get_rect()
        mainRect.centerx = screenX/2
        mainRect.centery = screenY/2
        window.blit(mainText, mainRect)
        
        if visualizeItem:
            closestY = screenY*0.90
            if len(balls) > 0:
                closestY = balls[0][1]-60
            lastPivot = screenY*0.60
            pivotTime = 1
            while(1):
                herey = closestY-0.5*g*multiple*pivotTime**3
                if herey > lastPivot:
                    pivotTime += 1
                    continue
                
                pygame.draw.line(window, colors[(pivotTime-1)%9], [screenX/2+leftRight*(radius), max(herey, 0)], [screenX/2+leftRight*(radius), lastPivot], 10)
                lastPivot = herey
                pivotTime += 1
                
                if herey < 0:
                    break
        
        for ball in balls:
            pygame.draw.circle(window, colors[(int(math.log(ball[2], 2))-1)%9], (ball[0], ball[1]), 30)
            ballsText = sysfont.render(str(ball[2]), True, (0, 0, 0))
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
                elif event.type == pygame.KEYDOWN:
                    if (event.key == 83 or event.key == 115) and sortItemLeft > 0 and not sortItem:
                        sortItemLeft -= 1
                        sortItem = True
                        sortBalls()
                        print("sorted! and Merged!")
                    elif (event.key == 86 or event.key == 118) and visualizeItemLeft > 0 and not visualizeItem:
                        visualizeItemLeft -= 1
                        visualizeItem = True
        
        elif playStage == 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                elif event.type == pygame.MOUSEBUTTONUP:
                    playStage = 2
                    startTime, elapseIntTime = time.time(), 0
                    startBallY = ballY
            if len(balls) == 0:
                y = max(0, min(pygame.mouse.get_pos()[1], screenY*0.60))
            else:
                y = max(0, min(pygame.mouse.get_pos()[1], min(screenY*0.60, balls[-(leftRight+1)//2][1]-100)))
            ballY = y
            
            arrowH = screenY*0.60
            if len(balls) > 0:
                arrowH = min(screenY*0.60, balls[0][1]-40)
            pygame.draw.line(window, (255,200,200), [screenX/2+leftRight*(radius+100), 0], [screenX/2+leftRight*(radius+100), arrowH], 5)
            pygame.draw.line(window, (255,200,200), [screenX/2+leftRight*(radius+100), 0], [screenX/2+leftRight*(radius+100)-30, 30], 5)
            pygame.draw.line(window, (255,200,200), [screenX/2+leftRight*(radius+100), 0], [screenX/2+leftRight*(radius+100)+30, 30], 5)
            pygame.draw.line(window, (255,200,200), [screenX/2+leftRight*(radius+100), arrowH], [screenX/2+leftRight*(radius+100)-30, arrowH-30], 5)
            pygame.draw.line(window, (255,200,200), [screenX/2+leftRight*(radius+100), arrowH], [screenX/2+leftRight*(radius+100)+30, arrowH-30], 5)
            
        elif playStage == 2:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    
            if len(balls) == 0:
                if ballY < screenY*0.60:
                    ballY = int(startBallY + 0.5*g*multiple*(time.time()-startTime)**3)
                    if elapseIntTime < int(time.time()-startTime):
                        ballNumber *= 2
                        elapseIntTime = int(time.time()-startTime)
                elif ballY < screenY*0.90:
                    ballY = int(startBallY + 0.5*g*multiple*(time.time()-startTime)**3)
                    if elapseIntTime < int(time.time()-startTime):
                        ballNumber *= 2
                        elapseIntTime = int(time.time()-startTime)
                    
                    if ballY > screenY*0.90:
                        ballY = screenY*0.90
                    h = ballY - screenY*0.60
                    ballX = screenX/2+leftRight*((radius)**2-h**2)**0.5
                else:
                    startTime, elapseIntTime = time.time(), 0
                    collide = True
                    playStage = 3
            
            elif balls[-(leftRight+1)//2][1] > screenY*0.60:
                y = int(startBallY + 0.5*g*multiple*(time.time()-startTime)**3)
                if ballY < screenY*0.60 or radius <= y-screenY*0.60:
                    x = ballX
                    if elapseIntTime < int(time.time()-startTime):
                        ballNumber *= 2
                        elapseIntTime = int(time.time()-startTime)
                elif dist(ballX, ballY, balls[-(leftRight+1)//2][0], balls[-(leftRight+1)//2][1]) > 65:
                    if elapseIntTime < int(time.time()-startTime):
                        ballNumber *= 2
                        elapseIntTime = int(time.time()-startTime)
                    h = y - screenY*0.60
                    x = screenX/2+leftRight*(((radius)**2-h**2)**0.5)
                    
                if dist(x, y, balls[-(leftRight+1)//2][0], balls[-(leftRight+1)//2][1]) < 85:
                    angle = math.atan( abs(balls[-(leftRight+1)//2][0]-screenX/2) / (balls[-(leftRight+1)//2][1]-screenY*0.60))
                    angle += 2*plusAngle
                    ballX = screenX/2 + leftRight*radius*math.sin(angle)
                    ballY = screenY*0.60 + radius*math.cos(angle)
                    startTime, elapseIntTime = time.time(), 0
                    collide = True
                    playStage = 3
                else:
                    ballX = x
                    ballY = y
            
            else:
                if dist(ballX, ballY, balls[-(leftRight+1)//2][0], balls[-(leftRight+1)//2][1]) > 65:
                    ballY = int(startBallY + 0.5*g*multiple*(time.time()-startTime)**3)
                    if elapseIntTime < int(time.time()-startTime):
                        ballNumber *= 2
                        elapseIntTime = int(time.time()-startTime)
                else:
                    startTime, elapseIntTime = time.time(), 0
                    collide = True
                    playStage = 3
        
        elif playStage == 3:
            if time.time()-startTime > 0.1:
                playStage = 4
                if len(balls) == 0:
                    if leftRight == 1:
                        balls.append([ballX, ballY, ballNumber])
                    else:
                        balls.appendleft([ballX, ballY, ballNumber])                    
                    ballNumber = 2
                else:
                    if leftRight == 1:
                        balls.append([ballX, ballY, ballNumber])
                    else:
                        balls.appendleft([ballX, ballY, ballNumber])
                    ballNumber = determineBallNumber() 
                ballX = screenX/2+leftRight*radius
                ballY = screenY*0.1               
        else:
            if visualizeItem:
                visualizeItem = False
            if sortItem:
                sortItem = False
            
            rdm = 0.5-random.random()
            if rdm < 0:
                leftRight = -1
            else:
                leftRight = 1
            ballX = screenX/2 + leftRight*radius
            playStage = 0
            startTime = time.time()
            if random.random()>0.995:
                multiple = 0.01
            elif random.random() < 0.005:
                multiple = 822
            else:
                multiple = random.choice(multiples)
        
        while (len(balls) >=2) and (balls[-2][2] == balls[-1][2] or balls[0][2] == balls[1][2]):
            if len(balls) >= 2 and balls[-2][2] == balls[-1][2]:
                balls.pop()
                balls[-1][2] *=2
                score += balls[-1][2]
            if len(balls) >= 2 and balls[0][2] == balls[1][2]:
                balls.popleft()
                balls[0][2] *= 2
                score += balls[0][2]
        
        ### End Game ###
        if len(balls) >= 1 and (balls[-1][1] < screenY*0.20 or balls[0][1] < screenY*0.20):
            addNew(scoreList, nameTxt, score)
            firstPlay = True
            gameStat = 2
        
        ### New Equilibrium ###
        if len(balls) > 0:
            if len(balls)%2 == 1:
                k = len(balls)//2
                balls[k][0], balls[k][1] = screenX/2, screenY*0.90
                for i in range(k-1, -1, -1):
                    mulAngle = plusAngle * (k-i) * 2
                    if mulAngle > PI/2:
                        balls[i][0] = screenX/2 - radius
                        balls[i][1] = balls[i+1][1]-(3600-(balls[i][0]-balls[i+1][0])**2)**0.5
                    else:
                        balls[i][0] = screenX/2 - radius * math.sin(mulAngle)
                        balls[i][1] = screenY*0.60 + radius * math.cos(mulAngle)
                for i in range(k+1, len(balls)):
                    mulAngle = plusAngle * (i-k) * 2
                    if mulAngle > PI/2:
                        balls[i][0] = screenX/2 + radius
                        balls[i][1] = balls[i-1][1]-(3600-(balls[i][0]-balls[i-1][0])**2)**0.5
                    else:
                        balls[i][0] = screenX/2 + radius * math.sin(mulAngle)
                        balls[i][1] = screenY*0.60 + radius * math.cos(mulAngle)
            else:
                k = len(balls)//2
                balls[k-1][0], balls[k-1][1] = screenX/2 - radius*math.sin(plusAngle), screenY*0.60 + radius * math.cos(plusAngle)
                balls[k][0], balls[k][1] = screenX/2 + radius*math.sin(plusAngle), screenY*0.60 + radius * math.cos(plusAngle)
                for i in range(k-2, -1, -1):
                    mulAngle = plusAngle * ((k-1-i)*2 + 1)
                    if mulAngle > PI/2:
                        balls[i][0] = screenX/2 - radius
                        balls[i][1] = balls[i+1][1]-(3600-(balls[i][0]-balls[i+1][0])**2)**0.5
                    else:
                        balls[i][0] = screenX/2 - radius * math.sin(mulAngle)
                        balls[i][1] = screenY*0.60 + radius * math.cos(mulAngle)
                for i in range(k+1, len(balls)):
                    mulAngle = plusAngle * ((i-k) * 2 + 1)
                    if mulAngle > PI/2:
                        balls[i][0] = screenX/2 + radius
                        balls[i][1] = balls[i-1][1]-(3600-(balls[i][0]-balls[i-1][0])**2)**0.5
                    else:
                        balls[i][0] = screenX/2 + radius * math.sin(mulAngle)
                        balls[i][1] = screenY*0.60 + radius * math.cos(mulAngle)
        
        pygame.draw.circle(window, colors[(int(math.log(ballNumber, 2))-1)%9], (ballX, ballY), 30)
        
        ballText = sysfont.render(str(ballNumber), True, (0, 0, 0))
        ballTextRect = ballText.get_rect()
        
        ballTextRect.centerx = ballX
        ballTextRect.centery = ballY
        window.blit(ballText, ballTextRect)
        
        pygame.display.flip()
    
    ### Result Window ###
    
    else:
        if firstPlay:
            firstPlay = False
            button = pyButton(screenX/2-200, screenY*0.7, 400, 50, 'Go to First scene', clickEvent)
            button.enableButton()        
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                
        window.fill((255, 255, 255))
        
        mainText = sysfont.render("Game Over️", True, (255, 0, 0))
        mainRect = mainText.get_rect()
        mainRect.centerx = screenX/2
        mainRect.centery = screenY*0.3
        window.blit(mainText, mainRect)
        
        scoreText = sysfont.render("Score:" + str(score), True, (0, 0, 0))
        scoreRect = scoreText.get_rect()
        scoreRect.centerx = screenX/2
        scoreRect.centery = screenY*0.5
        window.blit(scoreText, scoreRect)
        
        for obj in objects:
            obj.process()        
        
        pygame.display.flip()

pygame.quit()