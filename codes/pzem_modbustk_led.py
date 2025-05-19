# Reading PZEM-004t power sensor (new version v3.0) through Modbus-RTU protocol over TTL UART
# Run in python3

# To install library for PZEM:
# pip3 install modbus-tk
# pip3 install pyserial

import time

#library for LED matrix
from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.virtual import viewport
from luma.core.legacy import text, show_message, textsize
from luma.core.legacy.font import proportional, CP437_FONT, TINY_FONT, SINCLAIR_FONT, LCD_FONT

#library for PZEM-004T V3
import serial
import modbus_tk.defines as cst
from modbus_tk import modbus_rtu

#Setting LED matrix
serial_led = spi(port=0, device=0, gpio=noop())
device = max7219(serial_led, cascaded=4, block_orientation=-90)


# Connect to the slave
serial = serial.Serial(
                       port='/dev/ttyS0',
                       baudrate=9600,
                       bytesize=8,
                       parity='N',
                       stopbits=1,
                       xonxoff=0
                      )

master = modbus_rtu.RtuMaster(serial)
master.set_timeout(2.0)
master.set_verbose(True)

while True:
	data = master.execute(1, cst.READ_INPUT_REGISTERS, 0, 10)
	voltage = data[0] / 10.0 # [V]
	current = (data[1] + (data[2] << 16)) / 1000.0 # [A]
	power = (data[3] + (data[4] << 16)) / 10.0 # [W]
	energy = data[5] + (data[6] << 16) # [Wh]
	frequency = data[7] / 10.0 # [Hz]
	powerFactor = data[8] / 100.0
	alarm = data[9] # 0 = no alarm

	print('Voltage [V]\t: ', voltage)
	print('Current [A]\t: ', current)
	print('Power [W]\t: ', power) # active power (V * I * power factor)
	print('Energy [Wh]\t: ', energy)
	print('Frequency [Hz]\t: ', frequency)
	print('Power factor []\t: ', powerFactor)
	#print('Alarm : ', alarm)
	print("--------------------")

	#show Ampere in LED matrix
	msg = str(current)
	w, h = textsize(msg, font=proportional(CP437_FONT))
	x = round((device.width - w) / 2)
	with canvas(device) as draw:
		text(draw, (x, 0), msg, fill="white", font=proportional(CP437_FONT))
	
	time.sleep(1)

# Changing power alarm value to 100 W
# master.execute(1, cst.WRITE_SINGLE_REGISTER, 1, output_value=100)

#try:
    #master.close()
    #if slave.is_open:
        #slave.close()
#except:
   # pass