Tools for working with the MicroPython filesystem and REPL
==========================================================

As seen above the filesystem of a newly setup board just contains a single file called `boot.py`. You generally leave this as it is and just upload the main script, that you want the board to run, as `main.py` (for more on this see the Adafruit [guide](https://learn.adafruit.com/micropython-basics-load-files-and-run-code/boot-scripts) to the boot scripts). If you need any additional modules, beyond the default provided ones, you'll also need to upload these.

ampy
----

A little surprisingly there's no standard MicroPython tool for doing this. There are a number of third part tools available - one of the simplest and most popular is [Ampy](https://github.com/scientifichackers/ampy) which I'll use here.

Note: MicroPython doesn't currently support any mechanism to interact with the filesystem other than via the REPL, so under the covers tools like Ampy just interact with the REPL like a human does rather than having a proper API for interacting with the filesystem. This makes things a bit hacky, e.g see issue [#64](https://github.com/scientifichackers/ampy/issues/64).

Before you install anything Python related you should be operating in a Python virtual environment. If you haven't this setup already, you can do it like so:

    $ brew install python
    $ python3 -m venv ~/esp-env
    $ source ~/esp-env/bin/activate
    $ pip install --upgrade pip

The `source` step is the only one you need to repeat, if you open a new terminal and need to activate the virtual environment again. Once an environment is activated you can just use commands like `python` and `pip` rather than worrying about using specific versions like `python3` or `pip3`.

Now to install Ampy itself:

    $ pip install git+https://github.com/scientifichackers/ampy.git
    $ ampy --help
    Usage: ampy ...

Using the package name `git+https://github.com/scientifichackers/ampy.git` means that you get the latest version available on GitHub. Ampy is under active development but they seem to have stopped making releases to PyPi in October 2018 (see the PyPi [release history](https://pypi.org/project/adafruit-ampy/#history)).

Assuming your board is connected and you've still got the `PORT` environment variable set you can start using Ampy like so:

    $ export AMPY_PORT=$PORT
    $ ampy ls
    /boot.py
    $ ampy get /boot.py
    # This file is executed on every boot (including wake-boot from deepsleep)
    ...

Note that `get` just displays the contents of the file, it doesn't copy the file to your machine. Now let's upload a script:

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

Note: if you get the error message `Could not enter raw repl` when using Ampy, you'll have to set `AMPY_DELAY` (see the [configuration section](https://github.com/scientifichackers/ampy#configuration) of the Ampy `README`).

pyboard.py
----------

MicroPython do actually provide a tool as well, called [`pyboard.py`](https://docs.micropython.org/en/latest/reference/pyboard.py.html), but you have to do some hand assembly. Assuming you've already got a Python virtual environment setup as above, just do:

    $ curl -O https://raw.githubusercontent.com/micropython/micropython/master/tools/pyboard.py
    $ chmod a+x pyboard.py 
    $ pip install pyserial

Now it's setup, you can use it like so:

    $ ./pyboard.py --device $PORT -f ls
    ls :
         139 boot.py
         141 main.py
    $ ./pyboard.py --device $PORT -f cat :main.py
    cat :main.py
    import machine
    import time
    ...

Note the `:` before `main.py`, the colon means the remote device rather than the local machine. So you can copy a file to the board like this:

    $ ./pyboard.py --device $PORT -f cp main.py :main.py

Or just:

    $ ./pyboard.py --device $PORT -f cp main.py :

For more details see the [`pyboard.py` documentation](https://docs.micropython.org/en/latest/reference/pyboard.py.html).

rshell
------

[Rshell](https://github.com/dhylands/rshell) is developed by Dave Hylands. Unlike `ampy` and `pyboard.py` it provides a shell like environment that includes access to the MicroPython REPL. This avoids having to continuously switch between a tool like `screen` to interact with REPL and another tool to upload files to the board.

You can install it like so:

    $ pip install rshell

A nice feature of `rshell` is that you can ask it to discover the serial port of your board:

    $ rshell --list
    USB Serial Device 10c4:ea60 with vendor 'Silicon Labs' serial '01D1884D' found @/dev/ttyUSB0

Once installed, you can start `rshell` like so:

    $ rshell -p $PORT
    Using buffer-size of 32
    Connecting to /dev/cp2104 (buffer-size 32)...
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
    > repl
    Entering REPL. Use Control-X to exit.
    MicroPython v1.12 on 2019-12-20; ESP32 module with ESP32
    Type "help()" for more information.
    >>>

As it says, use `ctrl-X` to exit and return to the `rshell` prompt. When you run `repl` for the first time, it seems to actively interrupt any running program, in order to get you to the REPL prompt, but if you exit to the `rshell` prompt then it doesn't do this on subsequent invocations of `repl`.

Tab completion works for filenames in various situations, e.g. when using `ls`, but does not work in others, e.g. when using the `connect` command.

When I start `rshell` using `-p` it connects with a buffer size of 32:

    $ rshell -p $PORT
    Using buffer-size of 32
    Connecting to /dev/cp2104 (buffer-size 32)...

However the `README` for `rshell` says that the default buffer size is 512. If I connect within `rshell` then it does use this buffer size:

    $ rshell
    > connect serial /dev/cp2104
    Connecting to /dev/cp2104 (buffer-size 512)...

I don't know why it defaults to a smaller buffer size in the first situation but it makes a huge difference to file transfer speeds. So when using `-p` you should specify the buffer size explicitly:

    $ rshell -p $PORT --buffer-size 512
    Using buffer-size of 512
    Connecting to /dev/cp2104 (buffer-size 512)...
    ...
    > cp my-large-file /pyboard

Letting it use a buffer size of 32 results in file transfer that are 3 times slower for large files. I experimented with other buffer sizes - there's no further gain from increasing the buffer size beyond 512.

If you unplug your board and then reconnect it, `rshell` automatically reconnects. However, I found this didn't work perfectly, e.g. after reconnection I found that pressing `ctrl-C` while in the MicroPython REPL killed `rshell` rather than simply interrupting whatever was running in MicroPython.

For simply doing a hard reset, pressing the reset button on the board works fine. Or in the REPL one can do the following:

    > repl
    >>> import machine; machine.reset()

It's nice that `rshell` behaves as if `/pyboard` is a directory of your local filesystem, i.e. it pretends that your board is mounted under this directory. However the disadvantage of not having the concept of a local and remote filesystem is that you end up having to use long-ish path names to refer to your _local_ files if you've changed directory within `rshell` to `/pyboard`:

    > cd /pyboard
    > ls
    boot.py
    > cp ~/my-project/main.py .
    > ls 
    boot.py        main.py
    
Aside: `rshell` understands that `~` means your home directory but currently tab completion breaks when using `~`.

Note: when you use `ls` wihtout `-l` it doesn't behave quite like normal `ls`, it groups files by type (directories, `.py` files etc.) and sorts the filenames within these groups.

You can also use `rshell` to run a single command and then exit:

    $ rshell -p $PORT ls /pyboard
    Using buffer-size of 32
    ...
    Retrieving time epoch ... Jan 01, 2000
    boot.py        main.py

Use `--quiet` if you don't want all the start-up output:

    $ rshell -p $PORT --quiet ls /pyboard
    boot.py        main.py

You can also use this to go straight into the REPL:

    $ rshell -p $PORT --quiet repl
    ...
    >>>

You can get `rshell` to run things in the REPL and then exit:

    $ rshell -p $PORT --quiet repl '~ import sys ~ sys.implementation ~'
    >>> import sys ; sys.implementation
    (name='micropython', version=(1, 12, 0), mpy=10757)

Note that you have to use `~` (tilde) instead of `;` to separate statements. The first tilde is not optional but if you leave out the last tilde then `rshell` stays in the REPL rather than exiting and returning to your normal prompt.

You can also include a sequence of `rshell` commands in a script:

    $ cat > myscript << EOF
    connect serial /dev/cp2104
    rm -r /pyboard/libs
    cp -r libs /pyboard
    EOF
    $ rshell --quiet -f myscript 
    ...

Sometimes things got into a state where `rshell` would just hang at startup:

    $ rshell -p $PORT
    ...
    Trying to connect to REPL

Oddly the alternative that I've tried here, e.g. `mpfshell` or `pyboard.py`, could still connect when this happened.

The only solution was to disconnect the board and plug it back in - as the other tools could still connect, this seems to be an `rshell` issue rather than a board issue.

Notes:

* Rshell does not save your command history, so if you exit and restart `rshell` you can't just search backwards for what you were doing previously.
* Rshell development seems to have stopped in mid-2019, Peter Hinch [forked it](https://github.com/peterhinch/rshell) and added a macro feature (similar to `alias` in Bash) but does not seem to be developing it further either.

mpfshell
--------

Currently `pyboard.py`, `ampy`, `rshell` and `mpfshell` seem to be the main tools people are using to interact with MicroPython boards.

So let's install and take a look at the last of these - [`mpfshell`](https://github.com/wendlers/mpfshell):

    $ pip install mpfshell

Note that `mpfshell`, like `ampy` and `rshell`, is currently not being very actively developed.

You have to leave out the `/dev` to connect to particular device:

    $ mpfshell cp2104 
    Connected to esp32

    ** Micropython File Shell v0.9.1, sw@kaltpost.de ** 
    -- Running on Python 3.5 using PySerial 3.4 --

    mpfs [/]> help

    Documented commands (type help <topic>):
    ========================================
    EOF  cd     exec  get   lcd  lpwd  md    mput  mrm   put   pwd   rm
    cat  close  exit  help  lls  ls    mget  mpyc  open  putc  repl

It's feature set is very similar to that of `rshell`.

An interesting additional feature is the ability to compile files on the fly and copy the resulting `.mpy` file to your board using `putc`:

    mpfs [/]> putc main.py
    mpfs [/]> ls
    Remote files in '/':
           main.mpy 

This depends on `mpy-cross` being present in your path (see [`precompiling.md`](precompiling.md) for more on this).
