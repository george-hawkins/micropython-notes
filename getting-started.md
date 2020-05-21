Getting started with MicroPython on an ESP32 board
==================================================

This page covers installing [MicroPython](https://www.micropython.org/) on an ESP32 board, getting familiar with MicroPython. The board used was an [Adafruit HUZZAH32](https://www.adafruit.com/product/3405) but the steps described are applicable for any board.

I've written a similar [page](esp32-devkitc-vb) for the Espressif ESP32 DevKitC board. I wrote this page here when I was new to MicroPython, so it has more notes made as I discovered things, while the ESP32 DevKitC page is more a straight walk-thru with less explanation.

Installing MicroPython
----------------------

The following is just a condensed form of the MicroPython ESP32 [introduction](https://docs.micropython.org/en/latest/esp32/tutorial/intro.html).

### Choosing the firmware

Go to the MicroPython [ESP32 firmware downloads](https://micropython.org/download/esp32) and select the **GENERIC** firmware for ESP-IDF v4.x, i.e. the ESP32 firmware for boards, like the HUZZAH32, that have no external SPI RAM.

**Important:** I initially used the **GENERIC-SPIRAM** firmware, which is intended for boards that 4MB of external pSRAM. The Adafruit [product page](https://www.adafruit.com/product/3405) notes that the board has "4 MB of SPI Flash", however pSRAM is something different (as explained [here](https://docs.espressif.com/projects/esp-idf/en/latest/api-guides/external-ram.html#hardware)). If you use the GENERIC-SPIRAM firmware, it still works fine but you see these errors in the boot sequence:

    E (593) spiram: SPI RAM enabled but initialization failed. Bailing out.
    E (10) spiram: SPI RAM not initialized

I chose the latest non-nightly firmware. Nightlies have the same name as the latest stable release but with `unstable` before the version and something like `-167-gf020eac6a` after (the bit after the `-g` is the git hash of the revison that was built, i.e. `f020eac6a` in the example just given).

Note: ESP32 MicroPython versions are built on top of the Espressif IoT Development Framework (ESP-IDF), if you're interested in knowing more about the ESP-IDF, see my notes [here](https://github.com/george-hawkins/snippets/blob/master/esp-idf.md).

### Installing `esptool.py`

The firmware is flashed to your board using a tool from Espressif called [`esptool.py`](https://github.com/espressif/esptool).

If you haven't already got Python 3 installed on your local system, see my [notes](https://github.com/george-hawkins/snippets/blob/master/install-python.md) on installing it.

Before you can install `esptool.py` you need to create a [Python venv](https://docs.python.org/3/tutorial/venv.html).

    $ python3 -m venv env
    $ source env/bin/activate
    $ pip install --upgrade pip

This creates a directory called `env` in your current directory (you typically create one such environment in the base directory of any new Python related project that you start). You'll need to repeat just the `source` step in future, to activate the environment, whenever you start a new terminal session.

Note: many guides avoid a venv, but while venvs introduce a little extra setup, they save you a lot of trouble in the long run.

Now we can install `esptool.py`:

    $ pip install esptool

### Flashing the firmware

Now we're almost ready to plug in the board but before we can do that it may be necessary to install a driver for the board's USB to UART bridge - see [here](https://github.com/george-hawkins/snippets/blob/master/esp-usb-to-uart.md) for more details.

Once that's done and the board is plugged in, the serial port, that corresponds to the board, needs to be determined. On Mac the port is usually `/dev/cu.SLAB_USBtoUART` and on Linux it's usually `/dev/ttyUSB0`.

Note: when connected via USB, the yellow CHG LED on the Adafruit HUZZAH32 board flickers incessantly (if no battery is connected). This is apparently normal, see the end of the "[Battery + USB power](https://learn.adafruit.com/adafruit-huzzah32-esp32-feather?view=all#battery-plus-usb-power-4-2)" section of the Adafruit guide.

Now we can flash the downloaded firmware to the board:

    $ PORT=/dev/cu.SLAB_USBtoUART
    $ FIRMWARE=~/Downloads/esp32-idf4-20191220-v1.12.bin
    $ esptool.py --port $PORT erase_flash
    $ esptool.py --port $PORT write_flash -z 0x1000 $FIRMWARE

Adjust the `PORT` and `FIRMWARE` values to match the port for your system and the firmware you downloaded.

Note: many examples includes the additional argument `--chip esp32`, however `esptool.py` now automatically detects the chip version.

Working with the REPL
---------------------

Once uploaded you can connect to the MicroPython REPL:

    $ screen $PORT 115200

Note: `screen` behaves differently on Mac and Linux. On Mac quiting requires pressing `ctrl-a` and then `ctrl-\`, while on Linux it requires `ctrl-a` and then just `\`.

Just press return to get a prompt and then enter `help()`:

    >>> help()
    Welcome to MicroPython on the ESP32!
    ...
    For access to the hardware use the 'machine' module:
    ...
    import machine
    pin12 = machine.Pin(12, machine.Pin.OUT)
    ...
    Basic WiFi configuration:
    ...
    import network
    sta_if = network.WLAN(network.STA_IF);
    ...

Then press the reset button on the board - you'll see a boot sequence:

    I (519) cpu_start: Pro cpu up.
    I (519) cpu_start: Application information:
    I (519) cpu_start: Compile time:     Dec 20 2019 07:56:38
    I (522) cpu_start: ELF file SHA256:  0000000000000000...
    I (528) cpu_start: ESP-IDF:          v4.0-beta1
    I (533) cpu_start: Starting app cpu, entry point is 0x40083014
    I (526) cpu_start: App cpu up.

You can confirm that it's found the 4MB of flash RAM:

    >>> import esp
    >>> esp.flash_size()
    4194304

The flash is assigned to a virtual filesystem, while the onboard RAM is split between heap (managed by the GC) and stack - as can be seen by trying out the following:

    >>> import os
    >>> os.statvfs('/')
    (4096, 4096, 506, 505, 505, 0, 0, 0, 0, 255)
    >>> import micropython
    >>> micropython.mem_info()
    stack: 736 out of 15360
    GC: total: 111168, used: 104224, free: 6944
     No. of 1-blocks: 2172, 2-blocks: 381, max blk sz: 264, max free sz: 196
    >>> import gc
    >>> gc.collect()
    >>> micropython.mem_info()
    stack: 736 out of 15360
    GC: total: 111168, used: 83200, free: 27968
     No. of 1-blocks: 1175, 2-blocks: 226, max blk sz: 264, max free sz: 119

You can take a look at the filesystem like so:

    >>> import os
    >>> os.listdir('/')
    ['boot.py']
    >>> f = open('boot.py')
    >>> f.read()
    '# This file is executed on every boot ...'
    >>> f.close()

So a newly flashed board just contains a single file, called `boot.py`, in its root directory.

You can discover more about the available modules, using `help` and `dir`, like so:

    >>> help("modules")
    __main__          gc                uctypes           urequests
    ...
    framebuf          ucryptolib        ure
    Plus any modules on the filesystem
    >>> import machine
    >>> dir(machine)
    [... 'DEEPSLEEP', 'DEEPSLEEP_RESET', ..., 'sleep', 'time_pulse_us', 'unique_id', 'wake_reason']

Note: a lot of the modules have names like `uos`, `uio` etc., i.e. names that start with `u`. The `u` indicates a micro version of a standard Python module. You should drop the `u` when importing such modules, e.g. `import os`, i.e. use the standard module name (although it doesn't do any harm not to). For more, see [this post](https://forum.micropython.org/viewtopic.php?p=40415#p40415) on the MicroPython forums.

Paste mode
----------

The REPL supports auto-indent which is useful when entering larger pieces of code, however if you're copying and pasting in an already properly indented piece of code, the auto-indent feature will end up over indenting everything. To deal with this you need to use the REPL's [paste mode](http://docs.micropython.org/en/latest/esp8266/tutorial/repl.html#paste-mode) - just press `ctrl-E` to enter paste mode, then paste in the required text and press `ctrl-D` to exit paste mode.

Turning an LED of and off
-------------------------

Once you've had a look around, try turning on the red LED that's next to the USB port on the HUZZAH32 board and connected to GPIO #13:

    >>> import machine
    >>> pin13 = machine.Pin(13, machine.Pin.OUT)
    >>> pin13.value(1)

And then turn it off:

    >>> pin13.value(0)

For an example using an external LED (with a different ESP32 board but also using pin 13) see [here](esp32-devkitc-vb#example-circuit).

Tools
-----

Eventually, you'll want to copy files from your local system to your ESP32 board - for more on tools for doing this and on tools that make it easier to work with the REPL see [`tools-filesystem-and-repl.md`](tools-filesystem-and-repl.md).

Documentation and tutorial
--------------------------

You can find the documentation for the standard libraries and the MicroPython-specific libraries [here](https://docs.micropython.org/en/latest/library/index.html#python-standard-libraries-and-micro-libraries).

Once you're ready, you can work through the MicroPython tutorial for the [ESP8266](https://docs.micropython.org/en/latest/esp8266/tutorial/repl.html) (there's no separate version for the ESP32 and the two are identical for things covered here). And after that you can return to the ESP32 specific [quick reference](http://docs.micropython.org/en/latest/esp32/quickref.html).
