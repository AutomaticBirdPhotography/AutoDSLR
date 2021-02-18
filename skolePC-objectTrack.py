import cv2
from vidgear.gears import VideoGear
from vidgear.gears import NetGear

waiting = False

cap = cv2.VideoCapture(0)

tracker = cv2.TrackerKCF_create()
success, org = cap.read()
img = cv2.flip(org, 1)
bbox = cv2.selectROI("Tracker", img, False, True)
tracker.init(img, bbox)

def map(x, in_min, in_max, out_min, out_max):
    return int((x-in_min) * (out_max-out_min) / (in_max-in_min) + out_min)

def drawBox(img, bbox):
    centerFrame = int(img.shape[1]/2), int(img.shape[0]/2)
    x, y, w, h = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
    centerRect = int(x+w/2), int(y+h/2)
    move(centerRect, centerFrame)

    cv2.rectangle(img, (x,y), ((x+w), (y+h)), (255, 0, 255), 3, 1)
    cv2.line(img, centerRect, centerFrame, (255, 0, 0), 3)
    cv2.putText(img, "TRACKING",(75,75),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255,0),2)

def move(centerRect, centerFrame):
    vDiff = centerFrame[0]-centerRect[0]
    hDiff = centerFrame[1]-centerRect[1]
    vSpeed = map(vDiff, (centerFrame[0]-0), (centerFrame[0]-centerFrame[0]*2), -100, 100)
    hSpeed = map(hDiff, (centerFrame[1]-0), (centerFrame[1]-centerFrame[1]*2), -100, 100)
    print(str(vSpeed) + "\t" + str(hSpeed))
    '''
    if centerRect[0] < centerFrame[0]:
        print("--->")

    elif centerRect[0] > centerFrame[0]:
        print("<---")

    if centerRect[1] < centerFrame[1]:
        print("|")
        print("|")
        print("v")

    elif centerRect[1] > centerFrame[1]:
        print("^")
        print("|")
        print("|")
    '''

while True:
    while waiting:
        pass
    timer = cv2.getTickCount()
    success, org = cap.read()
    img = cv2.flip(org, 1)

    success, bbox = tracker.update(img)
    if success:
        drawBox(img, bbox)
    else:
        cv2.putText(img, "LOST",(75,75),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)

    fps = cv2.getTickFrequency()/(cv2.getTickCount()-timer)
    cv2.putText(img, str(int(fps)),(75,50),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)
    cv2.imshow("Tracker", img)

    if cv2.waitKey(1) & 0xff == ord('t'):
        waiting = True
        tracker = cv2.TrackerKCF_create()
        success, org = cap.read()
        img = cv2.flip(org, 1)
        bbox = cv2.selectROI("Tracker", img, False, True)
        tracker.init(img, bbox)
        success, bbox = tracker.update(img)
        waiting = False
        
