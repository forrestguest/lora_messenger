# lora_messenger
LORA Wireless Messenger

Some refinements to the project shown at:
https://msglab.co/room/lo-ra-msg

Notable improvements:
- Messages are encrypted
- Devices have names for better scroll back
- Some small bugs fixed
- Buttons all do something (mostly just change the color of the LED)
- I adjusted the STLs to fit the larger USB plugs I'm using

This project is mostly just a combination of free resources and developer boards.

Shopping list:
- Keyboard featherwing: https://www.tindie.com/products/arturo182/keyboard-featherwing-qwerty-keyboard-26-lcd/
- Feather m4: https://www.adafruit.com/product/3857
- LORA Featherwing: https://www.adafruit.com/product/3231
- A set of featherwing headers: https://www.adafruit.com/product/2940
- A 1200 mAh lipo battery pack: https://www.adafruit.com/product/258
- Antenna to ufl pad: https://www.adafruit.com/product/1661
- A stubby antenna: https://www.amazon.com/gp/product/B086ZG5WBR/
- m3 bolts: https://www.amazon.com/gp/product/B07H17DQDG/
- heat inserts: https://www.amazon.com/gp/product/B07HKW7LKH/
- Wrist Strap: https://www.amazon.com/gp/product/B0832CKB59/
- 3d printed case (see STL files)
- Tools
  - A 3d Printer
  - A soldering iron (with fine tip and 2 MM tip)
  - A computer
  - A USB to mini USB cable
  - A 2.5mm allen wrench
  - Offset tweezers: https://www.amazon.com/dp/B006RBBE3I/

More information:
Stores: Adafruit things are available in a variety of locations, their store charges shipping but is otherwise the cheapest option for the feather and LORA featherwing.  I would also recommend buying the headers from them, and batteries from another source may have reversed polarity.  Check the battery image at Adafruit against the battery you get to make sure you don't break anything.  Tindie, Adafruit, Digikey and of course Amazon are all places to check.

The blackbarry q10 keyboard featherwing is from https://www.solder.party/, made by https://twitter.com/arturo182.  
Docs: https://www.solder.party/docs/keyboard-featherwing/
Code: https://github.com/arturo182/keyboard_featherwing_sw

The feather m4 comes in two versions, either is fine.  One has CAN bus support and costs a few dollars more.

The LORA featherwing I use is the 900 MHz (915 MHz) for the US.  Here's a page giving the recommended version by country: https://www.thethingsnetwork.org/docs/lorawan/frequencies-by-country/index.html.  TLDR; Americas 900 MHz, EU 433MHz

I used 1500 mAh lipo battery pack.  Don't be tempted to go with a bigger one, it won't fit in the case.  I haven't managed to run out of battery yet.  As mentioned in the stores section above, make sure the polarity is correct for the Adafruit standard so the feather can charge and use the battery.

For 3d printed case, use three walls in your slicer for the bottom, you'll need the reinforcement for the heat set inserts.

You can use whatever antenna you want, but the case looks nice with the little stubby one.

I like the look of the hex bolts, you will probably have to clean up your print a little around all of the holes.  I also bought a little m3 tap, which I used before I put in the heat inserts.  The heat inserts go in very quickly, don't waste time when you're putting them in or you could melt it through the side of the hole.

Instructions:
1. Download everything you'll need
    - The code.py and msg_config.json from this repository
    - The Mu code editor (https://codewith.mu/)
    - The circuitpython installer (https://circuitpython.org/board/feather_m4_express/)
    - The circuitpython libraries (https://circuitpython.org/libraries)
    - The encryption libraries from this repository (source: https://www.nayuki.io/page/cryptographic-primitives-in-plain-python)
 2. Install Mu on your computer
 3. Assemble the feathers by soldering on the uFL connector and all of the headers.  I put some of them on upside down in order to keep the boards as close to the screen as possible.  Don't put the case on yet.
 4. Open Mu and plug in the USB cable
 5. Double click the reset button to put the feather into flashing mode.  The USB drive should disappear and you should get a drive named *SOMETHING*BOOT
 6. Copy and paste the circuitpython UF2 onto the drive.  It should reboot, and the drive name should switch back to CIRCUITPY.
 7. Open the boot.txt and make sure the version has been updated.
 8. Unplug everything and assemble the case, plug in the battery and antenna. I needed a pair of offset tweezers in order to seat the antenna correctly.
 9. Generate a key.  Open IDLE or another python editor (Mu doesn't seem to have an interactive console), and enter the following commands:
     - import random
     - '%030x' % random.randrange(16**32)
 10. Edit the msg_config.json file and update the key with the result of the above, and set the device name to something useful.  Only 10 characters will be used.
 11. Plug the usb back in and copy the following files into the main drive from this repository:
    - code.py
    - msg_config.json
 12. Edit the 
 13. Copy the following files into the lib directory from the encryption folder of this repository:
     - aescipher.py
     - cryptocommon.py
 14. Copy the following files into the lib directory from the circuitpython library zip file:
     - the entire adafruit_bus_device folder
     - the entire adafruit_display_shapes folder
     - the entire adafruit_display_text folder
     - the entire adafruit_hashlib folder
     - the entire adafruit_register folder
     - adafruit_binascii.mpy
     - adafruit_ili93451.mpy
     - adafruit_logging.mpy
     - adafruit_pct2075.mpy
     - adafruit_rfm9x.mpy
     - adafruit_sdcard.mpy
     - adafruit_stmpe610.mpy
     - bbq10keyboard.py
     - neopixel.mpy
 15. Saving the last file should have restarted the device, and the screen should load up and drop you into a black window 
 16. Realize you need to make at least two devices in order to chat, and repeat all of the above steps for any other devices.

TODO:
- find something for the other buttons to do
- find something for the pointer stick to do
- find out if the touchscreen is useful
