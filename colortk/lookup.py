from collections import OrderedDict

import grapefruit
from kivy.lang.builder import Builder
from kivy.properties import (DictProperty,
                             ListProperty,
                             NumericProperty,
                             ObjectProperty,
                             ReferenceListProperty,
                             StringProperty)
from kivy.uix.screenmanager import Screen
from kivy.uix.stacklayout import StackLayout
from kivy.uix.textinput import TextInput


Builder.load_file('lookup.kv')


class LookupScreen(Screen):
    rgbhex = ListProperty(('ffffff'))
    srgb = ListProperty()
    color_name = StringProperty(('<COLOR NAME>'))

    def __init__(self, **kwargs):
        self.color = grapefruit.Color((1, 1, 1))
        self.srgb = list(self.color.rgb)
        super().__init__(**kwargs)
        self.color_values = OrderedDict(sRGB=self.srgb,
                                        HSL=self.color.hsl,
                                        HSV=self.color.hsv,
                                        YIQ=self.color.yiq,
                                        YUV=self.color.yuv,
                                        CIE_XYZ=self.color.xyz,
                                        CIE_LAB=self.color.lab,
                                        CMY=self.color.cmy,
                                        CMYK=self.color.cmyk)
        self.value_displays = []
        for color_space, value in self.color_values.items():
            value_display = ValueDisplay(self.color, value, color_space)
            self.ids.value_stack.add_widget(value_display)
            self.value_displays.append(value_display)


class ValueDisplay(StackLayout):
    value_displays = []

    def __init__(self, color, value, color_space, **kwargs):
        super().__init__(**kwargs)
        self.value_displays.append(self)
        self.color = color
        if color_space == 'sRGB':
            self.value = value
        else:
            self.value = list(value)
        self.color_space = color_space
        self.ids.value_label.text = color_space
        self.value_inputs = []
        for index in range(len(value)):
            value_input = ValueInput(index, text=str(self.value[index]))
            self.add_widget(value_input)
            self.value_inputs.append(value_input)

    def update_inputs(self):
        for value_input in self.value_inputs:
            value_input.text = str(self.value[value_input.index])

    def update_color(self):
        if self.color_space == 'sRGB':
            self.color.rgb = self.value
        elif self.color_space == 'HSL':
            self.color.hsl = self.value
        elif self.color_space == 'HSV':
            self.color.hsv = self.value
        elif self.color_space == 'YIQ':
            self.color.yiq = self.value
        elif self.color_space == 'YUV':
            self.color.yuv = self.value
        elif self.color_space == 'CIE_XYZ':
            self.color.xyz = self.value
        elif self.color_space == 'CIE_LAB':
            self.color.lab = self.value
        elif self.color_space == 'CMY':
            self.color.cmy = self.value
        elif self.color_space == 'CMYK':
            self.color.cmyk = self.value
        self.update_values()

    def update_values(self):
        for value_display in self.value_displays:
            if value_display.color_space == 'sRGB':
                value_display.value[:] = list(self.color.rgb)
            elif value_display.color_space == 'HSL':
                value_display.value = list(self.color.hsl)
            elif value_display.color_space == 'HSV':
                value_display.value = list(self.color.hsv)
            elif value_display.color_space == 'YIQ':
                value_display.value = list(self.color.yiq)
            elif value_display.color_space == 'YUV':
                value_display.value = list(self.color.yuv)
            elif value_display.color_space == 'CIE_XYZ':
                value_display.value = list(self.color.xyz)
            elif value_display.color_space == 'CIE_LAB':
                value_display.value = list(self.color.lab)
            elif value_display.color_space == 'CMY':
                value_display.value = list(self.color.cmy)
            elif value_display.color_space == 'CMYK':
                value_display.value = list(self.color.cmyk)
            value_display.update_inputs()


class ValueInput(TextInput):
    def __init__(self, index, **kwargs):
        super().__init__(**kwargs)
        self.index = index

    def on_focus(self, instance, focused):
        if (not focused and self.text and
            float(self.text) != self.parent.value[self.index]):
            self.parent.value[self.index] = float(self.text)
            self.parent.update_color()
        else:
            self.text = str(self.parent.value[self.index])
