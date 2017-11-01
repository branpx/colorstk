from kivy.lang.builder import Builder
from kivy.properties import (ListProperty,
                             StringProperty)
from kivy.uix.screenmanager import Screen
from kivy.uix.stacklayout import StackLayout
from kivy.uix.textinput import TextInput


Builder.load_file('lookup.kv')


class LookupScreen(Screen):
    rgbhex = ListProperty(('#', 'ffffff'))
    srgb = ListProperty(('sRGB', 1, 1, 1))
    hsl = ListProperty(('HSL', 0, 0, 0))
    hsv = ListProperty(('HSV', 0, 0, 0))
    yiq = ListProperty(('YIQ', 0, 0, 0))
    yuv = ListProperty(('YUV', 0, 0, 0))
    ryb = ListProperty(('RYB', 0, 0, 0))
    cie_xyz = ListProperty(('CIE-XYZ', 0, 0, 0))
    cie_lab = ListProperty(('CIE-LAB', 0, 0, 0))
    cmy = ListProperty(('CMY', 0, 0, 0))
    cmyk = ListProperty(('CMYK', 0, 0, 0, 0))
    color_name = StringProperty(('<COLOR NAME>'))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        values = [self.srgb, self.hsl, self.hsv,
                  self.yiq, self.yuv, self.ryb, self.cie_xyz,
                  self.cie_lab, self.cmy, self.cmyk]
        for value in values:
            self.ids.value_stack.add_widget(ValueDisplay(value))

    def update(self):
        pass

    def on_srgb(self, instance, value):
        pass

    def on_hsl(self, instance, value):
        pass

    def on_hsv(self, instance, value):
        pass

    def on_yiq(self, instance, value):
        pass

    def on_yuv(self, instance, value):
        pass

    def on_ryb(self, instance, value):
        pass

    def on_cie_xyz(self, instance, value):
        pass

    def on_cie_lab(self, instance, value):
        pass

    def on_cmy(self, instance, value):
        pass

    def on_cmyk(self, instance, value):
        pass


class ValueDisplay(StackLayout):
    def __init__(self, value, **kwargs):
        super().__init__(**kwargs)
        self.ids.value_label.text = value[0]
        for num in range(1, len(value)):
            self.add_widget(ValueInput(value, num))


class ValueInput(TextInput):
    def __init__(self, value, index, **kwargs):
        super().__init__(**kwargs)
        self.value = value
        self.index = index
        self.text = str(value[index])

    def on_focus(self, instance, focused):
        if (not focused and self.text and
            float(self.text) != self.value[self.index]):
            self.value[self.index] = float(self.text)
        self.text = str(self.value[self.index])

    def is_valid(self):
        pass
