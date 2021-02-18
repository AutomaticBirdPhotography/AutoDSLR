'''
Videostreamen sendes til laptop 
laptop tracker og gjør alt. vSpeed og hSpeed sendes til rpi
'''
from vidgear.gears import NetGear
import cv2

client = NetGear("10.248.72.34", 8080, receive_mode = True)

while True:
    frame = client.recv()
    if frame is None:
        break

    cv2.imshow("Output Frame", frame)

    if cv2.waitKey(1) & 0xff == ord('q'):
        break


cv2.destroyAllWindows()
client.close()