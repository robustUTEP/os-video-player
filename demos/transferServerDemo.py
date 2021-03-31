#! /usr/bin/env python3

import sys
sys.path.append('../lib')       # for params
import re, socket, params, os
import pickle # for image serialization
import cv2
from threading import Thread
from encapFramedSock import EncapFramedSock


class Server(Thread):
    def __init__(self, sockAddr):
        Thread.__init__(self)
        self.sock, self.addr = sockAddr
        self.fsock = EncapFramedSock(sockAddr)
    def run(self):
        print(f'new thread handling connection from {self.addr}')

        payload = self.fsock.receive(debug)
        if debug:
            print(f'recvd: {payload}')
        if not payload:     # done
            if debug:
                print(f'connection to {self.addr} lost, exiting')
            self.fsock.close()
            return          # exit

        fileName = payload.decode()

        # open video file
        vidcap = cv2.VideoCapture(fileName)

        # make sure the we opened the file successfully
        if not vidcap.isOpened():
            print(f'Unable to open file {fileName}, does it exist?')
            self.fsock.close()
            return
        
        if debug:
            print(f'Reading frame')

        # read first image
        success,image = vidcap.read()

        # serialize the frame
        payload = pickle.dumps(image)
        
        if debug:
            print(f'Sending frame')
            
        self.fsock.send(payload, debug)

switchesVarDefaults = (
    (('-l', '--listenPort') ,'listenPort', 50001),
    (('-d', '--debug'), 'debug', False), # boolean (set if present)
    (('-?', '--usage'), 'usage', False), # boolean (set if present)
    )

progname = 'videoserver'
paramMap = params.parseParams(switchesVarDefaults)

debug, listenPort = paramMap['debug'], paramMap['listenPort']

if paramMap['usage']:
    params.usage()

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # listener socket
bindAddr = ("127.0.0.1", listenPort)
lsock.bind(bindAddr)
lsock.listen(5)
print(f'listening on: {bindAddr}')

while True:
    sockAddr = lsock.accept()
    server = Server(sockAddr)
    server.start()


