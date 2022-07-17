# AutoDSLR
Tracking pan-tilt DSLR head

På remote:  
```
sudo pip3 install -r requirements.txt
sudo pip3 install -U vidgear[core]
sudo apt install libgsm1 libatk1.0-0 libavcodec58 libcairo2 libvpx6 libvorbisenc2 libwayland-egl1 libva-drm2 libwavpack1 libshine3 libdav1d4 libwayland-client0 libxcursor1 libopus0 libchromaprint1 libxinerama1 libpixman-1-0 libzmq5 libmp3lame0 libxcb-shm0 libgtk-3-0 libharfbuzz0b libpangocairo-1.0-0 libvdpau1 libssh-gcrypt-4 libtwolame0 libnorm1 libxi6 libxfixes3 libxcomposite1 libxcb-render0 libwayland-cursor0 libvorbisfile3 libspeex1 libxrandr2 libxkbcommon0 libtheora0 libx264-160 libaom0 libzvbi0 libogg0 libpangoft2-1.0-0 librsvg2-2 libxvidcore4 libsrt1.4-gnutls libbluray2 libvorbis0a libdrm2 libmpg123-0 libatlas3-base libxdamage1 libavformat58 libatk-bridge2.0-0 libswscale5 libsnappy1v5 libcodec2-0.9 libsodium23 libudfread0 libswresample3 libcairo-gobject2 libx265-192 libthai0 libva-x11-2 ocl-icd-libopencl1 libepoxy0 libpango-1.0-0 libavutil56 libva2 librabbitmq4 libgme0 libatspi2.0-0 libgraphite2-3 libgfortran5 libsoxr0 libpgm-5.3-0 libopenmpt0 libxrender1 libdatrie1 libgdk-pixbuf-2.0-0 libopenjp2-7 libwebpmux3

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
692
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
