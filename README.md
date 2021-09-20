# Description

Corsair Lighting Node CORE is a simple python library for controlling RGB fans via [iCUE Lighting Node CORE Digital Fan RGB Lighting Controller](https://www.corsair.com/us/en/Categories/Products/Accessories-%7C-Parts/iCUE-CONTROLLERS/iCUE-Lighting-Node-CORE-Digital-Fan-RGB-Lighting-Controller/p/CL-8930009).


# Platforms

 - Linux

# Dependencies


 - [pyUSB](https://pyusb.github.io/pyusb/)

The code will have to be run as root so you'll have to install pyUSB globally using `sudo`

    $ sudo pip install pyusb

# Usage

First copy the file `CorsairLightingNodeCore.py` in the same directory as your script.

## Create an instance of the class CorsairLightingNodeCore.

    from CorsairLightingNodeCore import CorsairLightingNodeCore

    corsair = CorsairLightingNodeCore(3, 8, 0x1b1c)

The first parameter in the constructor is an integer between 1 and 6 and it is the number of fans connected to the controller. In this case I have 3 fans. The second parameters is an integer between 1 and 8 and is the number of LEDs in each fan. In my case I have 8 LEDs per fan.

`0x1b1c` is the `vendorId` for Corsair. If you have multiple USB devices from Corsair connected to your system you'll need to provide the `productId`. Both `vendorId` and `productId` can be found using the command `lsusb`.

    $ lsusb
    Bus 006 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
    Bus 005 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
    Bus 004 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
    ...
    Bus 001 Device 005: ID 1b1c:0c1a Corsair CORSAIR Lighting Node CORE
    ...

In this case my Corsair Lighting Node has the identifiers `1b1c:0c1a`, meaning `0x1b1c` is the `vendorId` and `0x0c1a` is the `productId`.

If I had multiple devices with the same `vendorId` I would have to specify the `productId` in the constructor like this:


    from CorsairLightingNodeCore import CorsairLightingNodeCore

    corsair = CorsairLightingNodeCore(3, 8, 0x1b1c, 0x0c1a)

 > If you only have one Corsair USB device connected, it is better to omit the `productId`. I noticed that the `productId` is not stable and it can change when you mess with kernel drivers.

## Set colors

Once you created the object, you have now access to three methods to set the RGB colors.

 - `set_all(rgb: tuple[int])`
 - `set_fan(fan: int, rgb: tuple[int])`
 - `set_led(fan: int, led: int, rgb: tuple[int])`
 - `set_leds(led: int, rgb: tuple[int])`
 - `push()`

### Example

    from CorsairLightingNodeCore import CorsairLightingNodeCore

    corsair = CorsairLightingNodeCore(3, 8, 0x1b1c)

    # first we prepare the color frame

    # set all fans to purple (My favorite color btw)
    corsair.set_all(0, 0, (0xff, 0x00, 0xff))
    # set second fan to green
    corsair.set_fan(1, (0x00, 0xff, 0x00))
    # set first led on first fan to red
    corsair.set_led(0, 0, (0xff, 0x00, 0x00))
    # set the fourth led in all fans to blue
    corsair.set_leds(3, (0x00, 0x00, 0xff))

    # push the color frame
    corsair.push()

<div class="warning" style='padding:0.1em; background-color:#E9D8FD; color:#69337A; text-align:center; font-size: medium;'>
<span>
<p style='margin-top:1em;'>
<b>WARNING</b></p>
<p style='margin-left:1em;'>
The code absolutely needs to run as root
</p>
</div>


# Credits

This project is based on [Chlorek](https://github.com/Chlorek)'s work on [Colorsair](https://github.com/Chlorek/Colorsair). Many thanks to him for his hard work on reverse engineering the USB protocol.

# Licensing

GNU GPL v2

See [LICENSE](https://github.com/aakodadi/CorsairLightingNodeCore/blob/main/LICENSE)