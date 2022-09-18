# AutoDSLR
Tracking pan-tilt DSLR head

På remote:  
```
sudo pip3 install -r requirements.txt
sudo pip3 install -U vidgear[core]
sudo apt install libgraphite2-3 libatspi2.0-0 libthai0 libxcb-shm0 libxcb-render0 libswscale5 librsvg2-2 libvorbisenc2 libavutil56 libzvbi0 libgsm1 libxinerama1 libxvidcore4 libsrt1.4-gnutls libswresample3 libatk1.0-0 libvorbisfile3 libogg0 libpangoft2-1.0-0 libpgm-5.3-0 libwayland-egl1 libharfbuzz0b libpango-1.0-0 libcairo2 libva-x11-2 libwayland-cursor0 libgfortran5 libxfixes3 libgme0 libxrender1 libvorbis0a libxi6 libudfread0 libspeex1 libwebpmux3 libsodium23 libdatrie1 libatk-bridge2.0-0 libxrandr2 libbluray2 libx264-160 libwavpack1 libxcomposite1 libpangocairo-1.0-0 libsoxr0 libshine3 libxkbcommon0 libvdpau1 libgtk-3-0 libopus0 librabbitmq4 libgdk-pixbuf-2.0-0 libavformat58 libmpg123-0 libxdamage1 libzmq5 libdav1d4 libopenmpt0 libatlas3-base libva2 libva-drm2 libxcursor1 libssh-gcrypt-4 libavcodec58 libaom0 libx265-192 libwayland-client0 libcairo-gobject2 libcodec2-0.9 libpixman-1-0 libdrm2 libsnappy1v5 libnorm1 libopenjp2-7 libtheora0 ocl-icd-libopencl1 libtwolame0 libvpx6 libepoxy0 libchromaprint1 libmp3lame0

#sudo apt-get install libatlas-base-dev libhdf5-dev libhdf5-serial-dev libatlas-base-dev libjasper-dev -y

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

cd /usr/local/lib/python3.9/dist-packages/vidgear/gears
sudo nano netgear.py
ctrl+"-"
681
endre fra 96 til 1
ctrl+"x"
y
enter

```


Problemer:

Koden for remote er egt. utdatert. Noe feil med "ved klikk" 10x for mye eller noe

Sliter med å få lock ved tracking

Krasjer med error "Broken pipe" stadig

![The head](https://github.com/AutomaticBirdPhotography/AutoDSLR/blob/main/Motorisert_kamerahode_2021-Jan-22_10-43-36PM-000_CustomizedView906122989%20(2).png?raw=true)
