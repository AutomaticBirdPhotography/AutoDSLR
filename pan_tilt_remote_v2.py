"""
!DETTE ER HOVEDVERSJONEN AV PROGRAMMET. BRUKES AV REMOTE-SHORTCUT!
versjon 2.9.3
"""

import PySimpleGUI as sg
import cv2, time, pygame, math, socket, threading
import numpy as np
from vidgear.gears import NetGear

'''
Notes:
Dataen sendes slik: 
s.send("j{"lengden på bufferen"}{:.0f},{:.0f},{:.0f},{:.0f}".format(hSpeed, vSpeed, PanServo, TiltServo).encode())
'''

#-------------------------Starte ulike resurrser--------------------------------------------------
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
retries = 15

while s.connect_ex(("192.168.4.1", 65432)) != 0:
    print(f"Kunne ikke koble til! prøver {retries} ganger til")
    retries -= 1
    if retries <= 0:
        print("Klarte ikke etablere kontakt med PanTilt!")
        exit()
    time.sleep(5)
print("Koblet til PanTilt")

options = {
    "request_timeout": 10,
    "max_retries": 20,
}
dslrClient = NetGear("192.168.4.4", 2345, receive_mode=True, pattern = 0, **options)
camClient = NetGear("192.168.4.4", 1234, receive_mode=True, pattern = 0, **options)


pygame.init()
time.sleep(1)
joystick = pygame.joystick.Joystick(0)
joystick.init()
print("Laster...")
time.sleep(0.5)

#----------------Variabler------------------------------------------------------------------
dslrScale = 95
dslrScaleFull = 130
camScale = 145
#halverer størrelsen på bildet, graphkordinatene må dobles | bildet ganges med scale/100, kordinatene deles med scale/100
#dobler størrelsen, halverer kordinatene
dslrFrameOrig = np.full((480, 640), 255, dtype='uint8') #dslrFrame = dslrClient.recv()
dslrFrame = cv2.resize(dslrFrameOrig, (int(dslrFrameOrig.shape[1]*(dslrScale/100)), int(dslrFrameOrig.shape[0]*(dslrScale/100))), interpolation = cv2.INTER_AREA)
camFrameOrig = np.full((320, 240), 255, dtype='uint8') #camFrame = camClient.recv()
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
enable = False
view_dslr_layout = False

#---------------------GUI-----------------------------------------------------------------
w, h = sg.Window.get_screen_size()
sg.theme('Black')
state_button = sg.Button('X', size=(2, 3), font='Any 15', button_color=('white', 'red'))
track_button = sg.Button('Start følgning', size=(12, 3), font='Helvetica 15', button_color=('black', 'white'))
point_button = sg.Button('Start klikk', size=(10, 3), font='Helvetica 15', button_color=('black', 'white'))
joy_button = sg.Button('Stopp joy', size=(10, 3), font='Helvetica 15', button_color=('white', 'blue'))
align_button = sg.Button('+', size=(3, 3), font='Helvetica 15')
home_button = sg.Button('Hjem', size=(10, 3), font='Helvetica 15')
focal_button = sg.Button('F', size=(3, 3), font='Helvetica 15')
enable_button = sg.Button('OFF', size=(4, 3), font='Helvetica 15', button_color=('white', 'red'))
layout_column = [[sg.Image(filename='', key='web'),
                sg.Image(filename='', key='dslr'), sg.Graph(canvas_size=(dslrFrame.shape[1], dslrFrame.shape[0]), graph_bottom_left=(0, dslrFrame.shape[0]), graph_top_right=(dslrFrame.shape[1], 0), key="-DSLR-", change_submits=True, background_color='lightblue', drag_submits=True),],
                [focal_button, home_button, align_button, track_button, joy_button, point_button, enable_button, state_button]]
layout_dslr = [[sg.Image(filename='', key='dslr_full'), sg.Button('Ut', size=(6,2), font='Helvetica 15', button_color=('white', 'red'))]]

layout_focal_input = [[sg.Text(size=(1,20))],[sg.Text(f'Brennvidde: {focal_lenght}mm, {round(h_angle, 2)}', key='tekst', size=(22,1), font='Helvetica 28'), sg.Combo(['50','70','200','500','750'], default_value='500', key='brennvidde', font='Helvetica 35'), sg.Button('OK', font='Helvetica 28', bind_return_key=True)]]

layout = [[sg.Column(layout_column, justification='center', element_justification='center', key='BASE'), sg.Column(layout_dslr, justification='center', element_justification='center', key='FULL_DSLR', visible=False), sg.Column(layout_focal_input, justification='center', element_justification='center', key='FOCAL_INPUT', visible=False)]]

window = sg.Window('En', layout, no_titlebar = True, location=(0, 0), size=(w, h)).Finalize()#sg.Window('En', layout, no_titlebar = True, keep_on_top = True, location=(0, 0), size=(w, h)).Finalize()
graph = window["-DSLR-"]
window.TKroot["cursor"] = "none"


#-------------Funksjoner----------------------------
def speed(x):
    offset = 20 #dødgang på joy
    if x > offset:
        return 1.25*x-25
    elif x < -offset:
        return 1.25*x+25
    else:
        return 0
        

def update_focal():
    global h_angle
    inn = values['brennvidde']
    h_angle = 2 * math.atan(float(h_sensor) / (2 * int(inn))) * (360 / (2 * math.pi))
    h_angle = round(h_angle, 2)
    window['tekst']. update("Brennvidde: " + values['brennvidde'] + f"mm, {h_angle}")

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
    global dslrBytes, camBytes, view_dslr_layout
    while encode:
        try:
            dslrFrameOrig = dslrClient.recv()
            if len(dslrFrameOrig) > 0:
                if view_dslr_layout:
                    dslrFrame = cv2.resize(dslrFrameOrig, (int(dslrFrameOrig.shape[1]*(dslrScaleFull/100)), int(dslrFrameOrig.shape[0]*(dslrScaleFull/100))), interpolation = cv2.INTER_AREA)
                    dslrBytes = cv2.imencode('.ppm', dslrFrame)[1].tobytes()
                else:
                    dslrFrame = cv2.resize(dslrFrameOrig, (int(dslrFrameOrig.shape[1]*(dslrScale/100)), int(dslrFrameOrig.shape[0]*(dslrScale/100))), interpolation = cv2.INTER_AREA)
                    cv2.rectangle(dslrFrame, (int(dslrFrame.shape[1]/2), int(dslrFrame.shape[0]/2)), (int(dslrFrame.shape[1]/2), int(dslrFrame.shape[0]/2)), (255,0,0), 7)
                    dslrBytes = cv2.imencode('.ppm', dslrFrame)[1].tobytes()
                camFrameOrig = camClient.recv()
                camFrame = cv2.resize(camFrameOrig, (int(camFrameOrig.shape[1]*((camScale)/100)), int(camFrameOrig.shape[0]*(camScale/100))), interpolation = cv2.INTER_AREA)
                cv2.rectangle(camFrame, (int(camFrame.shape[1]/2), int(camFrame.shape[0]/2)), (int(camFrame.shape[1]/2), int(camFrame.shape[0]/2)), (255,0,0), 7)
                camBytes = cv2.imencode('.ppm', camFrame)[1].tobytes()
        except Exception as e:
            print("!!!!!!!!!!!ERROR!!!!!!!!!!")
            print(e)
            break
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
    elif button == "X":
        joy_button.update('Start joy')
        joy_button.update(button_color=('black', 'white'))
        track_button.update('Start følgning')
        track_button.update(button_color=('black', 'white'))
        point_button.update('Start klikk')
        point_button.update(button_color=('black', 'white'))
    elif button == "ON":
        enable_button.update('ON')
        enable_button.update(button_color=('white', 'green'))
    elif button == "OFF":
        enable_button.update('OFF')
        enable_button.update(button_color=('white', 'red'))
        

#--------------------Programmet----------------------------------
while True:
    try:

        for event in pygame.event.get():
            if event.type == pygame.JOYBUTTONDOWN:
                joyInput = True

        event, values = window.read(timeout=0)
        if not view_dslr_layout:
            if a_id:
                graph.delete_figure(a_id)    #slett forige bilde
            a_id = graph.draw_image(data=dslrBytes, location=(0,0))  #lag nytt bilde
            graph.TKCanvas.tag_lower(a_id)   #setter bildet bakerst, tegninger kommer over

        if view_dslr_layout:
            window['dslr_full'].update(data=dslrBytes)
            
        window['web'].update(data=camBytes)
        
        if event != old_event or joyInput:  #unngå at to eventer skal være like rett etter hverandre og oppheve seg selv: stopp like etter stopp - stopper og starter umiddelbart

            if event == 'X' or event == sg.WIN_CLOSED or (joystick.get_button(8) and not view_dslr_layout): #back
                print("Program stoppet av bruker")
                break
            
            elif event == 'F':
                window['BASE'].update(visible=False)
                window['FOCAL_INPUT'].update(visible=True)
                
            elif event == '+' or joystick.get_button(1): #a
                s.send("a".encode())
                time.sleep(0.2)
                joy = True
            
            elif event == 'Hjem' or joystick.get_button(3): #y
                s.send("h".encode())
                time.sleep(0.2)
                joy = True
                
            elif event == 'OFF' or joystick.get_button(0): #x:
                s.send("b".encode())
                if enable == False:
                    update_labels("ON") #oppdaterer seg til å få ON-label
                elif enable == True:
                    update_labels("OFF") #oppdaterer seg til å få ON-label
                time.sleep(0.2)
                enable = not enable
                
            elif event == 'Start følgning':
                if tracking:
                    tracking = False
                    track_button.update('Start følgning')
                    track_button.update(button_color=('black', 'white'))
                else:
                    #select roi
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
                    s.send("p{}".format(h_angle).encode())

            elif event == 'OK':
                update_focal()
                window['BASE'].update(visible=True)
                window['FOCAL_INPUT'].update(visible=False)
                
            elif event == 'Ut' or (joystick.get_button(8) and view_dslr_layout):
                window['BASE'].update(visible=True)
                window['FULL_DSLR'].update(visible=False)
                view_dslr_layout=False

        if joy:
            RAWvSpeed = joystick.get_axis(3)*100  #for å få riktige verdier i speed-funksjonen
            RAWhSpeed = joystick.get_axis(2)*100
            vSpeed = (speed(RAWvSpeed)/100)*-65
            hSpeed = (speed(RAWhSpeed)/100)*65

            RAWPanServo = joystick.get_axis(0)*100
            RAWTiltServo = joystick.get_axis(1)*100
            PanServo = (speed(RAWPanServo)/100)*8
            TiltServo = (speed(RAWTiltServo)/100)*-8
            
            if (hSpeed != Old_hSpeed or vSpeed != Old_vSpeed or PanServo != Old_PanServo or TiltServo != Old_TiltServo):
                if first_value:
                    s.send("j090,0,0,0".encode())#09 foran der er hvor lang stringen er 
                    first_value = False
                else:
                    data_string = "{:.0f},{:.0f},{:.0f},{:.0f}".format(hSpeed, vSpeed, PanServo, TiltServo)
                    data_length = len(data_string)
                    if data_length >= 10:
                        data_string = "j{}".format(data_length) + data_string
                    else:
                        data_string = "j0{}".format(data_length) + data_string
                    s.send(data_string.encode())
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
                    s.send("t{}".format(str(bbox)).encode())
                    point = True
                    if prior_rect:
                        graph.delete_figure(prior_rect)
                elif point:
                    s.sendall("m{}, {}".format(int(start_point[0]/(dslrScale/100)), int(start_point[1]/(dslrScale/100))).encode())
                    if prior_rect:
                        graph.delete_figure(prior_rect)
                    time.sleep(0.7)
                else:
                    window['BASE'].update(visible=False)
                    window['FULL_DSLR'].update(visible=True)
                    view_dslr_layout=True
            end_point = None #for å unngå at forrige bbox vises i millisekunder v/ ny
            down = False
            dragging = False
            update = False

        joyInput = False
        old_event = event   #unngå at to eventer skal være like rett etter hverandre og oppheve seg selv: stopp like etter stopp - stopper og starter umiddelbart
    except Exception as e:
        print("!!!!!!!!!!!ERROR!!!!!!!!!!")
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
