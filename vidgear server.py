from vidgear.gears import VideoGear
from vidgear.gears import NetGear

stream = VideoGear(source=0).start()
server = NetGear("192.168.10.155", 8080)

while True:
    try: 
        frame = stream.read()

        if frame is None:
            break

        server.send(frame)

    except KeyboardInterrupt:
        break

stream.stop()
server.close()