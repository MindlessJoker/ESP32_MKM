import machine
import time
import _thread

class Stepper_28BYJ():
    def set_speed(self,step_period):
        self.step_period = step_period
        if self.timer is not None:
            self.timer.init(period=step_period,mode=machine.Timer.PERIODIC,callback=self.stepper_callback)
    def __init__(self,pins,timer_no=None,step_period=10):
        assert isinstance(pins,list)
        assert len(pins) == 4
        if isinstance(pins[0],int):
            pins = [machine.Pin(x,machine.Pin.OUT) for x in pins]
        self.pins = pins
        self.position = 0
        self.goto_position = 0
        self.zero_position = 0
        self.step_period = step_period
        if timer_no is not None:
            self.attached_steppers = [self]
            self.init_timer(timer_no)
        else:
            self.timer = None
            _thread.start_new_thread(self.thread_fun,())
    def init_timer(self,idx):
        self.timer = machine.Timer(idx)
        self.set_speed(self.step_period)
    def goto(self,new_position):
        self.goto_position = self.zero_position+new_position
    def get_position(self):
        return self.position-self.zero_position
    def ready(self):
        return self.position == self.goto_position
    def set_step(self,i):
        state = i&0x7 #i%8
        pin_value = 0
        pin_value+= (1<<(state>>1))
        if state & 0x1:
            pin_value += (1 << (((state+1)&0x07) >> 1))
        p = self.pins
        for i in range(4):
            p[i].value(0x01&(pin_value>>i))
    def set_zero(self,zero=None):
        #TODO: get rid of interrupt-conflict
        if zero is None:
            zero = self.position-self.zero_position
        self.zero_position +=zero
    def stepper_callback(self,_=None):
        pos = self.position
        gtp = self.goto_position
        if pos!=gtp:
            if pos>gtp:
                self.position-=1
            else:
                self.position+=1
            self.set_step(self.position)
    def thread_fun(self):
        print('Stepper thread started')
        while True:
            if self.position == self.goto_position:
                time.sleep_ms(50)
            else:
                self.stepper_callback()
                time.sleep_ms(self.step_period)


def timeit(fun,*args):
    t0 = time.ticks_us()
    fun(*args)
    t0 = time.ticks_us() - t0
    print(t0)