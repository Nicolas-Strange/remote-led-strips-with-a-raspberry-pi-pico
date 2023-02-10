import random

import utime

from colors import Colors
from neopixel import Neopixel


class LedController:
    """ handle the LED strip programs """
    # GPIO number of the LED strip data
    PIN = 2

    # setup the default brightness (0-255)
    DEFAULT_BRIGHTNESS = 255

    # setup the default color
    DEFAULT_COLOR = "royalblue"

    # setup the default program
    DEFAULT_PROG = "fade_prog"

    # setup the default brightness increment
    BRIGHTNESS_INCR = 25

    def __init__(self, config: dict):
        """
        init function. The config must contain the total number of pixel
        (number of LED on the strip), and the index list (e.g. for 3 pixels the list would be [0, 1, 2])
        """

        self._conf = config
        self._num_pixel = config["num_pixel"]
        self._strip = Neopixel(self._num_pixel, 0, self.PIN, "GRB")
        self._brightness = self.DEFAULT_BRIGHTNESS

        # Init the colors
        self._color_name = self.DEFAULT_COLOR
        self._color_tuple = self._convert_color()

        self._list_color = [p for p in dir(Colors) if "_" not in p]
        self._index_color = self._list_color.index(self._color_name)
        self._max_color_index = len(self._list_color) - 1

        # Init the programs
        self._list_prog = [p for p in dir(self) if p.endswith("_prog")]
        self._current_prog = self.DEFAULT_PROG
        self._index_prog = self._list_prog.index(self._current_prog)
        self._max_prog_index = len(self._list_prog) - 1

        # Init the pixels
        self._pixels = self._conf["all_pixel_list"]
        self._current_args = {"pixels": self._pixels}
        self.state = {}
        self.init_prog = True

    #######################################################
    # Function used to do actions on the LED strip
    # These functions are called to change the LED strip behavior.
    # e.g. change a program, change the color, ...
    #######################################################
    def bright_up(self) -> None:
        """ increase the brightness """
        self._brightness += self.BRIGHTNESS_INCR
        self._brightness = min(255, self._brightness)

    def bright_down(self):
        """ decrease the brightness """
        self._brightness -= self.BRIGHTNESS_INCR
        self._brightness = max(0, self._brightness)

    def change_color_left(self) -> None:
        """ Change the color to the left """
        self._index_color = max(0, self._index_color - 1)
        self._color_name = self._list_color[self._index_color]
        self._color_tuple = self._convert_color()

    def change_color_right(self) -> None:
        """ Change the color to the right """
        self._index_color = min(self._max_color_index, self._index_color + 1)
        self._color_name = self._list_color[self._index_color]
        self._color_tuple = self._convert_color()

    def change_color_rdm(self) -> None:
        """ Change the color to random """
        self._index_color = random.randint(0, self._max_color_index)
        self._color_name = self._list_color[self._index_color]
        self._color_tuple = self._convert_color()

    def change_prog_left(self) -> None:
        """ Change the prog to the left """
        self._index_prog = max(0, self._index_prog - 1)
        self._current_prog = self._list_prog[self._index_prog]

    def change_prog_right(self) -> None:
        """ Change the prog to the right """
        self._index_prog = min(self._max_prog_index, self._index_prog + 1)
        self._current_prog = self._list_prog[self._index_prog]

    def change_prog_rdm(self) -> None:
        """ Change the prog to random """
        self._index_prog = random.randint(0, self._max_prog_index)
        self._current_prog = self._list_prog[self._index_prog]

    #######################################################
    # Function used to do execute a program. Must be called for each iteration
    #######################################################
    def execu(self) -> None:
        """ execute the current program """
        getattr(self, self._current_prog)(**self._current_args)

    #######################################################
    # Programs
    # each program will do a specific action on the LED.
    # e.g. light up all the LED with a specific color, create a rainbow, ...
    # a program function's name must end with '_prog'.
    # each function must be quick to execute. For sequential behavior where the next iteration depends on the
    # previous iteration state, the function must save the parameters in the dictionary self.state.
    # self.init_prog is used to specify the beginning of the iteration or not.
    #######################################################
    def fill_prog(self, **kwargs) -> None:
        """ fill all the LED with a color """
        self._strip.brightness(self._brightness)
        self._strip.fill(self._color_tuple)
        self._strip.show()

    def rainbow_fade_prog(self, pixels: list, hue_offset: int = 4096) -> None:
        """ create a rainbow that is moving """
        if self.init_prog:
            self.state = {"pixels": self._init_pixels(pixels=pixels), "last_hue": 0, "speed": 2000}
            self.init_prog = False

        self._strip.brightness(self._brightness)
        hue = self.state["last_hue"]

        for led in pixels:
            color = self._strip.colorHSV(hue + (led * hue_offset), 255, 255)
            self._strip.set_pixel(led, color)

        self._strip.show()

        self.state["last_hue"] += int(self.state["speed"])

        if self.state["last_hue"] > 65535:
            self.state["last_hue"] = 0

    def fade_prog(self, pixels: list) -> None:
        """ fade on all the LED """
        if self.init_prog:
            self.state = {"pixels": self._init_pixels(pixels=pixels), "last_hue": 0, "speed": 50}
            self.init_prog = False

        self._strip.brightness(self._brightness)
        hue = self.state["last_hue"]

        color = self._strip.colorHSV(hue, 255, 255)
        self._strip.fill(color)

        self._strip.show()

        self.state["last_hue"] += int(self.state["speed"])

        if self.state["last_hue"] > 65535:
            self.state["last_hue"] = 0

    def snake_prog(self, pixels: list, size: int = 20, reverse: bool = False) -> None:
        """ switch on the LED one by one """
        if self.init_prog:
            self.state = {"pixels": self._init_pixels(pixels=pixels), "last_loop": 0, "led_on": [], "speed": 0.01}
            if reverse:
                self.state["pixels"] = self.state[:]
                self.state["pixels"].reverse()

            self.state["led_on"] = []
            self.init_prog = False

        self._strip.brightness(self._brightness)
        led = self.state["pixels"][self.state["last_loop"]]
        self._strip.set_pixel(led, self._color_tuple)
        self.state["led_on"].append(led)

        if len(self.state["led_on"]) > size:
            self._strip.set_pixel(self.state["led_on"][0], [0, 0, 0])

        self.state["led_on"] = self.state["led_on"][-size:]

        self._strip.show()
        utime.sleep(self.state["speed"])

        self.state["last_loop"] += 1
        if self.state["last_loop"] >= len(self.state["pixels"]):
            self.state["last_loop"] = 0

    #######################################################
    # Tools
    #######################################################
    def _init_pixels(self, pixels: list) -> list:
        """ init the pixels """
        pixels = self._squeeze(pixels)
        self._strip.brightness(self._brightness)

        return pixels

    def _convert_color(self) -> tuple:
        """ convert the color name to RGB tuple """
        return getattr(Colors, self._color_name)

    @staticmethod
    def _squeeze(pixels: list) -> list:
        """ squeeze a list """
        if isinstance(pixels[0], list):
            return [item for sublist in pixels for item in sublist]

        return pixels
