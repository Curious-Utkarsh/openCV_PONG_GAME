import cv2
print(cv2.__version__)
import numpy as np
import time
from random import choice

width=1280
height=720

rectW=25
rectH=150
rectColor=(0,255,255)

class mpHands:
    import mediapipe as mp
    def __init__(self,maxHands=2,tol1=.5,tol2=.5):
        self.handsDetect=self.mp.solutions.hands.Hands(False,maxHands,tol1,tol2)
        self.mpDraw=self.mp.solutions.drawing_utils
    def parseLandMarks(self,frame):
        myHands=[]
        handsType=[]
        frameRGB=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        results=self.handsDetect.process(frameRGB)
        if results.multi_hand_landmarks != 0:
            for hand in results.multi_handedness:
                handType=hand.classification[0].label
                handsType.append(handType)
            for handLandMarks in results.multi_hand_landmarks:
                self.mpDraw.draw_landmarks(x,handLandMarks,self.mp.solutions.hands.HAND_CONNECTIONS)
                myHand=[]
                for LandMark in handLandMarks.landmark:
                    myHand.append((int(LandMark.x*width),int(LandMark.y*height)))
                myHands.append(myHand)
        return myHands,handsType

cam=cv2.VideoCapture(0,cv2.CAP_DSHOW)
cam.set(cv2.CAP_PROP_FRAME_WIDTH,width)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT,height)
cam.set(cv2.CAP_PROP_FPS,120)
cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))

findHands=mpHands(2)

xPos=int(width/2)
yPos=int(height/2)
ballRadius=20
ballColor=(0,0,255)
deltaX=10
deltaY=10
livesA=5
livesB=5
scoreA=0
scoreB=0
radiusPointer=5
colorPointer=(255,0,0)

textFont=cv2.FONT_HERSHEY_SIMPLEX
textColor=(255,255,255)
textSize=4
textThickness=5
dt=3

while True:
    ignore,frame=cam.read()
    frame=cv2.flip(frame,1)
    x=np.zeros([height,width,3],dtype=np.uint8)
    x[:,:]=(0,0,0)
    myHands,handsType=findHands.parseLandMarks(frame)
    for oneHand,handType in zip(myHands,handsType):
        if(handType=='Left'):
            cv2.rectangle(x,(0,oneHand[5][1]-int(rectH/2)),(rectW,(oneHand[5][1]+int(rectH/2))),rectColor,-1)
        if(handType=='Right'):
            cv2.rectangle(x,((1280-rectW),oneHand[5][1]-int(rectH/2)),(1280,(oneHand[5][1]+int(rectH/2))),rectColor,-1)
        cv2.circle(x,oneHand[5],radiusPointer,colorPointer,-1)
        cv2.circle(x,(xPos,yPos),ballRadius,ballColor,-1)
        ballTopEdge=(yPos-ballRadius)
        ballBottomEdge=(yPos+ballRadius)
        ballLeftEdge=(xPos-ballRadius)
        ballRightEdge=(xPos+ballRadius)
        if(ballLeftEdge<=rectW and handType=='Left'):
            if((yPos>=(oneHand[5][1]-int(rectH/2))) and (yPos<=(oneHand[5][1]+int(rectH/2)))):
                value=choice([i for i in range(-1,2) if i not in [0]])
                deltaY=deltaY*(value)
                deltaX=deltaX*(-1)
                scoreA=scoreA+1
                if(scoreA%3==0):
                    livesA=livesA+1
                    deltaX=int(deltaX*1.2)
                    deltaY=int(deltaY*1.2)
            else:
                xPos=int(width/2)
                yPos=int(height/2)
                livesA=livesA-1
        if(ballRightEdge>=(1280-rectW) and handType=='Right'):
            if((yPos>=(oneHand[5][1]-int(rectH/2))) and (yPos<=(oneHand[5][1]+int(rectH/2)))):
                value=choice([i for i in range(-1,2) if i not in [0]])
                deltaY=deltaY*(value)
                deltaX=deltaX*(-1)
                scoreB=scoreB+1
                if(scoreB%3==0):
                    livesB=livesB+1
                    deltaX=int(deltaX*1.2)
                    deltaY=int(deltaY*1.2)
            else:
                xPos=int(width/2)
                yPos=int(height/2)
                livesB=livesB-1   
    if(ballTopEdge<=0 or ballBottomEdge>=height):
        deltaY=deltaY*(-1)
    xPos=xPos+deltaX
    yPos=yPos+deltaY
    if(livesA==0 or livesB==0):
        cv2.putText(x,'GAME OVER',(300,350),cv2.FONT_HERSHEY_COMPLEX,4,textColor,textThickness)
        cv2.putText(x,'SCORE A : '+str(scoreA),(300,450),textFont,2,textColor,textThickness)
        cv2.putText(x,'SCORE B : '+str(scoreB),(300,550),textFont,2,textColor,textThickness)
        if(scoreA>scoreB):
            cv2.putText(x,'Player A Won',(300,650),textFont,2,textColor,textThickness)
        elif(scoreA==scoreB):
            cv2.putText(x,'GAME TIE',(300,650),textFont,2,textColor,textThickness)
        else:
            cv2.putText(x,'Player B Won',(300,650),textFont,2,textColor,textThickness)
        deltaX=0
        deltaY=0
        ballRadius=0
        rectW=0
        rectH=0
    cv2.putText(x,str(scoreA),(30,120),textFont,textSize,textColor,textThickness)
    cv2.putText(x,str(scoreB),(1080,120),textFont,textSize,textColor,textThickness)
    cv2.putText(x,str(livesA),((int(width/2)-150),120),textFont,textSize,textColor,textThickness)
    cv2.putText(x,str(livesB),((int(width/2)+50),120),textFont,textSize,textColor,textThickness)
    cv2.putText(x,'A',((int(width/4)-100),680),textFont,2,textColor,textThickness)
    cv2.putText(x,'B',((1280-int(width/4)+100),680),textFont,2,textColor,textThickness)
    cv2.line(x,(int(width/2),0),(int(width/2),720),(0,255,0),1)
    cv2.line(x,(0,0),(0,720),(0,255,0),2)
    cv2.line(x,(1280,0),(1280,720),(0,255,0),2)
    cv2.line(x,(0,0),(1280,0),(0,255,0),5)
    cv2.line(x,(0,720),(1280,720),(0,255,0),3)
    if dt!=-2:
        cv2.putText(x,'GAME STARTS IN : '+str(dt)+' SEC',(185,350),cv2.FONT_HERSHEY_COMPLEX,2,textColor,textThickness)
        time.sleep(1)
        dt=dt-1
    cv2.imshow('PING PONG GAME',x)
    cv2.moveWindow('PING PONG GAME',0,0)
    if cv2.waitKey(1) & 0xff == ord('q'):
        break
cam.release()
cv2.destroyAllWindows()