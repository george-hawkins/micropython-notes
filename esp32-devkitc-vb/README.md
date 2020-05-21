Setting up MicroPython on the ESP32 DevKitC VB
==============================================

Most ESP32 development boards feature the basic WROOM module, which has 4MiB of flash but just 520KiB of SRAM - which can be a little tight when running more substantial MicroPython programs. However, an alternative to the WROOM module is the WROVER module which has an extra 4MiB of SRAM.

Espressif produce a board, featuring this module, that's called the ESP32 DevKitC **VB** and is available from:

* [Mouser](https://www.mouser.com/ProductDetail/356-ESP32-DEVKITC-VB) for US$10.
* [Banggood](https://www.banggood.com/ESP32-DevkitC-Core-Board-ESP32-Development-Board-ESP32-WROOM-32U32D-F-VB-VIB-S1-p-1426780.html?ID=566841) for US$18

Note: the Banggood price includes shipping while the Mouser price does not (though Mouser do provide free shipping on orders over a certain size).

The following short guide covers getting MicroPython set up on the board and using it to blink an LED on and off as a simple example.

Note: I wrote this page once I'd gotten used to MicroPython. I also wrote a similar [page](../getting-started.md) when installing MicroPython for the first time (on an [Adafruit HUZZAH32 board](https://www.adafruit.com/product/3405) that just has a WROVER module). That page covers most of the same details but includes more notes, so it may be more helpful if you find anything here unclear.

Setup
-----

If you haven't already got Python 3 installed on your local system, see my [notes](https://github.com/george-hawkins/snippets/blob/master/install-python.md) on installing it.

Create a new directory for your project, then create and set up a standard Python venv:

    $ mkdir esp32-devkitc-vb
    $ cd esp32-devkitc-vb
    $ python3 -m venv env
    $ source env/bin/activate
    $ pip install --upgrade pip

Note: you just need to repeat the `source` step, whenever you open a new terminal session, in order to activate the venv.

Install the Espressif [`esptool`](https://github.com/espressif/esptool):

    $ pip install esptool

Go to the MicroPython [ESP32 firmware downloads](https://micropython.org/download/esp32/), if there are firmwares listed for multiple ESP-IDF versions then go to the section for the latest version (4.x at the time of writing) and then chose the GENERIC-SPIRAM firmare in this section for the latest MicroPython version (1.12 at the time of writing).

There are two kinds of versions, e.g.:

* GENERIC-SPIRAM : esp32spiram-idf3-20200517-unstable-v1.12-464-gcae77daf0.bin
* GENERIC-SPIRAM : esp32spiram-idf4-20191220-v1.12.bin

The one ending in `v1.12.bin` is the latest stable build, while the one ending in `v1.12-464-gcae77daf0.bin` is a nightly build and includes commits made since the last stable release (the bit after the `-g` is the hash of the revision that was built). Usually it's best to go with the latest _stable_ build.

Notes:

* The plain GENERIC firmwares are for boards that just have the WROOM module while the GENERIC-SPIRAM firmwares are for boards that have the WROVER module with the addition 4MiB of SRAM.
* ESP32 MicroPython versions are built on top of the Espressif IoT Development Framework (ESP-IDF), if you're interested in knowing more about the ESP-IDF, see my notes [here](https://github.com/george-hawkins/snippets/blob/master/esp-idf.md).

Once you've downloaded the firmware, connect you board via USB and determine the serial device that corresponds to your board, typically this is `/dev/cu.SLAB_USBtoUART` on Mac and `/dev/ttyUSB0` on Linux.

Note: on Mac you will probably have to install a device driver for the CP2104 USB-to-UART bridge controller that the board uses - see [here](https://github.com/george-hawkins/snippets/blob/master/esp-usb-to-uart.md) for more details.

Now you can write the firmware to the board:

    $ FIRMWARE=~/Downloads/esp32spiram-idf4-20191220-v1.12.bin
    $ PORT=/dev/ttyUSB0
    $ esptool.py --port $PORT erase_flash
    $ esptool.py --port $PORT write_flash -z 0x1000 $FIRMWARE

Adjust `FIRMWARE` and `PORT` to match the name of the firmware you downloaded and the port for your system.

Once that's done, install [`rshell`](https://github.com/dhylands/rshell) so you can interact with MicroPython:

    $ pip install rshell

Then connect to the board like so:

    $ rshell --buffer-size 512 --quiet -p $PORT
    > help
    ...

For more on tools like `rshell` see [here](../tools-filesystem-and-repl.md).

Button press example
--------------------

The board has two buttons - one called **EN**, that causes the board to do a hard reset, and the other called **BOOT**, that causes the board to enter a firmware download mode if held down while you press the EN button.

The BOOT button only has special behavior when used in combination with EN. When the board is running, it's just a normal button connected to GPIO pin 0. So you can use it for a simple MicroPython example program.

So assuming `rshell` is started, just use the `repl` command to access the MicroPython REPL:

    > repl
    Entering REPL. Use Control-X to exit.
    >>>

The REPL supports auto-ident - this works well when you're entering code by hand but when you try to paste in code that's already correctly indented, the auto-indent will cause the pasted code to be over indented. So to paste in code, you first need to enter paste mode by pressing `ctrl-E`. When you do this you'll see:

    paste mode; Ctrl-C to cancel, Ctrl-D to finish
    ===

Note: if you need a reminder later of the various key bindings, like `ctrl-E`, just enter `help()` (when in normal mode).

Now you can copy and paste in the following code and then press `ctrl-D`, the code will start to run immediately:

```
import machine
button = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)
prev = True
while True:
    now = button.value()
    if now != prev:
        print('Button', 'released' if now else 'pressed')
        prev = now
```

Press the BOOT button and the code will print `Button pressed` (and `Button released` when you release the button).

Notes:

* The button value is `False` when the button is pressed, which is maybe the opposite to what you'd expect.
* The code may print more often than you'd expect due to a phenomenon called [bounce](https://learn.adafruit.com/make-it-switch/debouncing) (though if you look at the [board schematic](https://dl.espressif.com/dl/schematics/esp32_devkitc_v4-sch.pdf), you'll see that the buttons have 0.1&micro;F capicitors in parallel which is a cheap mechanism for reducing bounce).

You can press `ctrl-C` to interrupt the running code and return to the MicroPython REPL prompt. And then press `ctrl-X` to return to the `rshell` prompt.

Checking memory usage
---------------------

Now that you know how to access the MicroPython REPL, you can check out the memory usage like so:

```
>>> import micropython
>>> micropython.mem_info()
stack: 720 out of 15360
GC: total: 4098240, used: 4768, free: 4093472
 No. of 1-blocks: 14, 2-blocks: 7, max blk sz: 264, max free sz: 255829
```

If you did the same thing on a board with a WROOM module you'd see output something like this:

```
stack: 736 out of 15360
GC: total: 111168, used: 4768, free: 106400
 No. of 1-blocks: 14, 2-blocks: 7, max blk sz: 264, max free sz: 6637
```

You can see that with a WROOM module, the Python [garbage collector](https://en.wikipedia.org/wiki/Garbage_collection_(computer_science)) (GC) has considerably less space to work with.

Example circuit
---------------

Let's create a simple circuit with an LED connected to pin 13 on the board:

<img width="720" src="devkitc-and-led.jpg">

The circuit consists of:

* A standard **5mm 20mA red LED** - its long leg (the positive anode) is on the top side of the central divide of the breadboard and is connected to pin 13 of the DevKit board, while its short leg (the negative cathode) is on the other side of the divide.
* A **220&ohm; resister** - its legs are inserted such that one is connected with the cathode of the LED and the other to the GND pin of the DevKit board.

Note: 220&ohm; is actually much higher than needed (meaning the LED won't be very bright) but it's a common resistor type and will keep the current well below the safe level for the pins on the board.

Now lets create a simple program that flashes the LED on and off:

    $ cat > main.py << EOF
    import machine
    import time

    pin13 = machine.Pin(13, machine.Pin.OUT)
    on = 1
    while True:
        pin13.value(on)
        on ^= 1
        time.sleep(0.2)
    EOF

Let's copy it to the board and then connect to the MicroPython REPL:

    $ rshell --buffer-size 512 --quiet -p $PORT
    > cp main.py /pyboard
    > repl

If you now press the EN button on the board, you'll see it do a hard reset and start the program - the LED should blink on and off every 200ms.

Going further
-------------

For more on using the MicroPython REPL see the [REPL section](../getting-started.md#working-with-the-repl) of my other introduction to MicroPython. There I used `screen` to connect to the REPL but, now that you know how to access the REPL using `rshell`, it's better to use `rshell` rather than `screen`.

Similarly see the [documentation and tutorial section](../getting-started.md#documentation-and-tutorial) of that other introduction for pointers to more in-depth material.
