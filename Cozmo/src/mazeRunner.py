## Keon Williams
## Cozmo MazeRunner
## Main Class/Runner File

import cozmo
import asyncio
from colorDetection import ColorDetection
from quadTree import QuadTree, DrawQuad
import tkinter as tk

from cozmo.util import Angle, degrees, distance_inches, speed_mmps
from math import sin

LOOK_AROUND_STATE = 'look_around'
DRIVING_STATE = 'driving'

class MazeRunner():

    def __init__(self, robot):
        self.robot = robot
        self.robot.camera.image_stream_enabled = True
        self.robot.camera.color_image_enabled = True
        self.fov_x  = self.robot.camera.config.fov_x
        self.fov_y = self.robot.camera.config.fov_y

        self.color_detection = ColorDetection(robot)

        if not self.color_detection.cubes_connected():
            print('Cubes did not connect successfully - check that they are nearby. You may need to replace the batteries.')
            return
        self.color_detection.turn_on_cubes()
        
        self.state = None

        self.look_around_behavior = None # type: LookAroundInPlace behavior
        self.drive_action = None # type: DriveStraight action
        self.tilt_head_action = None # type: SetHeadAngle action
        self.rotate_action = None # type: TurnInPlace action
        self.lift_action = None # type: SetLiftHeight action
        
        self.conn = cozmo.conn.CozmoConnection

        self.quad_tree = QuadTree(0, {'x': 0, 'y': 0, 'width': 533, 'height': 533})
        self.maze = [];
        with open('map', 'w+') as mapFile:
            for line in mapFile:
                tempRow = list(line)
                self.maze.append(tempRow)
        mapFile.closed
        

    def abort_actions(self, *actions):
        for action in actions:
            if action != None and action.is_running:
                action.abort()

    def check_vision(self):
        width = self.color_detection.DOWNSIZE_WIDTH/2
        height = self.color_detection.DOWNSIZE_HEIGHT/2
        bottom_half_green = True
        for i in range (width):
            for j in range (height):
                if self.color_detection.pixel_matrix(i + width, j + height).value is not 'green':
                    bottom_half_green = False
        if bottom_half_green:
            self.quad_tree.insert({'x': -32, 'y': self.dist_from_wall(self.robot.camera.config.fov_y), 'width': 64, 'height': 3})       # FIX THIS W/ COZMO'S LOCATION!!!!!!!!!!!!!!!!!

    def dist_from_wall(self, fov_y):
        angle_a = fov_y/2
        angle_c = 90 - fov_y/2
        side_a = 1.5
        c = (side_a * sin(angle_c))/sin(angle_a)
        return c

    async def start_lookaround(self):
        if self.state == LOOK_AROUND_STATE:
            self.abort_actions(self.tilt_head_action, self.rotate_action, self.drive_action)
            self.look_around_behavior = self.robot.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace)

    async def run(self):
        await self.robot.drive_straight(distance_inches(1), speed_mmps(50), should_play_anim = False).wait_for_completed()
        while True:
            await asyncio.sleep(1)
            print (self.robot.camera.config.fov_y)
            print (self.robot.camera.config.fov_x)
            if self.state == LOOK_AROUND_STATE:
                await self.start_lookaround()



robot: cozmo.robot.Robot

async def cozmo_program(robot):
    maze_runner = MazeRunner(robot)
    display = tk.Tk()
    draw_map = DrawQuad(maze_runner.quad_tree.get_objs(), display)
    await maze_runner.run()


