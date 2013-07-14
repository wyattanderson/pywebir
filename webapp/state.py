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

    def btn_cool(self):
        self.mode = Mode.Cool

    def btn_eco(self):
        self.mode = Mode.Eco

    def btn_fan(self):
        self.mode = Mode.Fan

    def btn_fan_faster(self):
        self.fan_speed = min(self.fan_speed + 1, FanSpeed.High)

    def btn_fan_slower(self):
        self.fan_speed = max(self.fan_speed - 1, FanSpeed.Low)

    def btn_power(self):
        self.power = not self.power

    def btn_temp_up(self):
        if self.mode == Mode.Fan:
            return
        self.temperature += 1

    def btn_temp_down(self):
        if self.mode == Mode.Fan:
            return
        self.temperature -= 1

    def apply_button(self, button):
        button_slug = re.sub(r'[^a-z]', r'_', button)
        fn = getattr(self, 'btn_' + button_slug)
        if button_slug != 'power' and not self.power:
            return

        if fn:
            fn()

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

class FanSpeed:
    Low, Medium, High = range(3)

class Mode:
    Eco, Cool, Fan = range(3)
