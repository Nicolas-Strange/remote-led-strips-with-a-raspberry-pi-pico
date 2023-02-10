from machine import UART


class BluetoothController:
    """ class to handle the bluetooth message """
    # GPIO number of the TXD
    PIN_TXD = 0
    # GPIO number of the RXD
    PIN_RXD = 1

    def __init__(self):
        """ init function """
        self._uart = UART(0, 9600)

    def read(self):
        """
        Read the entire Bluetooth message when the start condition is detected and until the stop condition.
        a Bluetooth message is 1 character long. To read longer messages we have arbitrarily defined a start character
        and a stop character (e.g. ^message?).
        """
        first_value = self._uart.read(1)

        # check the start condition
        if first_value != b"^":
            return

        last_value = first_value
        sequence = b""

        # read the signal while the stop condition is not detected
        while last_value != b"?":
            new_value = self._uart.read(1)

            if new_value != b"?" and new_value is not None:
                sequence += new_value

            last_value = new_value

        return sequence

