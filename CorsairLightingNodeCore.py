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
        self._color_frame = [0] * 64
        self._color_frame[0] = 0x32
        self._color_frame[3] = 0x18

        if (fan_count < 0 or fan_count > 6):
            raise Error(f"fan_count should be an integer between 0 and 6, found: {fan_count}")

        if (led_per_fan < 0 or led_per_fan > 8):
            raise Error(f"led_per_fan should be an integer between 0 and 8, found: {led_per_fan}")

        self.fan_count = fan_count
        self.led_per_fan = led_per_fan

        if product_id is None:
            self._device = usb.core.find(idVendor=vendor_id)
        else:
            self._device = usb.core.find(idVendor=vendor_id, idProduct=product_id)

        # was it found?
        if self._device is None:
            raise Error('Could not find Corsair Lighting Node CORE')

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
            raise Error("Corsair output node not found")

    def _send_magic_frames(self):
        for frame in MAGIC_FRAMES:
            r = self._endpoint.write(frame, TIMEOUT)
            assert r == 64

    def _check_fan(self, fan: int):
        if (fan < 0 or fan >= self.fan_count):
            raise Error(f"fan should be an integer between 0 and {self.fan_count}, found: {fan}")

    def _check_led(self, led: int):
        if (led < 0 or led >= self.led_per_fan):
            raise Error(f"led should be an integer between 0 and {self.led_per_fan}, found: {led}")
    
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
        self._send_magic_frames()
        for c in range(3):
            self._color_frame[4] = c
            self._color_frame[(fan * self.led_per_fan) + led + 5] = rgb[c]
            r = self._endpoint.write(bytes(bytearray(self._color_frame)), TIMEOUT)
            assert r == 64

    def set_fan(self, fan: int, rgb: tuple[int]):
        self._check_fan(fan)
        self._send_magic_frames()
        for c in range(3):
            self._color_frame[4] = c
            for l in range(self.led_per_fan):
                self._color_frame[(fan * self.led_per_fan) + l + 5] = rgb[c]
                r = self._endpoint.write(bytes(bytearray(self._color_frame)), TIMEOUT)
                assert r == 64

    def set_all(self, rgb: tuple[int]):
        self._send_magic_frames()
        for c in range(3):
            self._color_frame[4] = c
            for f in range(self.fan_count):
                for l in range(self.led_per_fan):
                    self._color_frame[(f * self.led_per_fan) + l + 5] = rgb[c]
                    r = self._endpoint.write(bytes(bytearray(self._color_frame)), TIMEOUT)
                    assert r == 64
