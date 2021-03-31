#! /usr/bin/env python3

# Echo client program
import socket, sys, re

sys.path.append("../lib")       # for params
import params
import pickle # for image serialization
import cv2

from encapFramedSock import EncapFramedSock


switchesVarDefaults = (
    (('-s', '--server'), 'server', '127.0.0.1:50001'),
    (('-f', '--filename'), 'filename', 'clip.mp4'),
    (('-d', '--debug'), 'debug', False), # boolean (set if present)
    (('-?', '--usage'), 'usage', False), # boolean (set if present)
    )


progname = "framedClient"
paramMap = params.parseParams(switchesVarDefaults)

server, usage, debug  = paramMap['server'], paramMap['usage'], paramMap['debug']
filename = paramMap['filename']

if usage:
    params.usage()


try:
    serverHost, serverPort = re.split(':', server)
    serverPort = int(serverPort)
except:
    print("Can't parse server:port from '%s'" % server)
    sys.exit(1)

addrFamily = socket.AF_INET
socktype = socket.SOCK_STREAM
addrPort = (serverHost, serverPort)

sock = socket.socket(addrFamily, socktype)

if sock is None:
    print('could not open socket')
    sys.exit(1)

sock.connect(addrPort)

fsock = EncapFramedSock((sock, addrPort))

# send filename
fsock.send( str.encode(filename), debug)

# start receiving frames
#fsock.send(b'ready')
payload = fsock.receive(debug)

if not payload:     # done
    if debug:
        print(f'connection to {addr} lost, exiting')
    fsock.close()
    exit()

frame=pickle.loads(payload)

if debug:
    print('Displaying frame')        

# display the image in a window called "video" and wait 10s 10000ms
# before exiting
cv2.imshow('Video', frame)
cv2.waitKey(10000)

# cleanup the windows
cv2.destroyAllWindows()




