from tkinter import *
from PIL import ImageTk, Image
import math


SCALE_FACTOR = 0.339

MAX_MM = 8000
MIN_MM = 200
MAX_DISPLAY_MM = 600

FILE_HEADER = ''

class RadarStripes:
    blank_path = FILE_HEADER + 'Graphics/Radar_Stripes/blank.png'
    offset_x, offset_y = 200, 200
    scale_x, scale_y = int(810 * SCALE_FACTOR), int(829 * SCALE_FACTOR) #244 250
    pos_x, pos_y = 0,0
    state = 0
    path = ''
    blank_img = None
    imgs = []
    current_img = None
    canvas_img = None   
    lcl_canvas = None
    disabled = False

    def __init__(self, canvas, x_offst = 0, y_offset = 0, n = 6, path = 'Graphics/Radar_Stripes/stripe_'):
        self.path = FILE_HEADER + path
        self.offset_x = x_offst
        self.offset_y = y_offset
        self.state = 0
        self.lcl_canvas = canvas
        self.disabled = False


        #build images
        self.imgs = []
        i = self.state
        while(i <= n):
            lcl_path = self.path + repr(i) + ".png"
            img_n = ImageTk.PhotoImage(Image.open(lcl_path).resize((self.scale_x, self.scale_y), Image.ANTIALIAS)) #244 x 250
            self.imgs.append(img_n)
            i += 1
        self.current_img = self.imgs[self.state]

        self.canvas_img = self.lcl_canvas.create_image(self.offset_x, self.offset_y, anchor = CENTER, image = self.current_img)
        #build blank image 
        self.blank_img = ImageTk.PhotoImage(Image.open(self.blank_path).resize((self.scale_x, self.scale_y), Image.ANTIALIAS)) #244 x 250

    
    def increment(self):
        if(self.disabled):
            return
        self.state += 1
        if(self.state >= len(self.imgs)):
            self.state = 0
        self.set_state(None)

    error_counter = 0
    def set_state(self, n):
        if(n != None and n < 0): #error handler
            self.error_counter += 1
            if(self.error_counter < 15):
                return
            n = 0
        self.error_counter = 0 #reset
        if(n != None):
            self.state = n 
        self.current_img = self.imgs[self.state]
        self.lcl_canvas.itemconfigure(self.canvas_img, image = self.current_img)
    
    def set_disabled(self, v: bool):
        self.disabled = v
        if(self.disabled):
            self.lcl_canvas.itemconfigure(self.canvas_img, image = self.blank_img)
        else:
            self.lcl_canvas.itemconfigure(self.canvas_img, image = self.current_img)


class RadarBlob:
    img_path = FILE_HEADER + 'Graphics/Radar_Stripes/Red_Radar_Series/DOT.png'
    blank_path = FILE_HEADER + 'Graphics/Radar_Stripes/Red_Radar_Series/BLOCK_BLANK.png'
    origin = {'x': 0, 'y': 0}
    x_factor, y_factor = 1, 1
    sensor_angle = 0
    x_pos, y_pos = 0, 0
    states = 8
    size_x, size_y = int(400 * SCALE_FACTOR), int(112 * SCALE_FACTOR)
    canvas_img = None
    blank_img = None
    lcl_canvas = None
    disabled = None

    def __init__(self, _canvas, _x, _y, _origin, _sensor_angle, _size_x = 150, _size_y = 150, _x_factor = 1, _y_factor = 1):
        self.x_factor = _x_factor
        self.y_factor = _y_factor
        self.lcl_canvas = _canvas

        self.origin = _origin
        self.sensor_angle = math.radians(_sensor_angle)
 
        self.size_x, self.size_y = int(_size_x * SCALE_FACTOR), int(_size_y * SCALE_FACTOR)
        self.x_pos = self.origin['x'] + _x - (self.size_x)
        self.y_pos = self.origin['y'] + _y - (self.size_y / 2)
        #build Images
        self.img = ImageTk.PhotoImage(Image.open(self.img_path).resize((self.size_x, self.size_y), Image.ANTIALIAS)) 
        self.blank_img = ImageTk.PhotoImage(Image.open(self.blank_path).resize((self.size_x, self.size_y), Image.ANTIALIAS))
        self.canvas_img = self.lcl_canvas.create_image(self.x_pos, self.y_pos, anchor = CENTER, image = self.img)

    def set_disabled(self, v: bool):
        if(self.disabled == v):
            return
        self.disabled = v
        if(self.disabled):
            self.lcl_canvas.itemconfigure(self.canvas_img, image = self.blank_img)
        else:
            self.lcl_canvas.itemconfigure(self.canvas_img, image = self.img)
    def animate(self):
        return

    #gets value of mm
    def update_distance(self, v):
        #v = (v - MIN_MM) / (MAX_MM - MIN_MM)
        x = math.floor(math.sin(self.sensor_angle) * v * self.x_factor)
        y = math.floor(math.cos(self.sensor_angle) * v * self.y_factor)
        x_delta  = (self.origin['x'] + x) - (self.size_x / 2) - self.x_pos
        y_delta = (self.origin['y'] + y)  - (self.size_x / 2) - self.y_pos
        self.lcl_canvas.move(self.canvas_img, x_delta, y_delta)
        self.x_pos += x_delta
        self.y_pos += y_delta
        return 

'''
point max offset: 130
point min offset: 40
'''
class RadarBlock:
    x_factor, y_factor = 1, 1
    img_path = FILE_HEADER + 'Graphics/Radar_Stripes/Red_Radar_Series/BLOCK'
    blank_path = FILE_HEADER + 'Graphics/Radar_Stripes/Red_Radar_Series/BLOCK_BLANK.png'
    origin = {'x': 0, 'y': 0}
    x_pos, y_pos = 0, 0
    size_x, size_y = int(400 * SCALE_FACTOR), int(112 * SCALE_FACTOR)
    canvas_img = None
    blank_img = None
    lcl_canvas = None
    disabled = None

    def __init__(self, _canvas, _x, _y, _origin, _x_factor = 1, _y_factor = 1, img_type = '', _size_x = 400, _size_y = 51):
        self.lcl_canvas = _canvas
        self.x_pos = _x
        self.y_pos = _y
        self.origin = _origin
        self.x_factor = _x_factor
        self.y_factor = _y_factor
        self.size_x, self.size_y = int(_size_x * SCALE_FACTOR), int(_size_y * SCALE_FACTOR)

        #build Images
        self.img = ImageTk.PhotoImage(Image.open(self.img_path + img_type + '.png').resize((self.size_x, self.size_y), Image.ANTIALIAS))    
        self.blank_img = ImageTk.PhotoImage(Image.open(self.blank_path).resize((self.size_x, self.size_y), Image.ANTIALIAS))
        self.canvas_img = self.lcl_canvas.create_image(self.origin['x'] + (self.x_pos * self.x_factor), self.origin['y'] + (self.y_pos * self.y_factor), anchor = CENTER, image = self.img)

    def set_disabled(self, v: bool):
        if(self.disabled == v):
            return
        self.disabled = v
        if(self.disabled):
            self.lcl_canvas.itemconfigure(self.canvas_img, image = self.blank_img)
        else:
            self.lcl_canvas.itemconfigure(self.canvas_img, image = self.img)
    
    def update_distance(self, config: {}):
        x_delta  = (self.origin['x'] + (config['x'] * self.x_factor))
        y_delta = (self.origin['y'] + (config['y'] * self.y_factor))
        self.lcl_canvas.moveto(self.canvas_img, x_delta, y_delta)
        return 

class Application:
    car_path = FILE_HEADER + 'Graphics/car_img.png'
    test_path = FILE_HEADER + 'Graphics/Test_Red.png'
    bg_path = FILE_HEADER + 'Graphics/bg.png'

    WIDTH, HEIGHT = 416, 900

    def add_bg_image(self, canvas, path, size_x, size_y, offset_x = 0, offset_y = 0, img_anchor = NW):
        bg_img = ImageTk.PhotoImage(Image.open(path).resize((size_x, size_y), Image.ANTIALIAS))
        canvas.background = bg_img  # Keep a reference in case this code is put in a function.
        bg = canvas.create_image(0, 0, anchor=NW, image=bg_img)
        return bg
    
    def add_image(self, canvas, path, size_x, size_y, offset_x = 0, offset_y = 0, center = True):
        if(center):
            offset_x = self.WIDTH / 2
            offset_y = self.HEIGHT / 2
        obj = ImageTk.PhotoImage(Image.open(path).resize((size_x, size_y), Image.ANTIALIAS))
        canvas.create_image(offset_x, offset_y, image=obj, anchor=CENTER)
        return obj




    images = { }

    def __init__(self, _data_structure, endCommand):
        self.data_structure = _data_structure

        self.root = Tk()
        self.root.geometry('{}x{}'.format(self.WIDTH, self.WIDTH))

        canvas = Canvas(self.root, width=self.WIDTH, height=self.HEIGHT)
        canvas.pack()

        bg = self.add_bg_image(canvas, self.bg_path, self.WIDTH, self.HEIGHT)

        #x: 152 - 272
        #y: 237 - 653

        #default radar 
        self.images['front_radar'] = RadarStripes(canvas, x_offst=self.WIDTH / 2, y_offset=237) 
        self.images['rear_radar'] = RadarStripes(canvas, x_offst=self.WIDTH / 2, y_offset=645)

        #ping radar
        self.images['front_driver_ping'] = RadarStripes(canvas, x_offst=152, y_offset=237, path = 'Graphics/Radar_Stripes/Red_Radar_Series/Sensor_Hit_', n = 9)
        self.images['front_passenger_ping'] = RadarStripes(canvas, x_offst=264, y_offset=237, path = 'Graphics/Radar_Stripes/Red_Radar_Series/Sensor_Hit_', n = 9)
        self.images['rear_driver_ping'] = RadarStripes(canvas, x_offst=152, y_offset=653, path = 'Graphics/Radar_Stripes/Red_Radar_Series/Sensor_Hit_', n = 9)
        self.images['rear_passenger_ping'] = RadarStripes(canvas, x_offst=264, y_offset=653, path = 'Graphics/Radar_Stripes/Red_Radar_Series/Sensor_Hit_', n = 9)
        
        x = 78
        y = 244
        xx = 58
        yy = 234

        y_y = 653
        y_yy = 663

        h = 200
        self.line_a = canvas.create_line(int((self.WIDTH / 2) - (x)), y, int((self.WIDTH / 2) - (x + math.sin(math.radians(155)) * h)), y +math.cos(math.radians(155)) * h, dash=(4, 2))
        self.line_b = canvas.create_line(int((self.WIDTH / 2) - (xx)), yy, int((self.WIDTH / 2) - (xx + math.sin(math.radians(170)) * h)), yy + math.cos(math.radians(170)) * h, dash=(4, 2))
        self.line_c = canvas.create_line(int((self.WIDTH / 2) + (x)), y, int((self.WIDTH / 2) + (x + math.sin(math.radians(25)) * h)), y - math.cos(math.radians(25)) * h, dash=(4, 2))
        self.line_d = canvas.create_line(int((self.WIDTH / 2) + (xx)), yy, int((self.WIDTH / 2) + (xx + math.sin(math.radians(10)) * h)), yy - math.cos(math.radians(10)) * h, dash=(4, 2))

        self.line_e = canvas.create_line(int((self.WIDTH / 2) - (x)), y_y, int((self.WIDTH / 2) - (x + math.sin(math.radians(155)) * h)), y_y -math.cos(math.radians(155)) * h, dash=(4, 2))
        self.line_f = canvas.create_line(int((self.WIDTH / 2) - (xx)), y_yy, int((self.WIDTH / 2) - (xx + math.sin(math.radians(170)) * h)), y_yy-math.cos(math.radians(170)) * h, dash=(4, 2))
        self.line_g = canvas.create_line(int((self.WIDTH / 2) + (x)), y_y, int((self.WIDTH / 2) + (x + math.sin(math.radians(25)) * h)), y_y + math.cos(math.radians(25)) * h, dash=(4, 2))
        self.line_h = canvas.create_line(int((self.WIDTH / 2) + (xx)), y_yy, int((self.WIDTH / 2) + (xx + math.sin(math.radians(10)) * h)), y_yy + math.cos(math.radians(10)) * h, dash=(4, 2))

        #blocks
        self.images['front_block'] = RadarBlock(canvas, _x=0, _y=0, _origin = {'x':self.WIDTH / 2, 'y':207}, _y_factor = 1, _size_x = 310, _size_y = 34, img_type = '_FRONT')
        
        self.images['front_driver_blob'] = [
            RadarBlob(canvas, _x = 0, _y = 0, _origin = {'x':int((self.WIDTH / 2) - (78)), 'y':244}, _sensor_angle = 155, _x_factor = -1, _y_factor = 1),
            RadarBlob(canvas, _x = 0, _y = 0, _origin = {'x':int((self.WIDTH / 2) - (58)), 'y':234}, _sensor_angle = 170, _x_factor = -1, _y_factor = 1)

        ]

        self.images['front_passenger_blob'] = [
            RadarBlob(canvas, _x = 0, _y = 0, _origin = {'x':int((self.WIDTH / 2) + (78)), 'y':244}, _sensor_angle = 25, _x_factor = 1, _y_factor = -1),
            RadarBlob(canvas, _x = 0, _y = 0, _origin = {'x':int((self.WIDTH / 2) + (58)), 'y':234}, _sensor_angle = 10, _x_factor = 1, _y_factor = -1)

        ]

        self.images['rear_driver_blob'] = [
            RadarBlob(canvas, _x = 0, _y = 0, _origin = {'x':int((self.WIDTH / 2) - (78)), 'y':653}, _sensor_angle = 155, _x_factor = -1, _y_factor = 1),
            RadarBlob(canvas, _x = 0, _y = 0, _origin = {'x':int((self.WIDTH / 2) - (58)), 'y':663}, _sensor_angle = 170, _x_factor = -1, _y_factor = 1)

        ]

        self.images['rear_passenger_blob'] = [
            RadarBlob(canvas, _x = 0, _y = 0, _origin = {'x':int((self.WIDTH / 2) + (78)), 'y':653}, _sensor_angle = 25, _x_factor = 1, _y_factor = -1),
            RadarBlob(canvas, _x = 0, _y = 0, _origin = {'x':int((self.WIDTH / 2) + (58)), 'y':663}, _sensor_angle = 10, _x_factor = 1, _y_factor = -1)

        ]
        
        #self.images['front_driver_block'] = RadarBlock(canvas, _x=0, _y=0, _origin = {'x':int((self.WIDTH / 2) - (68)), 'y':222}, _x_factor = -1, _y_factor = 1, img_type = '_DRIVER_FRONT', _size_x = 147, _size_y = 120)
        #self.images['front_passenger_block'] = RadarBlock(canvas, _x=0, _y=0, _origin = {'x':int((self.WIDTH / 2) + (68)), 'y':222}, _y_factor = 1, img_type = '_PASSENGER_FRONT',  _size_x = 147, _size_y = 120)

        self.images['rear_block'] = RadarBlock(canvas, _x=0, _y=0, _origin = {'x':self.WIDTH / 2, 'y':668}, _y_factor = -1, _size_x = 310, _size_y = 34, img_type = '_REAR')
        #self.images['rear_driver_block'] = RadarBlock(canvas, _x=0, _y=0, _origin = {'x':int((self.WIDTH / 2) - (68)), 'y':654}, _x_factor = -1, _y_factor = -1, img_type = '_DRIVER_REAR', _size_x = 147, _size_y = 120)
        #self.images['rear_passenger_block'] = RadarBlock(canvas, _x=0, _y=0, _origin = {'x':int((self.WIDTH / 2) + (68)), 'y':654}, _y_factor = -1, img_type = '_PASSENGER_REAR',  _size_x = 147, _size_y = 120)

        #car overlay
        self.images['car_img'] = self.add_image(canvas, self.car_path, int(888 * SCALE_FACTOR), int(1578 * SCALE_FACTOR))



    '''
    Graphic Update Logic (For Side - Front / Back)
        Case 0 - (point + driver + passenger all None):
            All Pings and Blocks disabled and Default Radar enabled

        Case 1 - (point got a hit but driver + passenger are None):
            Default Radar disabled
            Both Ping Radars enabled
            Forward Block enabled 
            Side Blocks disabled 
        
        Case 2 - (point and 1 side are None but other Side got a hit):
            Default Radar and None Side are disabled
            Ping Radar on corresponding side enabled  - update with distance measure 
            If Close enough : pinged block is enabled 
            None Side and front Block Disabled
        
        Case 3 - (both sides got a hit and point is None):
            Default Radar is disabled
            Ping Radar and both Sides are enabled - update with distance measure 
            If Close enough for each side: corresponding pinged block is enabled 
            Front Block is Disabled 
    '''

    def mm_to_pixels(self, v):
        f = (v - MIN_MM) / (MAX_MM - MIN_MM)

        return int((f * 13.75 + 40) /15) * 15;
    def compute_point_on_screen(self, origin, distance):
        if(distance['type'] == 'point'):
            return {'x': 0, 'y': self.mm_to_pixels(distance['data']), 'w': 0}
        return {'x': 0 , 'y': 0, 'w': 0}

    def update_graphics_side(self, side, data):
        quad_data = data[side]
        if(quad_data == None):
            self.images[side+'_blob'][0].set_disabled(True)
            self.images[side+'_blob'][1].set_disabled(True)
            return
        i = 0
        for data in quad_data:
            if(data == None):
                self.images[side+'_blob'][i].set_disabled(True)
            else:
                self.images[side+'_blob'][i].set_disabled(False)
                self.images[side+'_blob'][i].update_distance(self.mm_to_pixels(data))
                self.images[side+'_blob'][i].animate()
            i += 1
        return

    def update_graphics_rear_front(self, side, data):

        if(data[side+'_point'] == None and data[side+'_driver'] == None and data[side+'_passenger'] == None): #CASE 0
            # turn on default radar
            self.images[side+'_radar'].set_disabled(False)

            # turn off ping radar both both sides
            self.images[side+'_driver_ping'].set_disabled(True)
            self.images[side+'_passenger_ping'].set_disabled(True)
            # turn off all blocks 
            
            #self.images[side+'_driver_block'].set_disabled(True)
            #self.images[side+'_passenger_block'].set_disabled(True)
            self.images[side+'_block'].set_disabled(True)
            
            #update graphics
            self.images[side+'_radar'].increment()
            return

        if(data[side+'_point'] != None and data[side+'_driver'] == None and data[side+'_passenger'] == None): #CASE 1
            # turn off default radar 
            self.images[side+'_radar'].set_disabled(True)
            # turn on ping radar both both sides
            self.images[side+'_driver_ping'].set_disabled(False)
            self.images[side+'_driver_ping'].increment()
            self.images[side+'_passenger_ping'].set_disabled(False)
            self.images[side+'_passenger_ping'].increment()

            # turn of side blocks and update 
            if(data[side+'_point'] < self.max_display_mm):
                self.images[side+'_block'].set_disabled(False)
                #self.images[side+'_block'].update_distance(config = self.compute_point_on_screen(origin = self.images[side+'_block'].origin, distance = {'type': 'point', 'data': data[side+'_point']}))
            else:
                self.images[side+'_block'].set_disabled(True)
            return

        self.update_graphics_side(side+'_driver', data)
        #self.update_graphics_side(side+'_passenger', data)

        return
        '''
        if(data[side+'_point'] != None): #Object is in front of Us: We Must Turn off Basic radar and enable both sides and add block
            self.image[side+'_driver_radar'].set_disabled(True)
            self.image[side+'_driver_ping'].set_disabled(False)
            self.image[side+'_passenger_ping'].set_disabled(False)
            #Turn on Forward Block 
            self.image[side+'_block'].set_disabled(False)
        else :
            #Turn off Forward Block
            self.image[side+'_block'].set_disabled(True)

        self.update_graphics_side(side +'_driver', data)
        self.update_graphics_side(side +'_passenger', data)
        '''

    def processIncoming(self):
        """Handle all messages currently in the queue, if any."""
        try:
            msg = self.data_structure.unpack()
            #Front Handler
            self.update_graphics_rear_front('front', msg)
            #self.update_graphics_rear_front('rear', msg)
        except Exception:
            # just on general principles, although we don't
            # expect this branch to be taken in this case
            traceback.print_exc()
            pass

    def run_main_loop(self):
        print('running')
        self.root.mainloop()

