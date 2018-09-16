'''
Created on May 18, 2018

@author: keonw
'''

import tkinter as tk
import time
import threading
import random
import queue



class taskManager:
    def __init__(self, root, client):
        self.root = root
        self.rand = random.Random()
        self.client = client
    
    def run(self):
        self.root.mainloop()

class GUI:
    def __init__(self, master, queue, endCommand):
        self.queue = queue
        
    def processIncoming(self):
        while self.queue.qsize():
            try:
                msg = self.queue.get(0)
                print(msg)
            except queue.Empty:
                pass

class ThreadedClient:
    def __init__(self, master):
        self.master = master
        self.queue = queue.Queue()
        self.gui = GUI(master, self.queue, self.endApplication)
        self.running = 1
        self.thread1 = threading.Thread(target=self.workerThread1)
        self.thread1.start()
        self.periodicCall()
    
    def periodicCall(self):
        self.gui.processIncoming()
        if not self.running:
            import sys
            sys.exit(1)
        self.master.after(100, self.periodicCall)
        
    def workerThread1(self):
        while self.running:
            time.sleep(taskManager.rand.random()*0.3)
            msg = taskManager.rand.random()
            self.queue.put(msg)
            
    def endApplication(self):
        self.running = 0
            