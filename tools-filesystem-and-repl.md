Working with the MicroPython filesystem and REPL
================================================

**TL;DR** - my recommendation is to use `rshell` for working with the MicroPython filesystem and REPL.

As seen in my [notes](getting-started.md) on setting up an ESP32 board with MicroPython, the filesystem of a newly setup board just contains a single file called `boot.py`. You generally leave this as it is and just upload the main script, called `main.py`, that you want the board to run. For more on boot scripts see this brief [guide](https://learn.adafruit.com/micropython-basics-load-files-and-run-code/boot-scripts) from Adafruit. If you need any additional modules, beyond the default ones provided, you'll also need to upload these.

A little surprisingly there's no clear winner when it comes to the most popular tool for transfering and managing files on MicroPython boards. There are four main contenders:

* [`pyboard.py`](https://docs.micropython.org/en/latest/reference/pyboard.py.html) - included as part of the main MicroPython distribution, this is the most basic.
* [`ampy`](https://github.com/scientifichackers/ampy) - a slightly more sophisticated file management tool - used in all the older Adafruit MicroPython tutorials (before they created their own MicroPython derivative called [CircuitPython](https://circuitpython.readthedocs.io/en/latest/README.html)).
* [`rshell`](https://github.com/dhylands/rshell) - supports both basic command line usage and a shell-like environment. In addition to file transfer and management, it supports the ability to interact with the MicroPython REPL.
* [`mpfshell`](https://github.com/wendlers/mpfshell) - similar to `rshell` but with a command set more reminiscent of DOS and ftp (whereas `rshell` command set is more UNIX like).

There's also [WebREPL](https://github.com/micropython/webrepl) but this requires that your board is already setup and connected to the web, i.e. you need to have used some other tool to get your board configured before you can use WebREPL. I'm not going to cover WebREPL here.

`pyboard.py` is very basic but provides the API needed to interact the MicroPython filesystem - `ampy`, `rshell` and `mpfshell` all use `pyboard.py` under the covers to do the low-level file management work for them.

Initially, I started using `ampy` as I have a lot of positive experience with Adafruit tutorials - if they recommend something, it's generally a good choice. And I liked the idea of a tool that just tried to do one thing well, i.e. file management, rather than also bundling in other things such as interacting with the REPL. However, using a tool that doesn't also support working with the REPL quickly gets tiring during development. At first I connected to the MicroPython REPL using [`screen`](https://www.gnu.org/software/screen/) and updated files using `ampy`. However, you can't transfer files while connected to the REPL - so development involves continuously quitting the REPL, transfering updated files and then restarting the REPL - not terribly convenient.

In the end, it's more convenient to use something like `rshell` and its shell-like environment that can manage both file related operations and working with the MicroPython REPL. I settled on `rshell` rather than `mpfshell` as I prefer its familar UNIX like feel and the way it makes your board look like its filesystem is mounted on your local system (an illusion that only goes so far).

Below are my notes on getting used to the various tools but, as noted above, I recommend `rshell`.

Note: the development of `ampy`, `rshell` and `mpfshell` is rather moribund - all three are stable and now seem to only receive very occassional updates.

Python
------

The following sections all assume that you've already got Python 3 installed locally, if you don't see my notes on [installing Python](https://github.com/george-hawkins/snippets/blob/master/install-python.md).

Then before you install anything Python related you should be operating in a Python venv. If you haven't set this up already, you can do it like so:

    $ python3 -m venv env
    $ source env/bin/activate
    $ pip install --upgrade pip

The `source` step is the only one you need to repeat, if you open a new terminal and need to activate the virtual environment again. Once an environment is activated you can just use commands like `python` and `pip` rather than worrying about using specific versions like `python3` or `pip3`.

Serial port
-----------

All the examples below assume you've set the variable `PORT` to point to the serial device corresponding to your board.

On Mac you typically just need to do:

    $ PORT=/dev/cu.SLAB_USBtoUART

And on Linux, it's typically:

    $ PORT=/dev/ttyUSB0

pyboard.py
----------

The MicroPython distribution provides a very basic tool called [`pyboard.py`](https://docs.micropython.org/en/latest/reference/pyboard.py.html), however it's not made available via [PyPI](https://pypi.org/) and a little hand assembly is necessary. Assuming you've already got a Python venv setup, just do:

    $ pip install pyserial
    $ curl -O https://raw.githubusercontent.com/micropython/micropython/master/tools/pyboard.py
    $ chmod a+x pyboard.py 

Now it's setup, you can use it like so:

    $ ./pyboard.py --device $PORT -f ls
    ls :
         139 boot.py
    $ ./pyboard.py --device $PORT -f cat :boot.py
    cat :boot.py
    # This file is executed on every boot (including wake-boot from deepsleep)
    ...

Note the `:` before `boot.py`, the colon means the remote device rather than the local machine. So you can copy a file to the board like this:

    $ ./pyboard.py --device $PORT -f cp main.py :main.py

Or just:

    $ ./pyboard.py --device $PORT -f cp main.py :

For more details see the [`pyboard.py` documentation](https://docs.micropython.org/en/latest/reference/pyboard.py.html).

Note: MicroPython doesn't currently support any mechanism to interact with the filesystem other than via the REPL, so under the covers `pyboard.py` just interacts with the REPL like a human does rather than having a proper API for interacting with the filesystem. This makes things a bit hacky, e.g `ampy` issue [#64](https://github.com/scientifichackers/ampy/issues/64) shows a typical consequence of this.

ampy
----

`ampy` was initially developed by Adafruit but is now maintained by [Scientific Hackers](https://github.com/scientifichackers) (previously known as PyCampers).

To install `ampy`:

    $ pip install git+https://github.com/scientifichackers/ampy.git
    $ ampy --help
    Usage: ampy ...

Using the package name `git+https://github.com/scientifichackers/ampy.git` means that you get the latest version available on GitHub. `ampy` is under semi-active development but they seem to have stopped making releases to PyPI in October 2018 (see the PyPI [release history](https://pypi.org/project/adafruit-ampy/#history)).

Assuming your board is connected and you've got the `PORT` environment variable set you can start using `ampy` like so:

    $ export AMPY_PORT=$PORT
    $ ampy ls
    /boot.py
    $ ampy get /boot.py
    # This file is executed on every boot (including wake-boot from deepsleep)
    ...

Note that `get` just displays the contents of the file, it doesn't copy the file to your machine. Now let's create and upload a simple Python script:

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
    $ ampy put main.py

Now press the reset button on the board and the script will start running.

Note: if you get the error message `Could not enter raw repl` when using `ampy`, you'll have to set `AMPY_DELAY` (see the [configuration section](https://github.com/scientifichackers/ampy#configuration) of the `ampy` `README`).

rshell
------

[`rshell`](https://github.com/dhylands/rshell) is developed by Dave Hylands. Unlike `ampy` and `pyboard.py` it provides a shell like environment that includes access to the MicroPython REPL. This avoids having to continuously switch between a tool like `screen` to interact with the REPL and another tool to upload files to the board.

You can install it like so:

    $ pip install rshell

A nice feature of `rshell` is that you can ask it to discover the serial port of your board:

    $ rshell --list
    USB Serial Device 10c4:ea60 with vendor 'Silicon Labs' serial '01D1884D' found @/dev/ttyUSB0

Once installed, you can start `rshell` like so:

    $ rshell -p $PORT
    Using buffer-size of 32
    Connecting to /dev/ttyUSB0 (buffer-size 32)...
    Trying to connect to REPL  connected
    Testing if sys.stdin.buffer exists ... Y
    Retrieving root directories ...
    Setting time ... Mar 07, 2020 16:22:55
    Evaluating board_name ... pyboard
    Retrieving time epoch ... Jan 01, 2000 

The important thing displayed as part of connecting is the name of your board, here it's `pyboard`. You have to use this name whenever you want to refer to the board's file system rather than your local filesystem.

    > ls -l /pyboard
       139 Jan  1 2000  boot.py
      5253 Jan  1 2000  main.py

I find this a really nice feature of `rshell`, i.e. that there isn't an idea of local and remote, instead your board's filesystem looks like it's mounted locally under `/pyboard`. This illusion only goes so far, e.g. if you do `ls /` you only see your local files, it doesn't attempt to add `pyboard` in to the list of local files.

You can move around and work with files as if there were just a single filesystem. To show your local files:

    > ls
    main.py

To change directory to your board and view the files there:

    > cd /pyboard
    > ls
    boot.py

To return to your local directory and copy `main.py` to your board:

    > cd -
    > cp main.py /pyboard
    > ls /pyboard
    boot.py  main.py

Note: when you use `ls` wihtout `-l` it doesn't behave quite like normal `ls`, it groups files by type (directories, `.py` files etc.) and sorts the filenames within these groups.

The big additional feature of `rshell` is being able to easily work with the REPL, like so:

    > repl
    Entering REPL. Use Control-X to exit.
    MicroPython v1.12 on 2019-12-20; ESP32 module with ESP32
    Type "help()" for more information.
    >>>

As it says, use `ctrl-X` to exit and return to the `rshell` prompt. When you run `repl` for the first time, it seems to actively interrupt any running program, in order to get you to the REPL prompt, but if you exit to the `rshell` prompt then it doesn't do this on subsequent invocations of `repl`.

For simply doing a hard reset, pressing the reset button on the board works fine. Or in the REPL one can do the following:

    > repl
    >>> import machine; machine.reset()

You can also use `rshell` to run a single command and then exit:

    $ rshell -p $PORT ls /pyboard
    Using buffer-size of 32
    ...
    Retrieving time epoch ... Jan 01, 2000
    boot.py  main.py

Use `--quiet` if you don't want all the start-up output:

    $ rshell --quiet -p $PORT ls /pyboard
    boot.py  main.py

You can also use this to go straight into the REPL:

    $ rshell --quiet -p $PORT repl
    ...
    >>>

You can get `rshell` to run things in the REPL and then exit:

    $ rshell --quiet -p $PORT repl '~ import sys ~ sys.implementation ~'
    >>> import sys ; sys.implementation
    (name='micropython', version=(1, 12, 0), mpy=10757)

Note that you have to use `~` (tilde) instead of `;` to separate statements. The first tilde is not optional but if you leave out the last tilde then `rshell` stays in the REPL rather than exiting and returning to your normal prompt.

For a more dramatic but sometimes useful operation, you can completely recreate the filesystem on the device like this:

    $ rshell --buffer-size 512 --quiet -p $PORT repl '~ import os ~ os.VfsFat.mkfs(bdev) ~'

This will also remove `boot.py` - if you've got any special boot setup, you should copy this file and restore it after the clean-up.

You can also include a sequence of `rshell` commands in a script and then get `rshell` to run this script:

    $ cat > myscript << EOF
    connect serial /dev/ttyUSB0
    rm -r /pyboard/libs
    cp -r libs /pyboard
    EOF
    $ rshell --quiet -f myscript 
    ...

### `rshell` issues

**1.** If you unplug your board and then reconnect it, `rshell` automatically reconnects. However, I found that after reconnection, pressing `ctrl-C` while in the MicroPython REPL killed `rshell` rather than simply interrupting whatever was running in MicroPython.

**2.** `rshell` understands that `~` means your home directory but currently tab completion breaks when using `~`.

**3.** Tab completion works for filenames in various situations, e.g. when using `ls`, but does not work in others, e.g. when using the `connect` command.

**4.** `rshell` does not save your command history, so if you exit and restart `rshell` you can't just search backwards for what you were doing previously.

**5.** Sometimes things got into a state where `rshell` would just hang at startup:

    $ rshell -p $PORT
    ...
    Trying to connect to REPL

Oddly the alternatives that I've tried here, e.g. `mpfshell` or `pyboard.py`, could still connect when this happened.

The only solution was to disconnect the board and plug it back in - as the other tools could still connect, this seems to be an `rshell` issue rather than a board issue.

### `rshell` buffer size

When I start `rshell` using `-p` it connects with a buffer size of 32:

    $ rshell -p $PORT
    Using buffer-size of 32
    Connecting to /dev/ttyUSB0 (buffer-size 32)...

However the `README` for `rshell` says that the default buffer size is 512. If I connect within `rshell` then it does use this buffer size:

    $ rshell
    > connect serial /dev/ttyUSB0
    Connecting to /dev/ttyUSB0 (buffer-size 512)...

I don't know why it defaults to a smaller buffer size in the first situation but it makes a huge difference to file transfer speeds. So when using `-p` you should specify the buffer size explicitly:

    $ rshell --buffer-size 512 -p $PORT
    Using buffer-size of 512
    Connecting to /dev/ttyUSB0 (buffer-size 512)...
    ...
    > cp my-large-file /pyboard

Letting it use a buffer size of 32 results in file transfer that are 3 times slower for large files. I experimented with other buffer sizes - there's no further gain from increasing the buffer size beyond 512.

I always start `rshell` with both the `--buffer-size` option and the `--quiet` flag, like so:

    $ rshell --buffer-size 512 --quiet -p $PORT

### `rshell` notes

`rshell` development seems to have stopped in mid-2019, Peter Hinch [forked it](https://github.com/peterhinch/rshell) and added a macro feature (similar to `alias` in Bash) but does not seem to be developing it further either.

mpfshell
--------

In the end I chose `rshell` as my main tool for interacting with MicroPython boards. [`mpfshell`](https://github.com/wendlers/mpfshell) is very similar feature-wise to `rshell` and I just looked at it briefly for comparison.

To install:

    $ pip install mpfshell

You have to leave out the `/dev` to connect to particular device:

    $ mpfshell ttyUSB0 
    Connected to esp32

    ** Micropython File Shell v0.9.1, sw@kaltpost.de ** 
    -- Running on Python 3.5 using PySerial 3.4 --

    mpfs [/]> help

    Documented commands (type help <topic>):
    ========================================
    EOF  cd     exec  get   lcd  lpwd  md    mput  mrm   put   pwd   rm
    cat  close  exit  help  lls  ls    mget  mpyc  open  putc  repl

It's feature set is very similar to that of `rshell` but I find it a bit confusing the way some `mpfshell` command arguments implicitly refer to local files and others to remote files. I also prefer the UNIX-like feel of `rshell`. `mpfshell` has more an `ftp` or DOS feel.

An interesting additional feature, that `rshell` does not have, is the ability to compile files on the fly and copy the resulting `.mpy` file to your board using `putc`:

    mpfs [/]> putc main.py
    mpfs [/]> ls
    Remote files in '/':
           main.mpy 

This depends on `mpy-cross` being present in your path (see [`precompiling.md`](precompiling.md) for more on this).
