from time import sleep

from evdev import InputEvent, InputDevice, UInput, ecodes as e

EVENT_ID = 5
BUTTONS = {
    'A': e.BTN_SOUTH
}

real_controller = InputDevice(f'/dev/input/event{EVENT_ID}')
print("Real Controller Info:", real_controller.info)

# Values for vendor, product and bustype mimic xbox controllers
def make_controller(name):
    return UInput.from_device(
        real_controller,
        name='Microsoft X-Box 360 pad',
        vendor=0x045e,
        product=0x028e,
        version=110,
        bustype=3,
        devnode='/dev/uinput',
        phys='py-evdev-uinput-1'
    )

ui1 = make_controller('k1')
ui2 = make_controller('k2')

def press(ui, btn):
    ui.write(e.EV_KEY, btn, 1)
    ui.syn()

def release(ui, btn):
    ui.write(e.EV_KEY, btn, 0)
    ui.syn()

def test_ui(sleep_duration=0.5):
    # Pressing
    print('Device 1, Pressing A')
    press(ui1, BUTTONS['A'])
    sleep(sleep_duration)

    print('Device 2, Pressing A')
    press(ui2, BUTTONS['A'])
    sleep(sleep_duration)

    # Releasing
    print('Device 1, Releasing A')
    release(ui1, BUTTONS['A'])
    sleep(sleep_duration)

    print('Device 2, Releasing A')
    release(ui2, BUTTONS['A'])
    sleep(sleep_duration)

    print()

while True:
    test_ui()

