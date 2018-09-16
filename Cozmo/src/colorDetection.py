'''
File intended to read in and assign a color to Cozmo's surroundings.
Slight modification of the pre-packaged app in the sdk example set provided by Anki.
'''
# Auth: Keon Williams
# Version: No. 1
# ColorDetection

'''Edit comments: None'''

import numpy
import sys

import cozmo

from cozmo.util import Vector2
try:
    from PIL import Image, ImageDraw, ImageStat
except ImportError:
    sys.exit('Cannot import from PIL: D `pip3 install --user Pillow` to install')

ENABLE_COLOR_BALANCING = True

hsv_color_ranges = {
'red' : (-20.0, 20.0, 0.5, 1.0, 0.5, 1.0), 
'green' : (90.0, 155.0, 0.5, 1.0, 0.5, 1.0), 
'blue' : (180.0, 245.0, 0.5, 1.0, 0.5, 1.0), 
'yellow' : (40.0, 80.0, 0.5, 1.0, 0.5, 1.0), 
'white' : (0.0, 360.0, 0.0, 0.2, 0.9, 1.0), 
'black' : (0.0, 360.0, 0.0, 0.1, 0.0, 0.2)
}

def hsv_color_distance_sqr(color, color_range):
    h, s, v = color
    minH, maxH, minS, maxS, minV, maxV = color_range
    h_dist_sqr = 0
    s_dist_sqr = 0
    v_dist_sqr = 0
    if h < minH:
        h_dist_sqr = (minH - h) ** 2
    elif h > maxH:
        h_dist_sqr = (maxH - h) ** 2
    if s < minS:
        s_dist_sqr = (minS - s) ** 2
    elif s > maxS:
        s_dist_sqr = (maxS - s) ** 2
    if v < minV:
        v_dist_sqr = (minV - v) ** 2
    elif v > maxV:
        v_dist_sqr = (maxV - v) ** 2
    sum_dist_sqr = h_dist_sqr + s_dist_sqr + v_dist_sqr
    return sum_dist_sqr

def color_balance(image):
    image_array = image_to_array(image)
    image_array = image_array.transpose(2, 0, 1).astype(numpy.uint32)
    average_g = numpy.average(image_array[1])
    image_array[0] = numpy.minimum(image_array[0] * (average_g / numpy.average(image_array[0])), 255)
    image_array[2] = numpy.minimum(image_array[2] * (average_g / numpy.average(image_array[2])), 255)
    return array_to_image(image_array.transpose(1, 2, 0).astype(numpy.uint8))

def image_to_array(image):
    image_array = numpy.asarray(image)
    image_array.flags.writeable = True
    return image_array

def array_to_image(image_array):
    return Image.fromarray(numpy.uint8(image_array))

def rgb_to_hsv(r, g, b):
    r_normalized = r / 255.0
    g_normalized = g / 255.0
    b_normalized = b / 255.0
    max_normalized_val = max(r_normalized, g_normalized, b_normalized)
    min_normalized_val = min(r_normalized, g_normalized, b_normalized)
    delta = max_normalized_val - min_normalized_val

    h = 0
    s = 0
    v = max_normalized_val

    if delta != 0:
        if max_normalized_val == r_normalized:
            h = 60.0 * ((g_normalized - b_normalized) / delta)
        elif max_normalized_val == g_normalized:
            h = 60.0 * (((b_normalized - r_normalized) / delta) + 2)
        else:
            h = 60.0 * (((r_normalized - g_normalized) / delta) + 4)
        if h < 0:
            h += 360

        if max_normalized_val == 0:
            s = 0
        else:
            s = delta / max_normalized_val
    return (h, s, v)

DOWNSIZE_WIDTH = 32
DOWNSIZE_HEIGHT = 24

ANNOTATOR_WIDTH = 640.0
ANNOTATOR_HEIGHT = 480.0

class ColorDetection (cozmo.annotate.Annotator):

    def __init__(self, robot: cozmo.robot.Robot):
        self.robot = robot
        self.fov_x  = self.robot.camera.config.fov_x
        self.fov_y = self.robot.camera.config.fov_y
        self.robot.add_event_handler(cozmo.objects.EvtObjectTapped, self.on_cube_tap)
        self.robot.add_event_handler(cozmo.world.EvtNewCameraImage, self.on_new_camera_image)
        
        self.grid_cube = None # type: LightCube
        self.robot.world.image_annotator.add_annotator('colorDetection', self)
        self.robot.world.image_annotator.annotation_enabled = False
        self.enabled = True
        self.pixel_matrix = Matrix(DOWNSIZE_WIDTH, DOWNSIZE_HEIGHT)

    def apply(self, image, scale):
        d = ImageDraw.Draw(image)
        WM = ANNOTATOR_WIDTH/DOWNSIZE_WIDTH
        HM = ANNOTATOR_HEIGHT/DOWNSIZE_HEIGHT

        for i in range(DOWNSIZE_WIDTH):
            for j in range(DOWNSIZE_HEIGHT):
                pt1 = Vector2(i * WM, j * HM)
                pt2 = Vector2(i * WM, (j + 1) * HM)
                pt3 = Vector2((i + 1) * WM, (j + 1) * HM)
                pt4 = Vector2((i + 1) * WM, j * HM)
                points_seq = (pt1, pt2, pt3, pt4)
                cozmo.annotate.add_polygon_to_image(image, points_seq, 1.0, 'green', self.pixel_matrix.at(i, j).value)
                
        text = cozmo.annotate.ImageText('Looking for {}'.format(self.color_to_find), color = 'white')
        text.render(d, (0, 0, image.width, image.height))

    
    def on_new_camera_image(self, evt, **kwargs):
        downsized_image = self.get_low_res_view()
        if ENABLE_COLOR_BALANCING:
            downsized_image = color_balance(downsized_image)
        self.update_pixel_matrix(downsized_image)

    def on_cube_tap(self, evt, obj, **kwargs):
        if obj.object_id == self.grid_cube.object_id:
            self.robot.world.image_annotator.annotation_enabled = not self.robot.world.image_annotator.annotation_enabled

    def turn_on_cubes(self):
        self.grid_cube.set_lights(cozmo.lights.white_light.flash())

    def cubes_connected(self):
        self.grid_cube = self.robot.world.get_light_cube(cozmo.objects.LightCube1Id)
        return not (self.grid_cube == None)

    def white_balance(self):
        image  = self.robot.world.latest_image.raw_image
        self.adjustment = ImageStat.Stat(image).mean

    def update_pixel_matrix(self, downsized_image):
        for i in range(self.pixel_matrix.num_cols):
            for j in range(self.pixel_matrix.num_rows):
                r, g, b = downsized_image.getpixel((i, j))
                self.pixel_matrix.at(i, j).set(self.approximate_color_of_pixel(r, g, b))
        self.pixel_matrix.fill_gaps()

    def approximate_color_of_pixel(self, r, g, b):
        min_distance = sys.maxsize
        closest_color = ''
        h, s, v = rgb_to_hsv(r, g, b)
        if h > 340.0:
            h -= 360.0
        for color_name, color_range in hsv_color_ranges.items():
            d = hsv_color_distance_sqr((h, s, v), color_range)
            if d < min_distance:
                min_distance = d
                closest_color = color_name
        return closest_color

    def get_low_res_view(self):
        image = self.robot.world.latest_image.raw_image
        downsized_image = image.resize((DOWNSIZE_WIDTH, DOWNSIZE_HEIGHT), resample = Image.LANCZOS)
        return downsized_image



class Matrix():
    def __init__(self, num_cols, num_rows):
        self.num_cols = num_cols
        self.num_rows = num_rows
        self._matrix = [[MatrixValueContainer() for _ in range(self.num_rows)] for _ in range(self.num_cols)]
        self.size = self.num_cols * self.num_rows

    def at(self, i, j):
        return self._matrix[i][j]

    def fill_gaps(self):
        for i in range(self.num_cols):
            for j in range(self.num_rows):
                val = self.surrounded(i, j)
                if val != None and val != 'white' and val != 'black':
                    self.at(i, j).set(val)

    def surrounded(self, i, j):
        if i != 0 and i != self.num_cols-1 and j != 0 and j != self.num_rows-1:
            left_value, up_value, right_value, down_value = self.get_neighboring_values(i, j)
            if left_value == up_value and left_value == right_value:
                return left_value
            if left_value == up_value and left_value == down_value:
                return left_value
            if left_value == right_value and left_value == down_value:
                return left_value
            if right_value == up_value and right_value == down_value:
                return right_value
        return None

    def get_neighboring_values(self, i, j):
        return (self.at(i-1, j), self.at(i, j-1), self.at(i + 1, j), self.at(i, j + 1))


class MatrixValueContainer():
    def __init__(self):
        self.value = None

    def set(self, new_value):
        self.value = new_value
