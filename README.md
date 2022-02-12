# AutoDSLR
Tracking pan-tilt DSLR head

På remote:  
```
sudo pip install -r requirements.txt
sudo pip install vidgear
sudo apt-get install libatlas-base-dev libhdf5-dev libhdf5-serial-dev libatlas-base-dev libjasper-dev -y
cd /usr/share/applications
sudo cp python3.9.desktop remote.desktop
sudo nano remote.desktop
[Desktop Entry]
Encoding=UTF-8
Type=Application
Name=PanTilt Remote
Icon=/home/pi/Documents/AutoDSLR-main/icon.png
Terminal=true
Exec=/usr/bin/python3.9 /home/pi/Documents/AutoDSLR-main/pan_tilt_remote_v2.py
StartupNotify=false
Categories=Other

sudo cp remote.desktop shutdown.desktop
sudo nano shutdown.desktop
[Desktop Entry]
Encoding=UTF-8
Type=Application
Name=Shutdown
Icon=/home/pi/Documents/AutoDSLR-main/shutdown.png
Terminal=true
Exec=/usr/bin/python3.9 /home/pi/Documents/AutoDSLR-main/shutdown.py
StartupNotify=false
Categories=Other
```


Problemer:

Sliter med å få lock ved tracking

Krasjer med error "Broken pipe" stadig

![The head](https://github.com/AutomaticBirdPhotography/AutoDSLR/blob/main/Motorisert_kamerahode_2021-Jan-22_10-43-36PM-000_CustomizedView906122989%20(2).png?raw=true)
