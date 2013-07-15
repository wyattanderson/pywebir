import re

class ACState:
    def __init__(self):
        self.power = False
        self.temperature = 75
        self.fan_speed = FanSpeed.High
        self.mode = Mode.Fan
        self.auto = False

    def btn_auto(self):
        self.auto = not self.auto
        return True

    def btn_cool(self):
        changed = self.mode != Mode.Cool
        self.mode = Mode.Cool
        return changed

    def btn_eco(self):
        changed = self.mode != Mode.Eco
        self.mode = Mode.Eco
        return changed

    def btn_fan(self):
        changed = self.mode != Mode.Fan
        self.mode = Mode.Fan
        return changed

    def btn_fan_faster(self):
        new_speed = min(self.fan_speed + 1, FanSpeed.High)
        changed = self.fan_speed != new_speed
        self.fan_speed = new_speed
        return changed

    def btn_fan_slower(self):
        new_speed = max(self.fan_speed - 1, FanSpeed.Low)
        changed = self.fan_speed != new_speed
        self.fan_speed = new_speed
        return changed

    def btn_power(self):
        self.power = not self.power
        return True

    def btn_temp_up(self):
        if self.mode == Mode.Fan:
            return False
        self.temperature += 1
        return True

    def btn_temp_down(self):
        if self.mode == Mode.Fan:
            return False
        self.temperature -= 1
        return True

    def apply_button(self, button):
        button_slug = re.sub(r'[^a-z]', r'_', button)
        fn = getattr(self, 'btn_' + button_slug)
        if button_slug != 'power' and not self.power:
            return False

        if fn:
            return fn()

    def export(self):
        return dict([
            (key, getattr(self, key)) for key in [
                'power',
                'temperature',
                'fan_speed',
                'mode',
                'auto'
                ]
            ])

    def unexport(self, values):
        for key, value in values.iteritems():
            if hasattr(self, key):
                setattr(self, key, value)

class FanSpeed:
    Low, Medium, High = range(3)

class Mode:
    Eco, Cool, Fan = range(3)
