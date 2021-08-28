"""
Versjon: 1.5
            .3 - endret hastigheter ved følgning og align
Dette er HOVEDVERSJONEN av programmet.
!KJØRES HVER GANG RPI STARTER!
!USIKRE ENDRINGER Må IKKE GJØRES!
"""

from vidgear.gears import NetGear
from vidgear.gears import CamGear
from vidgear.gears import PiGear
import socket, imutils, cv2, threading, serial, time, os

import numpy as np
ser = serial.Serial("/dev/ttyUSB0", 115200)


dslr = CamGear(source=0).start()


options = {
    "rotation": 270
    }
cam = PiGear(resolution=(240,320), **options).start()

options = {
    "jpeg_compression_fastupsample": True,
    "jpeg_compression_quality": 75,
    }

dslrServer = NetGear("192.168.4.3", 2345, pattern = 0, **options)
camServer = NetGear("192.168.4.3", 1234, pattern = 0, **options)

HOST = '192.168.4.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen()
conn, addr = s.accept()


tracker = cv2.TrackerKCF_create()
grab = True
wait = False
track_init = False
mouse_in = False
to_mouse = False
angle_in = False
joy = True
i = 0
n = 0
p = 0
buffer = "".encode()
Old_buffer = "0,0,0,0".encode()
dslrFrame = dslr.read()
midFrame = int(dslrFrame.shape[1]/2), int(dslrFrame.shape[0]/2)
posList = midFrame

h_angle = 2.6924060829966665
degrees_per_pixel = h_angle/dslrFrame.shape[1] #horisontale grader per pikselbredde på dslrFrame


def receive():
    global buffer
    global track_init
    global mouse_in
    global to_mouse
    global angle_in
    global joy
    global i
    global p
    global posList
    while True:
        buffer = conn.recv(1024)
            
        if buffer == b't':
            posList = midFrame
            print("Track")
            track_init = True
            mouse_in = False
            to_mouse = False
            joy = False

        elif buffer == b'a':
            print("align")
            ser.write("a".encode())
            track_init = False
            mouse_in = False
            to_mouse = False
            joy = True
            i = 0
            
        elif buffer == b'h':
            print("home")
            ser.write("h".encode())
            track_init = False
            mouse_in = False
            to_mouse = False
            joy = True
            i = 0

        elif buffer == b'j':
            track_init = False
            mouse_in = False
            to_mouse = False
            joy = True
            ser.write("0,0,0,0".encode())
            i = 0

        elif buffer == b'm':
            print("M!!")
            if joy == False and track_init == False:
                track_init = False
                mouse_in = True
                angle_in = False

        elif buffer == b'p':
            posList = midFrame
            joy = False
            mouse_in = True
            to_mouse = True
            p = 1
            angle_in = True
            i = 0
            
        elif buffer == b'b':
            print("begynn")
            ser.write("b".encode())
            
        elif buffer == b'f':
            print("fokus begynn")
            ser.write("f".encode())
            
            
threading._start_new_thread(receive, ())

def map(x, in_min, in_max, out_min, out_max):
    return int((x-in_min) * (out_max-out_min) / (in_max-in_min) + out_min)

def drawBox(img, bbox):
    centerFrame = int(posList[0]), int(posList[1])
    x, y, w, h = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
    centerRect = int(x+w/2), int(y+h/2)
    move(centerRect, centerFrame)

    cv2.rectangle(img, (x,y), ((x+w), (y+h)), (0, 255, 0), 3, 1)
    cv2.line(img, centerRect, centerFrame, (255, 0, 0), 4, cv2.LINE_AA)
    cv2.putText(img, "TRACKING",(75,75),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255,0),2)

def move(centerRect, centerFrame):
    hDiff = centerFrame[0]-centerRect[0] #centerFrame er 320, 240 vanligvis, går fra 0 ved midt til 320, men endres ved klikk fra server om ny senterposisjon
    vDiff = centerFrame[1]-centerRect[1]
    print(dslrFrame.shape[1])
    hSpeed = map(hDiff, (dslrFrame.shape[1]), (dslrFrame.shape[1]-dslrFrame.shape[1]*2), -20, 20) #fra 640 til 640-1280=-640 slik at den fortsatt har en verdi om centerFrame skulle være helt i kanten
    vSpeed = map(vDiff, (dslrFrame.shape[0]), (dslrFrame.shape[0]-dslrFrame.shape[0]*2), 20, -20) #fra 480 til -480
    global n
    if (n >= 1): #endres etter hvor ofte bevegelsen skal oppdateres
        ser.write("{},{},0,0".format(hSpeed, vSpeed).encode())
        print("{},{},".format(hSpeed, vSpeed))
        n = 0
old_send = "p0,0"
def degrees_to_mouse(posList):
    global old_send
    #print(posList, midFrame)
    h_angle_to_mouse = degrees_per_pixel*(posList[0]-midFrame[0]) #0-320=-320 gir negativ verdi- går mot venstre 
    v_angle_to_mouse = degrees_per_pixel*(midFrame[1]-posList[1]) #240-0= 240 gir positiv verdi- går opp
    send = "p"+str(h_angle_to_mouse)+","+str(v_angle_to_mouse)
    if send != old_send:
        ser.write(send.encode())
        print(send)
    old_send = send
'''
data = "0,0".encode()
def send_steps():
    global data
    while True:
        data = ser.readline()
        conn.send(data)
threading._start_new_thread(send_steps, ())
'''
def grab_frame():
    global i, n, grab
    while grab:
        dslrFrame = dslr.read()
        camFrame = cam.read()
        if i == 1:
            success, bbox = tracker.update(dslrFrame)
            n += 1
            if success:
                drawBox(dslrFrame, bbox)
            else:
                ser.write("0,0,0,0".encode())
                buffer = "0,0,0,0".encode()
                cv2.putText(dslrFrame, "LOST",(75,75),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)
                i = 0
                #joy = True
        camServer.send(camFrame)
        dslrServer.send(dslrFrame)

threading._start_new_thread(grab_frame, ())
    
while True:
    
    if buffer == b's': #må være her for å kunne bryte ut av while løkken
            print("stop")
            ser.write("h".encode())
            time.sleep(5)
            break

    if to_mouse:
        if p == 1 and not buffer == b'p':
            h_angle = float(buffer.decode())
            degrees_per_pixel = h_angle/dslrFrame.shape[1]
            print(degrees_per_pixel)
            p = 0

    if mouse_in:
        if not buffer == b'm' and not buffer == b'p' and not buffer == b'h' and not buffer == b'a' and not buffer == b't' and not buffer == b's':
            if not angle_in:
                posList = eval(buffer.decode())
                if to_mouse:
                    degrees_to_mouse(posList)
                else:
                    mouse_in = False


    if track_init:
        print("init")
        print(buffer)
        if not buffer == b't':
            print("track")
            bbox = eval(buffer.decode())
            print(bbox)
            tracker = cv2.TrackerCSRT_create()
            ser.write("0,0,0,0".encode())
            tracker.init(dslrFrame, bbox)
            track_init = False
            i = 1
    if joy:
        if not buffer == b'j':
            if buffer != Old_buffer:
                ser.write(buffer)
                print(buffer)
            
            Old_buffer = buffer



ser.write("0,0,0,0".encode())
grab = False
dslr.stop()
dslrServer.close()
cam.stop()
camServer.close()
s.close()
ser.close()
#time.sleep(10)
#os.system("sudo shutdown -h now") #skrur av rpi ved stoppkomando/break