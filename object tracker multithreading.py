from imutils.video import WebcamVideoStream
import cv2, serial, keyboard, imutils
import pygame
import numpy as np

wait = False

ser = serial.Serial("COM3", 115200)

cap = WebcamVideoStream(src=0).start()

tracker = cv2.TrackerCSRT_create()

img = cap.read()
img = imutils.resize(img, width=400)
img = cv2.flip(img, 1)

i = 0
number = 0

pygame.init()
screen = pygame.display.set_mode((400,400))
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()

def map(x, in_min, in_max, out_min, out_max):
    return int((x-in_min) * (out_max-out_min) / (in_max-in_min) + out_min)





def drawBox(img, bbox):
    centerFrame = int(posList[0]), int(posList[1])
    x, y, w, h = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
    centerRect = int(x+w/2), int(y+h/2)
    move(centerRect, centerFrame)
    crp = crop(img, x, y, w, h, img.shape[1], img.shape[0])

    dim = (w*2, h*2)
    resized = cv2.resize(crp, dim, interpolation = cv2.INTER_AREA)
    cv2.imshow("cropped", resized)

    cv2.rectangle(img, (x,y), ((x+w), (y+h)), (0, 255, 0), 3, 1)
    cv2.line(img, centerRect, centerFrame, (255, 0, 0), 4, cv2.LINE_AA)
    cv2.putText(img, "TRACKING",(75,75),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255,0),2)

def crop(img, x, y, w, h, iw, ih):
    if y < 0:
        y = 0
    if x < 0:
        x = 0
    crop = img[y:y+h, x:x+w]
    return crop

def move(centerRect, centerFrame):
    hDiff = centerFrame[0]-centerRect[0]
    vDiff = centerFrame[1]-centerRect[1]
    hSpeed = map(hDiff, (centerFrame[0]-0), (centerFrame[0]-centerFrame[0]*2), -750, 750)
    vSpeed = map(vDiff, (centerFrame[1]-0), (centerFrame[1]-centerFrame[1]*2), -750, 750)

    global i
    if (i >= 4):
        ser.write("{},{},".format(vSpeed, hSpeed).encode())
        #print(ser.readline().decode())
        print(vSpeed, hSpeed)
        i = 0

posList = int(img.shape[1]/2), int(img.shape[0]/2) 
def onMouse(event, x, y, flags, param):
    global posList
    if event == cv2.EVENT_LBUTTONDOWN:
        posList = (x, y)



def origin():
    return 

     
t = 0

while True:
#while cv2.getWindowProperty('Tracker', cv2.WND_PROP_VISIBLE) >= 1:
    while wait:
        pass


    if cv2.waitKey(1) & 0xff == ord('t') or joystick.get_button(3): #y
        wait = True
        tracker = cv2.TrackerCSRT_create()
        ser.write("{},{},".format(0, 0).encode())
        img = cap.read()
        img = imutils.resize(img, width=400)
        img = cv2.flip(img, 1)
        bbox = cv2.selectROI("Tracker", img, False, True)
        tracker.init(img, bbox)
        t = 1
        wait = False

    if keyboard.is_pressed('j') or joystick.get_button(5): #rb
        ser.write("{},{},".format(0, 0).encode())
        t = 0

    if t == 0:
        timer = cv2.getTickCount()
        img = cap.read()
        img = imutils.resize(img, width=400)
        img = cv2.flip(img, 1)
        cv2.imshow("Tracker", img)
        vSpeed = joystick.get_axis( 1 )*500
        hSpeed = joystick.get_axis( 0 )*-500

        ser.write("{:.0f},{:.0f}".format(vSpeed, hSpeed).encode())

    else:
        timer = cv2.getTickCount()
        img = cap.read()
        img = imutils.resize(img, width=400)
        img = cv2.flip(img, 1)
        success, bbox = tracker.update(img)

        if success:
            drawBox(img, bbox)
        else:
            ser.write("{},{},".format(0, 0).encode())
            cv2.putText(img, "LOST",(75,75),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)

        fps = cv2.getTickFrequency()/(cv2.getTickCount()-timer)
        cv2.putText(img, str(int(fps)),(75,50),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)
        cv2.imshow("Tracker", img)
        i += 1
        cv2.setMouseCallback("Tracker", onMouse)

    if keyboard.is_pressed('s') or joystick.get_button(1): #b
        ser.write("{},{},".format(0, 0).encode())
        break

    if keyboard.is_pressed('h') or joystick.get_button(4): #lb
        print("h")
        ser.write("h".encode())

    if keyboard.is_pressed('n') or joystick.get_button(2): #x
        print("n")
        ser.write("n".encode())


cap.release()
ser.write("{},{},".format(0, 0).encode())
ser.close()
pygame.quit()
cv2.destroyAllWindows()