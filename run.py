import serial
import time
import math
from time import sleep
from PIL import Image
from datetime import datetime
from os import listdir,system
from os.path import isfile, join
import os
deviceReady = False

DISPLAY_PIXEL_ORDER = [154, 132, 110, 88, 66, 44, 22, 0, 1, 
23, 45, 67, 89, 111, 133, 155, 156, 134, 112, 90, 68, 
46, 24, 2, 3, 25, 47, 69, 91, 113, 135, 157, 158, 136, 
114, 92, 70, 48, 26, 4, 5, 27, 49, 71, 93, 115, 137, 159,
 160, 138, 116, 94, 72, 50, 28, 6, 7, 29, 51, 73, 95, 
 117, 139, 161, 162, 140, 118, 96, 74, 52, 30, 8, 9, 31,
 53, 75, 97, 119, 141, 163, 164, 142, 120, 98, 76, 54,
 32, 10, 11, 33, 55, 77, 99, 121, 143, 165, 166, 144,
 122, 100, 78, 56, 34, 12, 13, 35, 57, 79, 101, 123, 145, 
 167, 168, 146, 124, 102, 80, 58, 36, 14, 15, 37, 59, 81, 
 103, 125, 147, 169, 170, 148, 126, 104, 82, 60, 38, 16,
 17, 39, 61, 83, 105, 127, 149, 171, 172, 150, 128, 106, 
 84, 62, 40, 18, 19, 41, 63, 85, 107, 129, 151, 173, 174, 
 152, 130, 108, 86, 64, 42, 20, 21, 43, 65, 87, 109, 131, 
 153, 175]
 
DISPLAYS = 3
WIDTH = 22
HEIGHT = 8 


class Object(object):
    pass

 
class Animation:

    def __init__(self, width, height, fps):       
        self.w = width
        self.h = height    
        self.fps = fps    
        self.frames = []  
        
        
    def setFPS(self,frames_per_second):
        self.fps = frames_per_second
        
        
    def appendFrame(self,frame):
        _frame = [0] * (self.w * self.h * 3) # pixels * 3 color channels
        if(frame):
            for i in range(0, len(frame)):
                if(i >= len(_frame)):
                    break
                _frame[i] = frame[i]
        self.frames.append(_frame)
        return len(self.frames) - 1 #return index of the newly added frame
        
        
    def setPixel(self,i,x,y,r,g,b):
        if(not(x >= 0 and x < self.w and y >= 0 and y < self.h)):   
            print('Unable to set a pixel, x: ' + str(x) + ', y: ' + str(y) + ' location out of picture frame')
            return False
        if(i >= len(self.frames)):
            print('Frame index out of lenght')
            return False
            
        index = y * self.w + x
        self.frames[i][index * 3 + 0] = r
        self.frames[i][index * 3 + 1] = g
        self.frames[i][index * 3 + 2] = b       
        return True
        

              
class Display:
    
    def __init__(self, width, height):      
        self.port = None
        self.port_root = '/dev/ttyUSB'
        self.port_search = 16    
        self.port_free = [True] * self.port_search
        self.arduino_baud = 1000000           
        self.w = width
        self.h = height    
        self.whiteBalance = [1.0,1.0,1.0]
        self.brightness = 0.1
        self.ready = True
        self.ready_time = 0
        self.number = -1
     
      
      
    #connect to a Arduino with that code number  
    def connect(self, number):     
        self.number = number
        print('')
        print('Finding an Arudino to connect to. My number is ' + str(self.number))
                 
        for i in range(0, self.port_search):
            port = self.port_root + str(i)
            data = [3]
            
            if(self.port == None and self.port_free[i] == True):               
                try:           
                    self.ser = serial.Serial(port, self.arduino_baud)    
                    print ('Serial port ' + port + ' opened')
                    
                    print('Waiting for Arduino to reset')
                    sleep(2)
                    
                    print ("Asking for a number of the Arduino")
                    self.ser.write(data)
                    
                    time = 0
                    while(True):
                        if self.ser.in_waiting:
                            num = int(self.ser.read())
                            print('Arduino\'s number is ' + str(num))
                            if(num == self.number):
                            #if(num == 0):
                                print('This is my Arduino! Setting the port to ' + port)
                                self.port = port
                                self.port_free[i] = False
                                return True
                            else:
                                print('It\'s not my Arduino.. Disconnecting..')
                                self.ser.close()
                                break
                        
                        sleep(0.001)
                        time = time + 1
                        if(time >= 100):
                            print('Connection timeout')
                            break
                            
                except serial.serialutil.SerialException:
                    print (port + " not avalible")
            else:
                return True
        
        return False
        
        
    def disconnect(self):
        self.ser.disconnect()
        port = None
        
        
    #WIP    
    def connected(self):
        return True
           
           
    def setWhiteBalance(self,r,g,b):
        self.whiteBalance = [r,g,b]
        
        
    def setBrightness(self,value):
        self.brightness = value
        
        
    def sendFrame(self,frame):
        if self.connected() and self.isReady():                 
            data = [None] * (len(frame)+1)
            data[0] = 2 # 2 = sending whole frame         
           
            i = 1
            j = 0
            while (i < len(frame) + 1):
                data[i + 0] = int(frame[DISPLAY_PIXEL_ORDER[j] * 3] * self.whiteBalance[0] * self.brightness)
                data[i + 1] = int(frame[DISPLAY_PIXEL_ORDER[j] * 3 + 1] * self.whiteBalance[1] * self.brightness)
                data[i + 2] = int(frame[DISPLAY_PIXEL_ORDER[j] * 3 + 2] * self.whiteBalance[2] * self.brightness)
                j += 1
                i += 3

            while(self.ser.in_waiting):
                self.ser.read()            
            self.ser.write(data)
            self.ready = False
            self.ready_time = int(round(time.time() * 1000))
            
    def isReady(self):
        if(not self.ready):
            if(self.ser.in_waiting):
                if(self.ser.read() == b'\x10'):
                    self.ready = True
                while(self.ser.in_waiting):
                    self.ser.read()
            
            if(int(round(time.time() * 1000)) - self.ready_time > 100):
                print('Arduino response timeout')
                while(self.ser.in_waiting):
                    self.ser.read()
                self.ready = True
        
        return self.ready      


    
'''        
def sendPixel(display, x, y, data):
    if (portOK()):
        deviceReady = False
        pixelData = []
        pixelData.append(0)

        w = W
        h = H

        rawIndex = (y * w) + x
        orderedIndex = pixelByteOrder[rawIndex]

        newX = orderedIndex % w
        newY = orderedIndex / w

        pixelData.append(newX)
        pixelData.append(newY)

        r = int(data[0] * WhiteBalance[0] * brightness)
        g = int(data[1] * WhiteBalance[1] * brightness)
        b = int(data[2] * WhiteBalance[2] * brightness)

        pixelData.append(255 if r > 255 else r)
        pixelData.append(255 if g > 255 else g)
        pixelData.append(255 if b > 255 else b)


        #print(pixelData)

        display.ser.write(pixelData)
'''




class GifRenderer:

    def __init__(self, display_count):
        self.n = display_count
        self.display = []
        
        for d in range(0, self.n):  
            self.display.append(Display(WIDTH,HEIGHT))
            self.display[-1].animations = []
            
        self.lasttime = 0    
    
        
    def connect(self):
        num = 0
        while num < self.n:
            if(not self.display[num].connect(num)):
                print ('Display ' + str(num) + ' failed to connect..')     
            else:
                print ('Display ' + str(num) + ' connected!')
                num += 1
            #wait for the arduino reset
            sleep(2)
        

    def appendGif(self, path):       
        f = 0
        gif = Image.open(path)

        try:
            gif.seek(f)
        except EOFError:
            return None
             
        name = os.path.basename(path)
        
        fps = 1.0
        try:
            fps = int(name[name.index('@')+1 : name.index('FPS')])
        except Exception as e:
            print('Wrong file name on ' + path)
             
        for d in range(0, self.n):             
            self.display[d].animations.append(Animation(WIDTH,HEIGHT,fps))
            

        while(gif):
            frame = gif.convert('RGB') 
            width, height = gif.size
            
            #print(gif.size)
            
            for d in range(0, self.n):
                self.display[d].animations[-1].appendFrame(None)
            
            for y in range(0, height):
                for x in range(0, width):
                    r, g, b = frame.getpixel((x, y))
                    
                    _x = int(math.floor(x % WIDTH))
                    _y = int(y)
                    d = int(math.floor(x / WIDTH))
                
                    #print(d)
                    
                    if(d < self.n):
                        self.display[d].animations[-1].setPixel(f, _x, _y, r, g, b)

            f += 1

            try:
                gif.seek(f) #load new frame of the gif
            except EOFError:
                break

   
    # very basic non well thought trů algorithm
    def play(self):            
        for a in range(0, len(self.display[0].animations)):
            
            frame_count = len(self.display[0].animations[a].frames)
            framerate = self.display[0].animations[a].fps

            for f in range(0, frame_count):
                
                for d in range(len(self.display)):
                    self.display[d].sendFrame(self.display[d].animations[a].frames[f])
                  
                for d in range(len(self.display)):                  
                    while(not self.display[d].isReady()):
                        sleep(0.001)

           
                while((time.time() - self.lasttime) < (1.0 / framerate)):
                    sleep(0.001)
                self.lasttime = time.time()




    
    
    
run = True

#path = '/mnt/usb/GIF_ANIMATIONS'
path = '/media/pi/DISPLAY/GIF_ANIMATIONS'

while(run):

    #try:
    if(True):    
        #os.system("sudo mount /dev/sda1 /mnt/usb")
        
        renderer = GifRenderer(DISPLAYS)
        renderer.connect()

        print("Searching for gifs...")

        files = [f for f in listdir(path) if isfile(join(path, f))]
        files.sort()

        print("Found:")
        
        for file_path in files:
            print("   " + file_path)
            renderer.appendGif(path + '/' + file_path)  
            
        while True:
            #try:

            hour = datetime.now().hour
            print('Hour: ' + str(hour))
            while((hour >= 18 and hour <= 23) or (hour >= 5 and hour <= 7) or (hour >= 0 and hour <= 1)):
                renderer.play()
                hour = datetime.now().hour
            sleep(1)

            #except Exception as e:
            #    print(e)
            
    #except Exception as e:
    #    print(e)
           
    #finally:
        #os.system("sudo umount /dev/sda1")
        #os.system('sudo shutdown -r now')
