import asyncio, evdev

@asyncio.coroutine
def print_events(device):
    while True:
        events = yield from device.async_read()
        for event in events:
            print(device.path, evdev.categorize(event), event, sep=': ')

print(evdev.list_devices())
devices = [evdev.InputDevice(path) for path in evdev.list_devices()]

for device in devices:
    asyncio.async(print_events(device))

loop = asyncio.get_event_loop()
loop.run_forever()
