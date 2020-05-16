Precompiling MicroPython files
------------------------------

Python is an interpreted language and normally there's no separate compile phase. The same is true when using MicroPython.

MicroPython actually compiles your `.py` files on-the-fly as needed on your board. Normally this works fine but when memory is tight the compiler itself may run out of memory.

You can avoid this by pre-compiling your `.py` files to `.mpy` files and then copying these, rather than the original `.py` files, to your board.

For more about `.mpy` files see the [MicroPython documentation](https://docs.micropython.org/en/latest/reference/mpyfiles.html).

Pre-compiling depends on the MicroPython [`mpy-cross`](https://github.com/micropython/micropython/tree/master/mpy-cross) tool which you can build from source yourself.

An easier alternative is to use the version made available [via PyPi](https://pypi.org/project/mpy-cross/).

Note that this version isn't made available directly by the Micropython GitHub organization. Instead it's built by the [mpy_cross](https://gitlab.com/alelec/mpy_cross) project on GitLab that's maintained by Andrew Leech (who also contributes commits to the main Micropython repo). His project is basically a CI setup that imports Micropython as a submodule (which is updated weeky to point to the latest commit) and creates builds for Windows, Mac and Linux. As such, it's much simpler to use than building from source yourself.

    $ pip install mpy_cross

**Update:** the following section, on creating a link to `mpy-cross`, may not be relevant by the time you're reading this - I logged issue [#8](https://gitlab.com/alelec/mpy_cross/-/issues/8) and it has been addressed (but as of May 16th, 2020 a new version of mpy_cross has not yet been released on PyPI).
    
For some reason the executable isn't automatically copied/linked to the `bin` directory of your current environment, so find the package location and then the executable:

    $ pip show mpy_cross
    ...
    Location: .../env/lib/python3.5/site-packages
    ...
    $ ls .../env/lib/python3.5/site-packages/mpy_cross
    ... mpy-cross

And create the necessary link yourself and once done, you can use `mpy-cross` like any other command:

    $ ln -s .../env/lib/python3.5/site-packages/mpy_cross/mpy-cross .../env/bin
    $ mpy-cross --version
    MicroPython v1.12 on 2019-12-21; mpy-cross emitting mpy v5

Note: make sure to use an absolute path when specifying the source of the soft link.

Now you can compile files locally and copy them to your board:

    $ mpy-cross main.py 
    $ ls main.*
    main.mpy  main.py
    pyboard.py --device $PORT -f cp main.mpy :

As well as avoiding having to do compilation work on your board, the resulting `.mpy` files are significantly smaller than the original `.py` files.


