import os


class Actuator:
    unit = os.getenv("A_UNIT", "C")
    min = float(os.getenv("A_MIN", 0))
    max = float(os.getenv("A_MAX", 30))
    step = float(os.getenv("A_STEP", 0.5))
    state = float(os.getenv("A_STATE", 20))
    active = False

    def start(self):
        print("starting")
        self.active = True

    def stop(self):
        print("stopping")
        self.active = False
