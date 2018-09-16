'''
Created on May 24, 2018

@author: keonw
'''
import tkinter as tk
import threading
import mazeRunner
import cozmo

class App(threading.Thread):
    
    def __init__(self, robot):
        threading.Thread.__init__(self)
        robot.drive_off_charger_on_connect = True
        cozmo.run_program(mazeRunner.cozmo_program(robot), use_viewer=True, force_viewer_on_top=True)
        self.start()
        
    def callback(self):
        self.root.quit()
        
    async def run(self):
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.callback)
        
        label = tk.Label(self.root, text = "Maze Runner")
        label.pack()
        
        
        self.root.update_idletasks()
        self.root.update()

    
robot = cozmo.robot.Robot    

async def run_program(robot):
    app = App(robot)
    await app.run()
    