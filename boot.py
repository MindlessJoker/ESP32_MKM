# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
# import webrepl
# webrepl.start()
import network
w = network.WLAN(network.STA_IF)
w.active(True)
w.connect('Forbidden','*****')
# import uftpd
# uftpd.start()

import machine
# import ssd1306
# i2c = machine.I2C(scl=machine.Pin(4), sda=machine.Pin(5))
# oled = ssd1306.SSD1306_I2C(128,64,i2c)
# oled.fill(0)
# oled.text('Hello',0,0)
# oled.show()