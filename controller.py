from evdev import InputEvent, InputDevice, UInput, ecodes as e
from time import sleep


class Controller:
    def __init__(self, name):
        self.name = name
        self.mapping = {
            'Y': e.BTN_WEST,
            'A': e.BTN_SOUTH,
            'X': e.BTN_NORTH,
            'B': e.BTN_EAST,
        }
        EVENT_ID = 18
        real_controller = InputDevice(f'/dev/input/event{EVENT_ID}')
        self.interface = UInput.from_device(
            real_controller,
            name='Microsoft X-Box 360 pad',
            vendor=0x045e,
            product=0x028e,
            version=110,
            bustype=3,
            devnode='/dev/uinput',
            phys='py-evdev-uinput-1'
        )

    def __repr__(self):
        return f"Controller {self.name}"

    def tabin(self, side):
        if side=="left":
            self.interface.write(1, 310, 1)
        if side=="right":
            self.interface.write(1, 311, 1)
        self.interface.syn()

    def tabout(self, side):
        if side=="left":
            self.interface.write(1, 310, 0)
        if side=="right":
            self.interface.write(1, 311, 0)
        self.interface.syn()

    def triggerin(self, side):
        if side=="left":
            self.interface.write(3, 2, 255)
        if side=="right":
            self.interface.write(3, 5, 255)
        self.interface.syn()

    def triggerout(self, side):
        if side=="left":
            self.interface.write(3, 2, 0)
        if side=="right":
            self.interface.write(3, 5, 0)
        self.interface.syn()

    def btnin(self, btn):
        self.interface.write(e.EV_KEY, self.mapping[btn], 1)
        self.interface.syn()

    def btnout(self, btn):
        self.interface.write(e.EV_KEY, self.mapping[btn], 0)
        self.interface.syn()

    def joystick(self, direction, side):
        """
        Send signal to controller based on X and Y displacement from center
        Args:
            direction: "up", "down", "left", "right", "upleft", "upright", "downleft", "downright"
            side: "left" or "right", indicating joystick
        Returns:
            null
        """
        # Code 0 is for X, Code 1 is for Y
        # Write(event type, code, value)
        x = 0
        y = 0
        if "down" in direction:
            y = -32767
        if "up" in direction:
            y = 32767
        if "left" in direction:
            x = -32767
        if "right" in direction:
            x = 32767
        if "stop" in direction:
            x, y = (0, 0)
        if side=="left":
            self.interface.write(3,0,x)
            self.interface.write(3,1,y)
        else:
            self.interface.write(3,3,x)
            self.interface.write(3,4,y)
        self.interface.syn()

    def test(self):
        print(f"Doing tests for f{self.name}")
        print("Holding X for 1.0 seconds")
        self.btnin("X")
        sleep(1.0)
        self.btnout("X")
        print("Holding Y for 1.0 seconds")
        self.btnin("Y")
        sleep(1.0)
        self.btnout("Y")
        print("Holding A for 1.0 seconds")
        self.btnin("A")
        sleep(1.0)
        self.btnout("A")
        print("Holding B for 1.0 seconds")
        self.btnin("B")
        sleep(1.0)
        self.btnout("B")
        print("Left Joy Left 1.0s")
        self.joystick(-1,0,"left")
        sleep(1.0)
        print("Left Joy Right 1.0s")
        self.joystick(1,0,"left")
        sleep(1.0)
        print("Left Joy Up 1.0s")
        self.joystick(0,1,"left")
        sleep(1.0)
        print("Left Joy Down 1.0s")
        self.joystick(0,-1,"left")
        sleep(1.0)
        self.joystick(0,0,"left")
        print("Right Joy Left 1.0s")
        self.joystick(-1,0,"right")
        sleep(1.0)
        print("Right Joy Right 1.0s")
        self.joystick(1,0,"right")
        sleep(1.0)
        print("Right Joy Up 1.0s")
        self.joystick(0,1,"right")
        sleep(1.0)
        print("Right Joy Down 1.0s")
        self.joystick(0,-1,"right")
        sleep(1.0)
        self.joystick(0,0,"right")
        print("Left Tab In 1.0s")
        self.tabin("left")
        sleep(1.0)
        self.tabout("left")
        print("Right Tab In 1.0s")
        self.tabin("right")
        sleep(1.0)
        self.tabout("right")
        print("Left Trigger In 1.0s")
        self.triggerin('left')
        sleep(1.0)
        self.triggerout('left')
        print("Right Trigger In 1.0s")
        self.triggerin('right')
        sleep(1.0)
        self.triggerout('right')
        self.interface.close()


if __name__=="__main__":
    controller_one = Controller("One")
    controller_one.test()
