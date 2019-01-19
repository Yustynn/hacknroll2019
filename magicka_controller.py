from controller import Controller
import time
from time import sleep
from threading import Timer

class MagickaController:
    def __init__(self, name):
        # We use self.firing as a semaphore; if some other spell is casting, you cannt cast spells
        # jk if we're just using magicks then firing wont matter anymore
        self.Controller = Controller(name)
        self.firing = False

    def joinGame(self):
        sleep(2)
        name = self.Controller.name
        print(f"{name} joining game")
        self.Controller.btnin("A")
        sleep(0.1)
        self.Controller.btnout("A")

    def elementSequence(self, sequence):
        """Casts an element of sequence"""
        for element in sequence:
            self.Controller.btnin(element)
            sleep(0.1)
            self.Controller.btnout(element)
            sleep(0.1)

    def fire(self, direction, duration):
        print("Gandalf Charging....")
        self.firing = True
        # start_time = time.time()
        # while time.time() - start_time < duration:
        self.Controller.joystick(direction, "right")
        time.sleep(2)
        self.firing = False
        self.Controller.joystick("stop", "right")
        print("Gandalf UNLEASH")

    def fireball(self, direction, duration=2.0):
        sequence = ["A", "A", "A", "B", "B"]
        self.elementSequence(sequence)
        self.fire(direction, duration)

    def lightninglaser(self, direction, duration=2.0):
        print("Gandalf building Water")
        self.Controller.tabin("left")
        sequence = ["X", "X"]
        self.elementSequence(sequence)
        self.Controller.tabout("left")
        print("Gandalf building Fire Lightning Arcane")
        sequence = ["A", "A", "X", "Y"]
        time.sleep(0.1)
        self.elementSequence(sequence)
        self.fire(direction, duration)

    def move(self, direction):
        self.Controller.joystick(direction, "left")

    def dragonstrike(self):
        sequence = ["A", "A", "B", "A", "A"]
        self.elementSequence(sequence)
        self.Controller.triggerin("right")
        time.sleep(0.1)
        self.Controller.triggerout("right")

if __name__=="__main__":
    magickaController = MagickaController("Gandalf")
    magickaController.joinGame()
    # magickaController.fireball((1,1))
    magickaController.lightninglaser((-1,-1))
    print("Gandalf moving")
    movements = ["up", "down", "left", "right", "upleft", "upright", "downleft", "downright", "stop"]
    for movement in movements:
        magickaController.move(movement)
        time.sleep(0.5)
