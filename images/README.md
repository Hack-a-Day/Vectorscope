Here you'll find some `uf2` images that you can copy directly to the badge when it's mounted in bootloader / USB-disk mode.

The images in micropython_compiled/ are a preview version of v1.22.0, with a driver for the GC9A01 screen and pull release for DMA support compiled in.  This is here really just in case you want to play around, or if you've soldered on a Pico W, which requires its own firmware.

The Supercon image includes our modified Micropython and all of the various python code that makes it run.

Note that flashing the Supercon `uf2` will probably wipe anything you have on the device, so save your work first.  Heck, save your work right now anyway.  You never know!

