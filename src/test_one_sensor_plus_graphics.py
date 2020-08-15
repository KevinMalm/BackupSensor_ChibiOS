from tkinter import *
from PIL import ImageTk, Image
import time
import threading
import random
import queue

from src.VL53L0X_api import VL53L0X_Sensor
import smbus


class RadarStripes:
    offset_x, offset_y = 200, 200
    state = 0
    path = 'Graphics/Radar_Stripes/stripe_'
    n = 6
    imgs = []
    current_img = None
    canvas_img = None   
    lcl_canvas = None

    def __init__(self, canvas, x_offst = 0, y_offset = 0, base_path = 'Graphics/Radar_Stripes/stripe_', n = 6):
        self.path = base_path
        self.offset_x = x_offst
        self.offset_y = y_offset
        self.state = 1
        self.lcl_canvas = canvas
        #build images
        i = self.state
        while(i <= n):
            lcl_path = self.path + repr(i) + ".png"
            img_n = ImageTk.PhotoImage(Image.open(lcl_path).resize((int(244*1.2), int(250*1.2)), Image.ANTIALIAS)) #244 x 250
            self.imgs.append(img_n)
            i += 1
        self.current_img = self.imgs[self.state]
        self.canvas_img = self.lcl_canvas.create_image(self.offset_x, self.offset_y, anchor=CENTER, image=self.current_img)
    
    def increment(self):
        self.state += 1
        if(self.state >= len(self.imgs)):
            self.state = 0
        self.current_img = self.imgs[self.state]
        self.lcl_canvas.itemconfigure(self.canvas_img, image = self.current_img)
    def set_state(self, s):
        self.state = s
        if(self.state >= len(self.imgs)):
            self.state = 0
        #self.current_img = self.imgs[self.state]
        self.current_img = self.current_img.resize(int(s/200), int(s/200), Image.ANTIALIAS)
        self.lcl_canvas.itemconfigure(self.canvas_img, image = self.current_img)      



class Application:
    car_path = 'Graphics/car_img.png'
    test_path = 'Graphics/Test_Red.png'
    bg_path = 'Graphics/bg.png'

    WIDTH, HEIGHT = 416, 900

    def add_bg_image(self, canvas, path, size_x, size_y, offset_x = 0, offset_y = 0, img_anchor = NW):
        bg_img = ImageTk.PhotoImage(Image.open(path).resize((size_x, size_y), Image.ANTIALIAS))
        canvas.background = bg_img  # Keep a reference in case this code is put in a function.
        bg = canvas.create_image(0, 0, anchor=NW, image=bg_img)
        return bg
        img = ImageTk.PhotoImage(Image.open(path).resize((size_x, size_y), Image.ANTIALIAS))
        obj = canvas.create_image(offset_x, offset_y, image = img, anchor=img_anchor)
        return obj
    
    def add_image(self, canvas, path, size_x, size_y, offset_x = 0, offset_y = 0, center = True):
        if(center):
            offset_x = self.WIDTH / 2
            offset_y = self.HEIGHT / 2
        obj = ImageTk.PhotoImage(Image.open(path).resize((size_x, size_y), Image.ANTIALIAS))
        canvas.create_image(offset_x, offset_y, image=obj, anchor=CENTER)
        return obj

    images = {

    }


    def __init__(self, queue, endCommand):
        self.queue = queue

        self.root = Tk()
        self.root.geometry('{}x{}'.format(self.WIDTH, self.WIDTH))

        canvas = Canvas(self.root, width=self.WIDTH, height=self.HEIGHT)
        canvas.pack()

        bg = self.add_bg_image(canvas, self.bg_path, self.WIDTH, self.HEIGHT)
        self.images['front_driver_radar'] = RadarStripes(canvas, x_offst=self.WIDTH / 2, y_offset=237)  #152, 272
        self.images['front_driver_radar_red'] = RadarStripes(canvas, x_offst=152, y_offset=237, base_path='Graphics/Radar_Stripes/Red_Radar_Series/Sensor_Hit_', n = 9)
        self.images['rear_driver_radar'] = RadarStripes(canvas, x_offst=self.WIDTH / 2, y_offset=653)
        self.images['car_img'] = self.add_image(canvas, self.car_path, 290, 536)

    def process(self, v):
        if(v < 50):
            self.images['front_driver_radar_red'].set_state(1)
            return
        if(v < 150):
            self.images['front_driver_radar_red'].set_state(2)
            return      
        if(v < 500):
            self.images['front_driver_radar_red'].set_state(3)
            return   
        if(v < 800):
            self.images['front_driver_radar_red'].set_state(4)
            return   
        if(v < 1500):
            self.images['front_driver_radar_red'].set_state(5)
            return                     
    def processIncoming(self):
        """Handle all messages currently in the queue, if any."""
        #while self.queue.qsize(  ):
        try:
            msg = self.queue.get()
            self.images['front_driver_radar'].increment()
            self.images['rear_driver_radar'].increment()
            self.process(msg)
            print(msg)
        except queue.Empty:

            pass

    def run_main_loop(self):
        print('running')
        self.root.mainloop()

class data_struct:
    value = 0
    def __init__(self):
        self.value = 0
    
    def set(self, v):
        self.value = v
    def get(self):
        return self.value

class ThreadedClient:

    sensor = None

    def __init__(self, app, q):
        self.sensor = VL53L0X_Sensor(smbus.SMBus(1), address=0x29)
        self.sensor.start()
        self.application = app
        self.queue = q
        self.running = 1
        self.thread1 = threading.Thread(target=self.workerThread1)
        self.thread1.start(  )
        self.periodicCall(  )

    def periodicCall(self):

        self.application.processIncoming(  )
        if not self.running:
            import sys
            sys.exit(1)
        self.application.root.after(200, self.periodicCall)

    def workerThread1(self):

        while self.running:
            time.sleep(0.2)
            msg = self.sensor.getDistance()
            self.queue.set(msg)

    def endApplication(self):
        self.running = 0


q = data_struct() #queue.Queue(  )
app = Application(q, None)
rand = random.Random(  )

client = ThreadedClient(app, q)
app.run_main_loop()

while(True):
    print('here')
    time.sleep(3)