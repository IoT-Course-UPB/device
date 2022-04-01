import os


class Actuator:
    unit = os.getenv("A_UNIT", "C")
    binary = float(os.getenv("A_BIN", 0))  # 1 if values can only be binary
    state_0 = os.getenv("A_STATE0", "off")  # off state if binary
    state_1 = os.getenv("A_STATE1", "on")  # on state if binary
    min = float(os.getenv("A_MIN", 0))  # min value if non-binary
    max = float(os.getenv("A_MAX", 30))  # max value if non-binary
    name = str(os.getenv("D_NAME")) + '_a'
    active = False

    if (binary == 1):
        state = state_0
    else:
        state = min

    def start(self):
        if (self.active == False):
            print("Actuator of device " + self.name + " starting")
            self.active = True
        else:
            print("Actuator of device " + self.name + " already started")

    def stop(self):
        if (self.active == True):
            print("Actuator of device " + self.name + " stopping")
            self.active = False
        else:
            print("Actuator of device " + self.name + " already stopped")

    def get_status(self):
        data = {'name': self.name, 'state': self.state,
                'unit': self.unit, 'active': self.active}
        return data

    def set_state(self, value):
        if (self.binary == 1):
            if (float(value) == 0):
                self.state = self.state_0
            else:
                self.state = self.state_1
        else:
            val = float(value)
            if (val < self.min or val > self.max):
                return False
            else:
                self.state = val
                return True
