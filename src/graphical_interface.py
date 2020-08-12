from tkinter import *
from PIL import ImageTk, Image
import time
import threading
import random
import queue



class RadarStripes:
    offset_x, offset_y = 200, 200
    state = 0
    path = 'Graphics/Radar_Stripes/stripe_'
    n = 6
    imgs = []
    current_img = None
    canvas_img = None   
    lcl_canvas = None

    def __init__(self, canvas, x_offst = 0, y_offset = 0):
        self.offset_x = x_offst
        self.offset_y = y_offset
        self.state = 1
        self.lcl_canvas = canvas
        #build images
        i = self.state
        while(i <= self.n):
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
        self.images['front_driver_radar'] = RadarStripes(canvas, x_offst=self.WIDTH / 2, y_offset=237)
        #self.images['front_passenger_radar'] = RadarStripes(canvas, x_offst=272, y_offset=237)
        self.images['rear_driver_radar'] = RadarStripes(canvas, x_offst=self.WIDTH / 2, y_offset=653)
        #self.images['rear_passenger_radar'] = RadarStripes(canvas, x_offst=272, y_offset=653)
        self.images['car_img'] = self.add_image(canvas, self.car_path, 290, 536)


    def processIncoming(self):
        """Handle all messages currently in the queue, if any."""
        while self.queue.qsize(  ):
            try:
                msg = self.queue.get(0)
                self.images['front_driver_radar'].increment()
                #self.images['front_passenger_radar'].increment()
                self.images['rear_driver_radar'].increment()
                #self.images['rear_passenger_radar'].increment()
                print(msg)
            except queue.Empty:
                # just on general principles, although we don't
                # expect this branch to be taken in this case
                pass

    def run_main_loop(self):
        print('running')
        self.root.mainloop()

class ThreadedClient:



    def __init__(self, app, q):

        self.application = app
        self.queue = q

        #self.gui = GuiPart(master, self.queue, self.endApplication)

        self.running = 1
        self.thread1 = threading.Thread(target=self.workerThread1)
        self.thread1.start(  )
        self.periodicCall(  )

    def periodicCall(self):
        """
        Check every 200 ms if there is something new in the queue.
        """
        self.application.processIncoming(  )
        if not self.running:
            import sys
            sys.exit(1)
        self.application.root.after(200, self.periodicCall)

    def workerThread1(self):
        """
        This is where we handle the asynchronous I/O. For example, it may be
        a 'select(  )'. One important thing to remember is that the thread has
        to yield control pretty regularly, by select or otherwise.
        """
        while self.running:
            # To simulate asynchronous I/O, we create a random number at
            # random intervals. Replace the following two lines with the real
            # thing.
            time.sleep(0.2)
            msg = rand.random(  )
            self.queue.put(msg)

    def endApplication(self):
        self.running = 0


q = queue.Queue(  )
app = Application(q, None)
rand = random.Random(  )

client = ThreadedClient(app, q)
app.run_main_loop()

while(True):
    print('here')
    time.sleep(3)