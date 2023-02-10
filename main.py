import json

from bluetooth_controler import BluetoothController
from led_controler import LedController


class Main:
    """ main class that will handle the bluetooth messages and the LED programs to be executed """

    # Name of the config file to be used
    CONFIG_NAME = "desk"

    # Define the different bluetooth messages mapping
    _BRIGHT_UP = b'bright_up'
    _BRIGHT_DOWN = b'bright_down'
    _CHANGE_PROG_LEFT = b'prog_left'
    _CHANGE_PROG_RIGHT = b'prog_right'
    _SPEED_UP = b'speed_up'
    _SPEED_DOWN = b'speed_down'
    _CHANGE_COLOR_LEFT = b'color_left'
    _CHANGE_COLOR_RIGHT = b'color_right'
    _CHANGE_COLOR_RDM = b'rdm_color'

    _DEFAULT_COLOR = (0, 0, 255)

    def __init__(self):
        """
        init function
        The config file must be in a directory `config`
        """
        with open(f"./config/{self.CONFIG_NAME}.json") as infile:
            self._conf = json.load(infile)

        self._conf_converter()

        # Instantiate the Classes
        self._bluet = BluetoothController()
        self._led_controller = LedController(config=self._conf)

    def _conf_converter(self) -> None:
        """
        convert the LED list to provide the full list of pixel coordinates and add the total number
        of pixel to the config
        """
        num_pixel = 0
        i = 0
        for name, num_in_strip in self._conf["led_list"].items():
            self._conf["led_list"][name] = list(range(num_pixel, num_in_strip + num_pixel))
            num_pixel += num_in_strip
            i += 1
        self._conf["num_pixel"] = num_pixel
        self._conf["all_pixel_list"] = list(range(num_pixel))

    def run(self) -> None:
        """
        core function to iterate
        For each iteration the Bluetooth message is checked to change or not the different programs or
        conditions of the LED strip.
        """

        while True:
            # Receive the Bluetooth message
            value_received = self._bluet.read()

            # Change the LED programs or conditions accordingly
            if value_received == self._BRIGHT_UP:
                self._led_controller.bright_up()
            elif value_received == self._BRIGHT_DOWN:
                self._led_controller.bright_down()
            elif value_received == self._CHANGE_PROG_LEFT:
                self._led_controller.init_prog = True
                self._led_controller.change_prog_left()
            elif value_received == self._CHANGE_PROG_RIGHT:
                self._led_controller.init_prog = True
                self._led_controller.change_prog_right()
            elif value_received == self._SPEED_UP:
                self._led_controller.state["speed"] = self._led_controller.state.get("speed", 0) * 0.9
            elif value_received == self._SPEED_DOWN:
                self._led_controller.state["speed"] = self._led_controller.state.get("speed", 0) * 1.1
            elif value_received == self._CHANGE_COLOR_LEFT:
                self._led_controller.change_color_left()
            elif value_received == self._CHANGE_COLOR_RIGHT:
                self._led_controller.change_color_right()
            elif value_received == self._CHANGE_COLOR_RDM:
                self._led_controller.change_prog_rdm()

            # execute the iteration
            self._led_controller.execu()


if __name__ == '__main__':
    run = Main()
    run.run()
