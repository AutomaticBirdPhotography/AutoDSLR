"""
Versjon: 3.7.1
            .3 - endret hastigheter ved følgning og align
          .7 - med LED
Dette er HOVEDVERSJONEN av programmet.
!KJØRES HVER GANG RPI STARTER!
!USIKRE ENDRINGER Må IKKE GJØRES!

Venter på kontroller:           fast blått
Når kontroller er koblet til:   fast grønt frem til første kommando sendes
Skrus kontrollert av:           fast rødt
Error:                          blinkende gult

"""

from vidgear.gears import NetGear
from vidgear.gears import CamGear
from vidgear.gears import PiGear
from gpiozero import LED
import numpy as np
import socket, imutils, cv2, threading, serial, time, os

RedLed = LED(18)
BlueLed = LED(19)
GreenLed = LED(20)

ser = serial.Serial("/dev/ttyUSB0", 115200, timeout=0.1)


dslr = CamGear(source=0).start()


options = {
    "rotation": 270
    }
cam = PiGear(resolution=(240,320), **options).start()

options = {
    "jpeg_compression_fastupsample": True,
    "jpeg_compression_quality": 75,
    }

dslrServer = NetGear("192.168.4.4", 2345, pattern = 0, **options)
camServer = NetGear("192.168.4.4", 1234, pattern = 0, **options)

HOST = '192.168.4.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen()
BlueLed.on()
print("Venter på at kontroller skal koble til")
conn, addr = s.accept()
BlueLed.off()
GreenLed.on()
GREEN = True
print("Kontroller koblet til")


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

scale_percent = 60 #prosent størrelse på tracker-videoen

def error_blink():
    for i in range(10):
        t_now = time.time()
        GreenLed.on()
        RedLed.on()
        while time.time()-1 < t_now:
            pass
        GreenLed.off()
        RedLed.off()
        while time.time()-0.2 < t_now+1:
            pass


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
    global bbox
    global degrees_per_pixel
    while True:
        try:
            buffer = conn.recv(32)
            print(buffer)
            
            if buffer == b's':
                break
            
            elif buffer.decode()[0] == 't':
                posList = midFrame
                track_init = True
                bbox = eval(buffer.decode()[1:])
                mouse_in = False
                to_mouse = False
                joy = False

            elif buffer == b'a':
                ser.write("a".encode())
                track_init = False
                mouse_in = False
                to_mouse = False
                joy = True
                i = 0
                start_time = time.time()
                while ser.read() != b'a' and time.time()-start_time < 10:
                    pass
                buffer = "0,0,0,0".encode()
                
            elif buffer == b'h':
                ser.write("h".encode())
                track_init = False
                mouse_in = False
                to_mouse = False
                joy = True
                i = 0
                start_time = time.time()
                while ser.read() != b'h' and time.time()-start_time < 10:
                    pass
                buffer = "0,0,0,0".encode()

            elif buffer.decode()[0] == 'j':
                track_init = False
                mouse_in = False
                to_mouse = False
                joy = True
                data_length = int(buffer.decode()[1:3])#verdi på hvor lang stingen er, tall send fra klienten
                mod_buffer = buffer.decode()[3:]
                buffer_length = len(mod_buffer) #hvor lang bufferen mottat faktisk er
                
                if data_length == buffer_length:
                    ser.write(mod_buffer.encode())
                    if GREEN:
                        GreenLed.off()
                else:
                    ser.write("0,0,0,0".encode())
                i = 0

            elif buffer.decode()[0] == 'm':
                if joy == False and track_init == False:
                    posList = eval(buffer.decode()[1:])
                    if to_mouse:
                        degrees_to_mouse(posList)
                    else:
                        mouse_in = False

            elif buffer.decode()[0] == 'p':
                posList = midFrame
                h_angle = float(buffer.decode()[1:])
                degrees_per_pixel = h_angle/dslrFrame.shape[1]
                joy = False
                mouse_in = True
                to_mouse = True
                i = 0
                
            elif buffer == b'b':
                ser.write("b".encode())
                
            elif buffer == b'f':
                ser.write("f".encode())

        except Exception as e:
            print("!!!!!!!!!!ERROR!!!!!!!!!!")
            print(e)
            error_blink()
            exit()
            
            
threading._start_new_thread(receive, ())

def map(x, in_min, in_max, out_min, out_max):
    return int((x-in_min) * (out_max-out_min) / (in_max-in_min) + out_min)

def drawBox(img, bbox):
    centerFrame = int(posList[0]), int(posList[1])
    x, y, w, h = int(bbox[0]*100/scale_percent), int(bbox[1]*100/scale_percent), int(bbox[2]*100/scale_percent), int(bbox[3]*100/scale_percent)
    centerRect = int(x+w/2), int(y+h/2)
    move(centerRect, centerFrame)

    cv2.rectangle(img, (x,y), ((x+w), (y+h)), (0, 255, 0), 3, 1)
    cv2.line(img, centerRect, centerFrame, (255, 0, 0), 4, cv2.LINE_AA)

def move(centerRect, centerFrame):
    hDiff = centerFrame[0]-centerRect[0] #centerFrame er 320, 240 vanligvis, går fra 0 ved midt til 320, men endres ved klikk fra server om ny senterposisjon
    vDiff = centerFrame[1]-centerRect[1]
    hSpeed = map(hDiff, (dslrFrame.shape[1]), (dslrFrame.shape[1]-dslrFrame.shape[1]*2), -20, 20) #fra 640 til 640-1280=-640 slik at den fortsatt har en verdi om centerFrame skulle være helt i kanten
    vSpeed = map(vDiff, (dslrFrame.shape[0]), (dslrFrame.shape[0]-dslrFrame.shape[0]*2), 20, -20) #fra 480 til -480
    ser.write("{},{},0,0".format(hSpeed, vSpeed).encode())
    
def degrees_to_mouse(posList):
    h_angle_to_mouse = degrees_per_pixel*(posList[0]-midFrame[0]) #0-320=-320 gir negativ verdi- går mot venstre 
    v_angle_to_mouse = degrees_per_pixel*(midFrame[1]-posList[1]) #240-0= 240 gir positiv verdi- går opp
    send = "p"+str(h_angle_to_mouse)+","+str(v_angle_to_mouse)
    if not send == "skip":
        ser.write(send.encode())
        start_time = time.time()
        while ser.read() != b'p' and time.time()-start_time < 10:
            pass
        buffer = "0,0,0,0".encode()
        send = "skip"
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
    global i, grab
    while grab:
        try:
            dslrFrame = dslr.read()
            camFrame = cam.read()
            if i == 1:
                dslrFrame_scaled = cv2.resize(dslrFrame, (int(dslrFrame.shape[1]*scale_percent/100), int(dslrFrame.shape[0]*scale_percent/100)), interpolation = cv2.INTER_AREA)
                success, bbox = tracker.update(dslrFrame_scaled)
                if success:
                    drawBox(dslrFrame, bbox)
                else:
                    ser.write("0,0,0,0".encode())
                    buffer = "0,0,0,0".encode()
                    cv2.putText(dslrFrame, "LOST",(75,75),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)
                    #i = 0
                    #joy = True
            camServer.send(camFrame)
            dslrServer.send(dslrFrame)
        except Exception as e:
            print("!!!!!!!!!!ERROR!!!!!!!!!!")
            print(e)
            error_blink()
            exit()

threading._start_new_thread(grab_frame, ())
    
while True:
    try:
        if buffer == b's': #må være her for å kunne bryte ut av while løkken
                ser.write("h".encode())
                grab = False
                time.sleep(5)
                break


        if track_init:
                bbox = (int(bbox[0]*scale_percent/100), int(bbox[1]*scale_percent/100),int(bbox[2]*scale_percent/100),int(bbox[3]*scale_percent/100))
                print(bbox)
                dslrFrame_scaled = cv2.resize(dslrFrame, (int(dslrFrame.shape[1]*scale_percent/100), int(dslrFrame.shape[0]*scale_percent/100)), interpolation = cv2.INTER_AREA)
                
                tracker = cv2.TrackerCSRT_create()
                ser.write("0,0,0,0".encode())
                tracker.init(dslrFrame_scaled, bbox)
                track_init = False
                i = 1
    except Exception as e:
            print("!!!!!!!!!!ERROR!!!!!!!!!!")
            print(e)
            error_blink()
            break
            
RedLed.on()
ser.write("0,0,0,0".encode())
grab = False
dslr.stop()
dslrServer.close()
cam.stop()
camServer.close()
s.close()
ser.close()
#time.sleep(10)
RedLed.off()
#os.system("sudo shutdown -h now") #skrur av rpi ved stoppkomando/break
