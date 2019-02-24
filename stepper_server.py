import socket
import _thread
from stepper import Stepper_28BYJ
import ssd1306
import machine
import time
#pins0 = [25,26,2,14] Conflict with I2C
#pins1 = [16,5,4,0]
pins0 = [25,26,12,13]
pins1 = [16,0,2,14]


def process_command(data,motors):
    pass
def display_thread(motors):
    i2c = machine.I2C(scl=machine.Pin(4), sda=machine.Pin(5))
    oled = ssd1306.SSD1306_I2C(128, 64, i2c)
    while True:
        oled.fill(0)
        oled.text('P0= '+str(motors[0].get_position()), 0, 0)
        oled.text('P1= ' + str(motors[1].get_position()), 0, 10)
        oled.show()
        time.sleep_ms(1000)
def main():
    min_period = 2
    m1 = Stepper_28BYJ(pins0,None,5)
    m2 = Stepper_28BYJ(pins1,None,5)
    motors = [m1,m2]
    _thread.start_new_thread(display_thread,(motors,))
    addr = socket.getaddrinfo('0.0.0.0',80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)

    while True:
        #try:
        cl,addr  = s.accept()
        while True:
            cl_file = cl.makefile('rwb',0)
            data = cl_file.readline()
            if len(data) == 0:
                cl_file.close()
                cl.close()
                break
            if len(data)>100:
                data = data[:100]
            data = data[:-2].decode('latin').split(' ')
            cmd = data[0]
            try:
                if cmd == 'GOTO' and len(data)>=3:
                        motor_no = int(data[1])
                        if motor_no>len(motors):
                            raise ValueError
                        pos = int(data[2])
                        motors[motor_no].goto(pos)
                elif cmd == 'POSITION' and len(data) >= 2:
                    motor_no = int(data[1])
                    if motor_no > len(motors):
                        raise ValueError
                    cl_file.write(str(motors[motor_no].get_position()).encode('latin')+b'\r\n')
                elif cmd == 'ZERO' and len(data) >= 2:
                    motor_no = int(data[1])
                    if motor_no > len(motors):
                        raise ValueError
                    if len(data)>=3:
                        zero = int(data[2])
                    else:
                        zero = None
                    motors[motor_no].set_zero(zero)
                elif cmd == 'SPEED' and len(data) >= 3:
                    motor_no = int(data[1])
                    if motor_no > len(motors):
                        raise ValueError
                    timer_period = int(data[2])
                    if timer_period<min_period:
                        raise ValueError
                    motors[motor_no].set_speed(timer_period)
                elif cmd == 'READY':
                    ready = all([m.ready() for m in motors])
                    ready = str(int(ready)).encode('latin')
                    cl_file.write(ready + b'\r\n')
            except ValueError:
                continue
        # except :
        #     print('Unhandled expection, closing server')
        #     s.close()
        #     return