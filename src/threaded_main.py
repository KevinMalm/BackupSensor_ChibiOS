import time
import threading
import tkinter
from graphical_interface import Application
from dummy_sensor_objects import DUMMY_SENSOR_SYSTEM

class ThreadedClient:
    def __init__(self, app, data_structure):

        self.application = app
        self.sensor_data_structure = data_structure

        #self.gui = GuiPart(master, self.queue, self.endApplication)

        self.running = 1
        self.thread1 = threading.Thread(target=self.workerThread1)
        self.thread1.start(  )
        self.periodicCall(  )

    def periodicCall(self):
        self.application.processIncoming()
        if not self.running:
            import sys
            sys.exit(1)
        #sleep for 200 ms 
        self.application.root.after(200, self.periodicCall)

    def workerThread1(self):
        while self.running:
            # Update Whichever Sensors Need to be Updated
            time.sleep(0.2)

    def endApplication(self):
        # Force Application to Exit 
        self.running = 0

data_structure = SENSOR_SYSTEM()
data_structure.start_sensors()
app = Application(data_structure, None)

client = ThreadedClient(app, data_structure)
app.run_main_loop()

while(True):
    print('here')
    time.sleep(3)