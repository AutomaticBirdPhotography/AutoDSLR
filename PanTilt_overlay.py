import cv2, math

cap = cv2.VideoCapture(0)
_, frame = cap.read()
capsize = 640,480
h_sensor = 23.5
focal_lenght = 500
h_angle = 2 * math.atan(float(h_sensor) / (2 * int(focal_lenght))) * (360 / (2 * math.pi))
degrees_per_pixel = 10/640

'''
(-180, 90)-----(0,90)-----(180,90)
|
|
|
(-180, 0)------(0,0)-------(180,90)
|
|
| 
(-180, -90)-----(0,-90)----(180,-90)
til piksler
-180/degrees_per_pixel
nåværende midpiksel: vertikal.currentposition()/16/degrees_per_pixel
vinkler vi ser vertikalt:  
'''
vSteps = 0
hSteps = 0


def put_line(x, y, x1, y1, hSteps, vSteps):
    vGrader = vSteps/16
    hGrader = hSteps/16
    x = int((x+640/2)-hGrader/degrees_per_pixel)         #få det slik at (0,0) er i midten av skjermen
    y = int((-y+480/2)+vGrader/degrees_per_pixel)
    x1 = int((x1+640/2)-hGrader/degrees_per_pixel)
    y1 = int((-y1+480/2)+vGrader/degrees_per_pixel)
    cv2.line(frame, (x,y), (x1, y1), (255,0,0), 4, cv2.LINE_AA)

def put_rectangle(x, y, x1, y1, hSteps, vSteps):
    vGrader = vSteps/16
    hGrader = hSteps/16
    x = int((x+640/2)-hGrader/degrees_per_pixel)         #få det slik at (0,0) er i midten av skjermen
    y = int((-y+480/2)+vGrader/degrees_per_pixel)
    x1 = int((x1+640/2)-hGrader/degrees_per_pixel)
    y1 = int((-y1+480/2)+vGrader/degrees_per_pixel)
    cv2.rectangle(frame, (x,y), (x1, y1), (255, 0, 0), 3, 1)
while True:
    _, frame = cap.read()
    cv2.line(frame,(320,0), (320,480), (0,255,0), 2)
    cv2.line(frame,(0,240), (640,240), (0,255,0), 2)
    put_line(0,100,75,150,hSteps,vSteps)
    put_line(150,100,75,150,hSteps,vSteps)
    put_rectangle(0,0,150,100,hSteps,vSteps)
    cv2.imshow("frame", frame)
    if cv2.waitKey(1) & 0xff == ord('w'):
        vSteps += 1
    if cv2.waitKey(1) & 0xff == ord('s'):
        vSteps -= 1
    if cv2.waitKey(1) & 0xff == ord('a'):
        hSteps -= 1
    if cv2.waitKey(1) & 0xff == ord('d'):
        hSteps += 1 
