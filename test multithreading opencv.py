from imutils.video import WebcamVideoStream
import imutils
import cv2

vs = WebcamVideoStream(src=0).start()

while True:
    frame = vs.read()
    frame = imutils.resize(frame, width=400)
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

cv2.destroyAllWindows()
vs.stop()