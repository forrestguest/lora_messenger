# keyboard featherwing
from bbq10keyboard import BBQ10Keyboard, STATE_PRESS, STATE_RELEASE, STATE_LONG_PRESS
from adafruit_stmpe610 import Adafruit_STMPE610_SPI
import adafruit_ili9341
import adafruit_sdcard
import digitalio
import displayio
import neopixel
import storage
import board
import time
import os
import busio

# config file
import json

# encryption
import aescipher
import cryptocommon

#LORA featherwing
import adafruit_rfm9x

# battery voltage meter
from analogio import AnalogIn

# shapes
from adafruit_display_text.label import Label
from adafruit_display_shapes.rect import Rect

# text to screen
import terminalio
import gc

# Optional Qwiic test
try:
    import adafruit_pct2075
except Exception as e:
    print('Skipping Qwiic test,', e)

all_passed = True

#device name, must be 10 char long

#default name
device_name = "code name "

#read name from file
with open("/msg_config.json", "r") as cfg_fp:
    config_string = cfg_fp.read()
    config = json.loads(config_string)
    device_name = config["device_name"]

# build key from config
key = config["msg_key"]
keybytelist = cryptocommon.hexstr_to_bytelist(key)

#truncate to 10 characters
device_name = device_name[0:10]

#pad with spaces to 10 characters
dev_size = len(device_name)
dev_space = 10 - dev_size
device_name += " " * dev_space

# ui dimensions
header = 16
margin = 0
border = 0

# Release any resources currently in use for the displays
displayio.release_displays()

# board pins
spi = board.SPI()
tft_cs = board.D9
tft_dc = board.D10
touch_cs = board.D6
sd_cs = board.D5
neopix_pin = board.D11

# initialize display module
display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs)
display = adafruit_ili9341.ILI9341(display_bus, width=320, height=240)

# battery voltage reader
vbat_voltage = AnalogIn(board.VOLTAGE_MONITOR)

# Define radio parameters.
# Frequency of the radio in Mhz. Must match your
# module! Can be a value like 915.0, 433.0, etc.
RADIO_FREQ_MHZ = 915.0

# Define pins connected to the chip - you must solder fly wires
#  they are not connected from the factory
CS = digitalio.DigitalInOut(board.A3)
RESET = digitalio.DigitalInOut(board.A4)

# Initialize RFM radio
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ)

# Note that the radio is configured in LoRa mode so you can't control sync
# word, encryption, frequency deviation, or other settings!

# You can however adjust the transmit power (in dB).  The default is 13 dB but
# high power radios like the RFM95 can go up to 23 dB:
rfm9x.tx_power = 23

#initialize keyboard featherwing
i2c = board.I2C()
kbd = BBQ10Keyboard(i2c)

splash = displayio.Group(max_size=25)
display.show(splash)

# background
def bg_stripe(x, color):
    width = display.width
    color_bitmap = displayio.Bitmap(width, 240, 1)
    color_palette = displayio.Palette(1)
    color_palette[0] = color
    bg_sprite = displayio.TileGrid(
        color_bitmap, x=x*width, y=0, pixel_shader=color_palette)
    splash.append(bg_sprite)


bg_stripe(0, 0x000000)

# output rect
output_rect = Rect(margin, margin, display.width-margin*2, display.height -
                   margin*2-header-margin, fill=0x000000, outline=0x000000)
splash.append(output_rect)

# output header
header_rect = Rect(margin + border, margin+border,
                   display.width-(margin+border)*2+10, header, fill=0x03447c)
splash.append(header_rect)

#read the battery voltage
def get_voltage(pin):
    return (pin.value * 3.3) / 65536 * 2

# send a message, prepend sender, append eol characters
# and make sure not to send more than 252 bytes at once
# Send a packet.  Note you can only send a packet up to 252 bytes in length.
# This is a limitation of the radio packet size, so if you need to send larger
# amounts of data you will need to break it into smaller send calls.  Each send
# call will wait for the previous one to finish before continuing.
def send_message(msg_to_send):
    # prepare message
    send_string = device_name + ": " + msg_to_send + "\r\n"
    # initialize encrypted byte list
    send_bytes = []

    # convert message to byte list
    plaintextbytelist = cryptocommon.asciistr_to_bytelist(send_string)
    # split message into 16 byte block
    blocks = [plaintextbytelist[i:i+16] for i in range(0, len(plaintextbytelist), 16)]
    for block in blocks:
        # pad block
        block += [0] * (16 - len(block))
        # encrypt
        ciphertextbytelist = aescipher.encrypt(block, keybytelist)
        # add block to full message
        send_bytes.extend(ciphertextbytelist)

    # convert list to byte array
    send_buff = bytearray(send_bytes)
    # split bytes to 252 byte chunks
    chunks = [send_buff[i:i+252] for i in range(0, len(send_buff), 252)]
    for chunk in chunks:
        # pass to LORA module
        rfm9x.send_with_ack(chunk)

    # echo to local device
    term.write(send_string.encode('utf-8'))

# battery info
battery_voltage = get_voltage(vbat_voltage)
battery_level = "{:.2f}".format(battery_voltage)

# signal statistics
rssi = "{0}".format(rfm9x.last_rssi)
snr = "{:.2f}".format(rfm9x.last_snr)

# format header
msg_size = len(" lora " + device_name + " rssi:" + rssi + "  snr:" + snr + "  Bat:" + battery_level)
need_spc = 50 - msg_size
message = " lora " + device_name + (" " * need_spc) + " rssi:" + rssi + "  snr:" + snr + "  Bat:" + battery_level

header_text = Label(terminalio.FONT, text=str(message[0:50]),
                    x=margin * 2+border, y=int(margin+border+header/2), color=0xFFFFFF)
splash.append(header_text)

# output text
p = displayio.Palette(2)
p.make_transparent(0)
p[1] = 0xFFFFFF

w, h = terminalio.FONT.get_bounding_box()
tilegrid = displayio.TileGrid(terminalio.FONT.bitmap, pixel_shader=p, x=margin*2+border, y=int(
    margin+border+header+margin/2), width=48, height=15, tile_width=w, tile_height=h)
term = terminalio.Terminal(tilegrid, terminalio.FONT)
splash.append(tilegrid)

# input textarea
input_rect = Rect(margin, display.height-header-3,
                  display.width, header, fill=0x000000, outline=0x000000)
splash.append(input_rect)

# input text
max_input_char = 50
input_text = Label(terminalio.FONT, text='', x=margin*2+border,
                   y=int(display.height-margin-border-header*0.7), color=0xFFFFFF, max_glyphs=max_input_char)
splash.append(input_text)

# carret
carret = Rect(input_text.x + input_text.bounding_box[2] + 1, int(
    display.height-margin-header/2-header/4), 1, header//2, fill=0xFFFFFF)
splash.append(carret)

send_message("online - commlink open")

carret_blink_time = time.monotonic()
carret_blink_state = True

bat_refresh_time = time.monotonic()
bat_refresh_state = True

pixels = neopixel.NeoPixel(neopix_pin, 1)

run = 1

while True:
    packet = None
    packet = rfm9x.receive(with_ack=True)
    pixels[0] = [0, 0, 0]

    if packet is None:
        pixels[0] = [0, 0, 0]
        kbd.backlight = 0.5
    else:
        # Received a packet!
        # flash the LED
        pixels[0] = 0x03447c
        pixels.brightness = 0.05

        # And decode to ASCII text and print it too.  Note that you always
        # receive raw bytes and need to convert to a text format like ASCII
        # if you intend to do string processing on your data.  Make sure the
        # sending side is sending ASCII data before you try to decode!
        try:
            packet_text = ""
            packetbytelist = list(packet)
            blocks = [packetbytelist[i:i+16] for i in range(0, len(packetbytelist), 16)]
            for block in blocks:
                ascii_bytes = aescipher.decrypt(block, keybytelist)
                ascii_list = bytearray(ascii_bytes)
                packet_text += str(ascii_list, "ascii")
        except Exception as e:
            packet_text = "problem receiving message:\r\n" + str(e) + "\r\n"

        term.write("{0}".format(packet_text))

    # Carret blink animation
    if time.monotonic() - carret_blink_time >= 0.01:
        if carret_blink_state:
            splash.remove(carret)
        else:
            splash.append(carret)

        carret_blink_state = not carret_blink_state
        carret_blink_time = time.monotonic()

    # Process keyboard
    while kbd.key_count > 0:
        k = kbd.key
        if k[0] == STATE_PRESS:
            if k[1] == '\x06':  # L1
                pixels[0] = 0xdaf7a6
                pixels.brightness = 0.05
            if k[1] == '\x11':  # L2
                pixels[0] = 0xc70039
                pixels.brightness = 0.05
            if k[1] == '\x07':  # R1
                pixels[0] = 0x33ff3f
                pixels.brightness = 0.05
            if k[1] == '\x12':  # R2
                pixels[0] = 0x4233ff
                pixels.brightness = 0.05
            if k[1] == '\x08':  # Backspace
                if len(input_text.text) > 0:
                    input_text.text = input_text.text[:-1]
            elif k[1] == '\n':
                if len(input_text.text) > 0:
                    text = input_text.text
                    send_message(text)
                    input_text.text = ''
            else:  # Anything else, we add to the text field
                if len(input_text.text) < max_input_char:
                    input_text.text += k[1]

            carret.x = input_text.x + input_text.bounding_box[2] + 1

    if time.monotonic() - bat_refresh_time >= 10:
        if bat_refresh_state:
            # battery charge
            battery_voltage = get_voltage(vbat_voltage)
            battery_level = "{:.2f}".format(battery_voltage)

            # signal statistics
            rssi = "{0}".format(rfm9x.last_rssi)
            snr = "{:.2f}".format(rfm9x.last_snr)

            header_text.text = str(" lora " + device_name + "   "
                                + " rssi:" + rssi
                                + "  snr:" + snr
                                + "  Bat:" + battery_level)
        bat_refresh_state = not bat_refresh_state
        bat_refresh_time = time.monotonic()