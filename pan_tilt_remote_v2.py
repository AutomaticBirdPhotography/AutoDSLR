"""
!DETTE ER HOVEDVERSJONEN AV PROGRAMMET. BRUKES AV REMOTE-SHORTCUT!
versjon 1.6
"""

import PySimpleGUI as sg
import cv2, time, pygame, math, socket, threading
import numpy as np
from vidgear.gears import NetGear

'''
Notes:
Dataen sendes slik: 
s.send("{:.0f},{:.0f},{:.0f},{:.0f}".format(hSpeed, vSpeed, PanServo, TiltServo).encode())
'''

#-------------------------Starte ulike resurrser--------------------------------------------------

options = {
    "request_timeout": 10,
    "max_retries": 20,
}
dslrClient = NetGear("192.168.4.3", 2345, receive_mode=True, pattern = 0, **options)
camClient = NetGear("192.168.4.3", 1234, receive_mode=True, pattern = 0, **options)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect(("192.168.4.1", 65432))
except:
    print("PanTilt down")
    exit()
print("Connected to PanTilt")


pygame.init()
time.sleep(1)
joystick = pygame.joystick.Joystick(0)
joystick.init()
print("Loading...")
time.sleep(0.5)

#----------------Variabler------------------------------------------------------------------
dslrScale = 80 #%
camScale = 100
#halverer størrelsen på bildet, graphkordinatene må dobles | bildet ganges med scale/100, kordinatene deles med scale/100
#dobler størrelsen, halverer kordinatene
dslrFrameOrig = np.full((480, 640), 255, dtype='uint8') #dslrFrame = dslrClient.recv()
dslrFrame = cv2.resize(dslrFrameOrig, (int(dslrFrameOrig.shape[1]*(dslrScale/100)), int(dslrFrameOrig.shape[0]*(dslrScale/100))), interpolation = cv2.INTER_AREA)
camFrameOrig = np.full((640, 480), 255, dtype='uint8') #camFrame = camClient.recv()
camFrame = cv2.resize(camFrameOrig, (int(camFrameOrig.shape[1]*((camScale)/100)), int(camFrameOrig.shape[0]*(camScale/100))), interpolation = cv2.INTER_AREA)
dslrBytes = cv2.imencode('.png', dslrFrame)[1].tobytes()
camBytes = cv2.imencode('.png', camFrame)[1].tobytes()

h_sensor = 23.5
focal_lenght = 500
h_angle = 2 * math.atan(float(h_sensor) / (2 * int(focal_lenght))) * (360 / (2 * math.pi))
degrees_per_pixel = h_angle/dslrFrame.shape[1]


joy = True
tracking = False
a_id = None

dragging = False
start_point = end_point = prior_rect = None
update = False
point = False
stop = False
encode = True
old_event = '__TIMEOUT__'
joyInput = False
down = False

rect_x = 0
rect_y = 0
rect_width = 0
rect_height = 0
bbox = (0,0,0,0)

Old_hSpeed = 0
Old_vSpeed = 0
Old_PanServo = 0
Old_TiltServo = 0
first_value = True

#---------------------GUI-----------------------------------------------------------------
w, h = sg.Window.get_screen_size()
sg.theme('Black')
state_button = sg.Button('Stopp', size=(10, 1), font='Any 14', button_color=('white', 'red'))
track_button = sg.Button('Start følgning', size=(12, 1), font='Helvetica 14', button_color=('black', 'white'))
point_button = sg.Button('Start klikk', size=(10, 1), font='Helvetica 14', button_color=('black', 'white'))
joy_button = sg.Button('Stopp joy', size=(10, 1), font='Helvetica 14', button_color=('white', 'blue'))
align_button = sg.Button('Sentrér', size=(10, 1), font='Helvetica 14')
home_button = sg.Button('Hjem', size=(10, 1), font='Helvetica 14')
layout_column = [[sg.Text(f'Brennvidde: {focal_lenght}mm, {round(h_angle, 2)}', key='tekst', size=(22,1), font='Helvetica 12'), sg.Combo(['50','70','200','500','750'], default_value='500', key='brennvidde', font='Helvetica 14'), sg.Button('OK', font='Helvetica 12', bind_return_key=True)],
                [sg.Image(filename='', key='web'),
                sg.Image(filename='', key='dslr'), sg.Graph(canvas_size=(dslrFrame.shape[1], dslrFrame.shape[0]), graph_bottom_left=(0, dslrFrame.shape[0]), graph_top_right=(dslrFrame.shape[1], 0), key="-DSLR-", change_submits=True, background_color='lightblue', drag_submits=True),],
                [home_button, align_button, track_button, joy_button, point_button, state_button,],
                [sg.Text(key='info', size=(60, 1))]]

layout = [[sg.Column(layout_column, justification='center', element_justification='center')]]

window = sg.Window('En', layout, location=(0, 0), no_titlebar=True, size=(w, h)).Finalize()#sg.Window('En', layout, no_titlebar = True, keep_on_top = True, location=(0, 0), size=(w, h)).Finalize()
graph = window["-DSLR-"]


#-------------Funksjoner----------------------------
def update_focal():
    global h_angle
    inn = values['brennvidde']
    h_angle = 2 * math.atan(float(h_sensor) / (2 * int(inn))) * (360 / (2 * math.pi))
    #print(h_angle)
    window['tekst']. update("Brennvidde: " + values['brennvidde'] + f"mm, {round(h_angle, 2)}")

def roi(start_point, end_point):
    global rect_x, rect_y, rect_width, rect_height, bbox
    if start_point[0] <= end_point[0]:
        rect_x = start_point[0]
        rect_width = end_point[0]-start_point[0]
    else:
        rect_x = end_point[0]
        rect_width = start_point[0]-end_point[0]
    
    if start_point[1] <= end_point[1]:
        rect_y = start_point[1]
        rect_height = end_point[1]-start_point[1]
    else:
        rect_y = end_point[1]
        rect_height = start_point[1]-end_point[1]
    
    bbox = (int(rect_x/(dslrScale/100)), int(rect_y/(dslrScale/100)), int(rect_width/(dslrScale/100)), int(rect_height/(dslrScale/100)))

def encode_video():
    global dslrBytes, camBytes
    while encode:
        dslrFrameOrig = dslrClient.recv()
        dslrFrame = cv2.resize(dslrFrameOrig, (int(dslrFrameOrig.shape[1]*(dslrScale/100)), int(dslrFrameOrig.shape[0]*(dslrScale/100))), interpolation = cv2.INTER_AREA)
        cv2.rectangle(dslrFrame, (int(dslrFrame.shape[1]/2), int(dslrFrame.shape[0]/2)), (int(dslrFrame.shape[1]/2), int(dslrFrame.shape[0]/2)), (255,0,0), 7)
        camFrameOrig = camClient.recv()
        camFrame = cv2.resize(camFrameOrig, (int(camFrameOrig.shape[1]*((camScale)/100)), int(camFrameOrig.shape[0]*(camScale/100))), interpolation = cv2.INTER_AREA)
        cv2.rectangle(camFrame, (int(camFrame.shape[1]/2), int(camFrame.shape[0]/2)), (int(camFrame.shape[1]/2), int(camFrame.shape[0]/2)), (255,0,0), 7)
        dslrBytes = cv2.imencode('.ppm', dslrFrame)[1].tobytes()
        camBytes = cv2.imencode('.ppm', camFrame)[1].tobytes()
    cv2.destroyAllWindows()
        
threading._start_new_thread(encode_video, ())

def update_labels(button):
    if button == "joy":
        joy_button.update('Stopp joy')
        joy_button.update(button_color=('white', 'blue'))
        track_button.update('Start følgning')
        track_button.update(button_color=('black', 'white'))
        point_button.update('Start klikk')
        point_button.update(button_color=('black', 'white'))
    elif button == "track":
        joy_button.update('Start joy')
        joy_button.update(button_color=('black', 'white'))
        track_button.update('Stopp følgning')
        track_button.update(button_color=('white', 'blue'))
        point_button.update('Start klikk')
        point_button.update(button_color=('black', 'white'))
    elif button == "point":
        joy_button.update('Start joy')
        joy_button.update(button_color=('black', 'white'))
        track_button.update('Start følgning')
        track_button.update(button_color=('black', 'white'))
        point_button.update('Stopp klikk')
        point_button.update(button_color=('white', 'blue'))
    elif button == "stop":
        joy_button.update('Start joy')
        joy_button.update(button_color=('black', 'white'))
        track_button.update('Start følgning')
        track_button.update(button_color=('black', 'white'))
        point_button.update('Start klikk')
        point_button.update(button_color=('black', 'white'))

#--------------------Programmet----------------------------------
while True:
    try:
        start = time.time()
        for event in pygame.event.get():
            if event.type == pygame.JOYBUTTONDOWN:
                joyInput = True

        event, values = window.read(timeout=0)
        if a_id:
            graph.delete_figure(a_id)    #slett forige bilde
        a_id = graph.draw_image(data=dslrBytes, location=(0,0))  #lag nytt bilde
        graph.TKCanvas.tag_lower(a_id)   #setter bildet bakerst, tegninger kommer over

        window['web'].update(data=camBytes)
        
        if event != old_event or joyInput:  #unngå at to eventer skal være like rett etter hverandre og oppheve seg selv: stopp like etter stopp - stopper og starter umiddelbart

            if event == 'Stopp' or event == sg.WIN_CLOSED or joystick.get_button(8): #back
                break

            elif event == 'Sentrér' or joystick.get_button(1): #a
                s.send("a".encode())
                time.sleep(0.2)
                joy = True
            
            elif event == 'Hjem' or joystick.get_button(3): #y
                s.send("h".encode())
                time.sleep(0.2)
                joy = True
            
            elif event == 'Start følgning' or joystick.get_button(0): #x
                if tracking:
                    tracking = False
                    track_button.update('Start følgning')
                    track_button.update(button_color=('black', 'white'))
                else:
                    s.send("t".encode())
                    #select roi
                    info = window["info"]
                    info.update(value="Select ROI")

                    tracking = True
                    joy = False
                    point = False
                    update_labels("track")

            elif event == 'Stopp joy' or joystick.get_button(2): #B
                if joy:
                    joy = False
                    joy_button.update('Start joy')
                    joy_button.update(button_color=('black', 'white'))
                else:
                    joy = True
                    tracking = False
                    point = False
                    update_labels("joy")
                    s.send("j".encode())
                    time.sleep(0.2)
            
            elif event == 'Start klikk' or joystick.get_button(9): #start
                if point:
                    point = False
                    point_button.update('Start klikk')
                    point_button.update(button_color=('black', 'white'))
                else:
                    joy = False
                    tracking = False
                    point = True
                    update_labels("point")
                    s.send("p".encode())
                    time.sleep(0.2)
                    s.send("{}".format(h_angle).encode())

            elif event == 'OK':
                update_focal()

        if joy:
            vSpeed = joystick.get_axis(3)*-65
            hSpeed = joystick.get_axis(2)*65
            if hSpeed < 3 and hSpeed > -3:
                hSpeed = 0
            if vSpeed < 3 and vSpeed > -3:
                vSpeed = 0

            PanServo = joystick.get_axis(0)*8
            TiltServo = joystick.get_axis(1)*-8
            if (hSpeed != Old_hSpeed or vSpeed != Old_vSpeed or PanServo != Old_PanServo or TiltServo != Old_TiltServo):
                if first_value:
                    s.send("0,0,0,0".encode())
                    print("0,0,0,0")
                    first_value = False
                else:
                    s.send("{:.0f},{:.0f},{:.0f},{:.0f}".format(hSpeed, vSpeed, PanServo, TiltServo).encode())
                    print("{:.0f},{:.0f},{:.0f},{:.0f}".format(hSpeed, vSpeed, PanServo, TiltServo))
                    #time.sleep(0.5)
            Old_hSpeed = hSpeed
            Old_vSpeed = vSpeed
            Old_PanServo = PanServo
            Old_TiltServo = TiltServo

        if event == "-DSLR-":
            down = True
            if point or tracking:
                x, y = values["-DSLR-"]
                if not point:
                    if not dragging:
                        start_point = (x, y)
                        info = window["info"]
                        dragging = True
                    else:
                        if not x == start_point[0] and not y == start_point[1]:
                            end_point = (x, y)
                            roi(start_point, end_point)
                            update = True
                else:
                    start_point = (x, y)
                    end_point = (x, y)
                    rect = (0,0,0,0)
                    update = True
                if prior_rect:
                    graph.delete_figure(prior_rect)
                if None not in (start_point, end_point):
                    prior_rect = graph.draw_rectangle(start_point, end_point, line_color='red', line_width=5)

        elif event.endswith('+UP'):
            if down == True:
                if tracking:
                    tracking = False
                    track_button.update('Start følgning')
                    track_button.update(button_color=('black', 'white'))
                    time.sleep(0.7)
                    s.send("{}".format(str(bbox)).encode())
                    point = True
                    if prior_rect:
                        graph.delete_figure(prior_rect)
                elif point:
                    s.send("m".encode())
                    time.sleep(0.2)
                    s.send("{}, {}".format(int(start_point[0]/(dslrScale/100)), int(start_point[1]/(dslrScale/100))).encode())
                    if prior_rect:
                        graph.delete_figure(prior_rect)
                if update:
                    info = window["info"]
                    info.update(value=f"x: {bbox[0]}, y: {bbox[1]} width: {bbox[2]} height: {bbox[3]}")
            end_point = None #for å unngå at forrige bbox vises i millisekunder v/ ny
            down = False
            dragging = False
            update = False

        joyInput = False
        old_event = event   #unngå at to eventer skal være like rett etter hverandre og oppheve seg selv: stopp like etter stopp - stopper og starter umiddelbart
        end = time.time()
        #print(end-start)
    except Exception as e:
        print(e)
        break
window.close()
encode = False
s.send("s".encode())
pygame.quit()
time.sleep(1)
dslrClient.close()
camClient.close()
s.close()