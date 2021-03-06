import usb.core
import usb.util

MAGIC_FRAME_1 = b'\x33\xff' + b'\x00' * 62
MAGIC_FRAME_2 = b'\x38\x01\x02' + b'\x00' * 61
MAGIC_FRAME_3 = b'\x34\x01' + b'\x00' * 62
MAGIC_FRAME_4 = b'\x38\x00\x02' + b'\x00' * 61
MAGIC_FRAMES = (MAGIC_FRAME_1, MAGIC_FRAME_2, MAGIC_FRAME_3, MAGIC_FRAME_1, MAGIC_FRAME_4)

TIMEOUT = 5000

class CorsairLightingNodeCore:

    def __init__(self, fan_count: int, led_per_fan: int, vendor_id: int, product_id: int = None):
        color_frame_1 = [0] * 64
        color_frame_1[0] = 0x32
        color_frame_1[3] = 0x18
        color_frame_1[4] = 0
        color_frame_2 = [0] * 64
        color_frame_2[0] = 0x32
        color_frame_2[3] = 0x18
        color_frame_2[4] = 1
        color_frame_3 = [0] * 64
        color_frame_3[0] = 0x32
        color_frame_3[3] = 0x18
        color_frame_3[4] = 2
        self._color_frame = (color_frame_1, color_frame_2, color_frame_3)

        if (fan_count < 0 or fan_count > 6):
            raise ValueError(f'fan_count should be an integer between 0 and 6, found: {fan_count}')

        if (led_per_fan < 0 or led_per_fan > 8):
            raise ValueError(f'led_per_fan should be an integer between 0 and 8, found: {led_per_fan}')

        self.fan_count = fan_count
        self.led_per_fan = led_per_fan

        if product_id is None:
            self._device = usb.core.find(idVendor=vendor_id)
        else:
            self._device = usb.core.find(idVendor=vendor_id, idProduct=product_id)

        # was it found?
        if self._device is None:
            raise ConnectionError('Could not find Corsair Lighting Node CORE')

        # print(self._device)

        # detach kernel drivers, otherwise we get a resource busy error
        if self._device.is_kernel_driver_active(0):
            print('Kernel driver is attached. Detach it')
            self._device.detach_kernel_driver(0)
        else:
            print('Kernel driver is not attached. Continue without detaching')
        
        # set the active configuration. With no arguments, the first
        # configuration will be the active one
        self._device.set_configuration()

        # get an endpoint instance
        config = self._device.get_active_configuration()
        #print(config)
        interface = config[(0,0)]
        #print(interface)

        self._endpoint = usb.util.find_descriptor(
            interface,
            # match the first OUT endpoint
            custom_match = \
            lambda e: \
                usb.util.endpoint_direction(e.bEndpointAddress) == \
                usb.util.ENDPOINT_OUT)

        #print(self._endpoint)

        if self._endpoint:
            print("Corsair output node found")
        else:
            raise ConnectionError("Corsair output node not found")

    def _send_magic_frames(self):
        for frame in MAGIC_FRAMES:
            r = self._endpoint.write(frame, TIMEOUT)
            assert r == 64

    def _check_fan(self, fan: int):
        if (fan < 0 or fan >= self.fan_count):
            raise IndexError(f'fan should be an integer between 0 and {self.fan_count}, found: {fan}')

    def _check_led(self, led: int):
        if (led < 0 or led >= self.led_per_fan):
            raise IndexError(f'led should be an integer between 0 and {self.led_per_fan}, found: {led}')
    
    def destroy(self):
        if not self._device.is_kernel_driver_active(0):
            print('Kernel driver is detached. Trying to reattach it')
            try:
                self._device.attach_kernel_driver(0)
            except usb.core.USBError as e:
                print(f'Could not reattach kernel driver: {e}')

    def set_led(self, fan: int, led: int, rgb: tuple[int]):
        self._check_fan(fan)
        self._check_led(led)
        for c in range(3):
            self._color_frame[c][(fan * self.led_per_fan) + led + 5] = rgb[c]

    def set_leds(self, led: int, rgb: tuple[int]):
        self._check_led(led)
        for c in range(3):
            for f in range(self.fan_count):
                self._color_frame[c][(f * self.led_per_fan) + led + 5] = rgb[c]

    def set_fan(self, fan: int, rgb: tuple[int]):
        self._check_fan(fan)
        for c in range(3):
            for l in range(self.led_per_fan):
                self._color_frame[c][(fan * self.led_per_fan) + l + 5] = rgb[c]

    def set_all(self, rgb: tuple[int]):
        for c in range(3):
            for f in range(self.fan_count):
                for l in range(self.led_per_fan):
                    self._color_frame[c][(f * self.led_per_fan) + l + 5] = rgb[c]

    def push(self):
        self._send_magic_frames()
        for c in range(3):
            r = self._endpoint.write(bytes(bytearray(self._color_frame[c])), TIMEOUT)
            assert r == 64