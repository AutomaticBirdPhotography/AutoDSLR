import serial, time, pygame, socket, cv2
from vidgear.gears import NetGear

dslrClient = NetGear("192.168.4.13", 8080, receive_mode = True)
camClient = NetGear("192.168.4.13", 8081, receive_mode = True)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try: server.connect(("192.168.4.1", 65432))
except: print("raspberry down"); exit()
print("connected to raspberry")

pygame.init()
screen = pygame.display.set_mode((400, 400))

time.sleep(2)

joystick = pygame.joystick.Joystick(0)
joystick.init()

while True:
    dslrFrame = dslrClient.recv()
    scale_percent = 200 # percent of original size
    width = int(dslrFrame.shape[1] * scale_percent / 100)
    height = int(dslrFrame.shape[0] * scale_percent / 100)
    dim = (width, height)
    dslrFrame = cv2.resize(dslrFrame, dim, interpolation = cv2.INTER_AREA)
    cv2.imshow("Recieved video", dslrFrame)

    camFrame = camClient.recv()
    scale_percent = 200 # percent of original size
    width = int(camFrame.shape[1] * scale_percent / 100)
    height = int(camFrame.shape[0] * scale_percent / 100)
    dim = (width, height)
    camFrame = cv2.resize(camFrame, dim, interpolation = cv2.INTER_AREA)
    cv2.imshow("Recieved video", camFrame)

    if cv2.waitKey(1) & 0xff == ord('s'):
        break

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            server.send("h".encode())
            pygame.quit()
            capClient.close()
            server.close()
            cv2.destroyAllWindows()
            break

    vSpeed = joystick.get_axis( 1 )*500
    hSpeed = joystick.get_axis( 0 )*-500
    if hSpeed < 3 and hSpeed > -3:
        hSpeed = 0
    if vSpeed < 3 and vSpeed > -3:
        vSpeed = 0
    server.send("{:.0f},{:.0f},0,0".format(vSpeed, hSpeed).encode())

    PanServo = joystick.get_axis( 2 )*-15
    TiltServo= joystick.get_axis( 3 )*15
    ser.write("0,0,{:.2f},{:.2f}".format(PanServo, TiltServo).encode())
    time.sleep(0.1)


    
pygame.quit()
dslrClient.close()
camClient.close()
server.close()
cv2.destroyAllWindows()
