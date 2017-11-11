from collections import OrderedDict

import grapefruit
from kivy.lang.builder import Builder
from kivy.uix.gridlayout import GridLayout
from kivy.properties import (ObjectProperty,
                             StringProperty)
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput


Builder.load_file('lookup.kv')


class LookupScreen(Screen):
    color_name = StringProperty(('<COLOR NAME>'))
    color = ObjectProperty()

    def __init__(self, **kwargs):
        self.color = grapefruit.Color((0, 0, 0))
        super().__init__(**kwargs)
        displays = [('Hex', [self.color.html]), ('sRGB', self.color.ints),
                    ('HSL', self.color.hsl), ('HSV', self.color.hsv),
                    ('YIQ', self.color.yiq), ('YUV', self.color.yuv),
                    ('CIE-XYZ', self.color.xyz), ('CIE-LAB', self.color.lab),
                    ('CMY', self.color.cmy), ('CMYK', self.color.cmyk)]
        self.color_values = OrderedDict(displays)
        for color_space, value in self.color_values.items():
            self.ids.value_grid.add_widget(
                ValueDisplay(self, color_space, value))

    def on_color(self, instance, color):
        for value_display in self.ids.value_grid.children:
            if value_display.color_space == 'Hex':
                value_display.value = [self.color.html]
            elif value_display.color_space == 'sRGB':
                value_display.value = list(self.color.ints)
            elif value_display.color_space == 'HSL':
                value_display.value = list(self.color.hsl)
            elif value_display.color_space == 'HSV':
                value_display.value = list(self.color.hsv)
            elif value_display.color_space == 'YIQ':
                value_display.value = list(self.color.yiq)
            elif value_display.color_space == 'YUV':
                value_display.value = list(self.color.yuv)
            elif value_display.color_space == 'CIE-XYZ':
                value_display.value = list(self.color.xyz)
            elif value_display.color_space == 'CIE-LAB':
                value_display.value = list(self.color.lab)
            elif value_display.color_space == 'CMY':
                value_display.value = list(self.color.cmy)
            elif value_display.color_space == 'CMYK':
                value_display.value = list(self.color.cmyk)
            value_display.update_inputs()


class ValueDisplay(GridLayout):
    def __init__(self, lookup_screen, color_space, value, **kwargs):
        self.color_space = color_space
        self.lookup_screen = lookup_screen
        self.value = list(value)
        super().__init__(**kwargs)
        self.value_inputs = []
        for index in range(len(self.value)):
            if self.color_space == 'Hex':
                value_input = ValueInput(0, width=90, input_filter=None)
            else:
                value_input = ValueInput(index)
            value_input.text = value_input.format_value(self.value[index])
            self.add_widget(value_input)
            self.value_inputs.append(value_input)

    def update_inputs(self):
        for value_input in self.value_inputs:
            value_input.text = value_input.format_value(
                self.value[value_input.index])

    def update_color(self):
        if self.color_space == 'Hex':
            self.lookup_screen.color = grapefruit.Color.from_html(*self.value)
        elif self.color_space == 'sRGB':
            self.value = [val / 255 for val in self.value]
            self.lookup_screen.color = grapefruit.Color.from_rgb(*self.value)
        elif self.color_space == 'HSL':
            self.lookup_screen.color = grapefruit.Color.from_hsl(*self.value)
        elif self.color_space == 'HSV':
            self.lookup_screen.color = grapefruit.Color.from_hsv(*self.value)
        elif self.color_space == 'YIQ':
            self.lookup_screen.color = grapefruit.Color.from_yiq(*self.value)
        elif self.color_space == 'YUV':
            self.lookup_screen.color = grapefruit.Color.from_yuv(*self.value)
        elif self.color_space == 'CIE-XYZ':
            self.lookup_screen.color = grapefruit.Color.from_xyz(*self.value)
        elif self.color_space == 'CIE-LAB':
            self.lookup_screen.color = grapefruit.Color.from_lab(*self.value)
        elif self.color_space == 'CMY':
            self.lookup_screen.color = grapefruit.Color.from_cmy(*self.value)
        elif self.color_space == 'CMYK':
            self.lookup_screen.color = grapefruit.Color.from_cmyk(*self.value)
        print(self.lookup_screen.color.is_legal)


class ValueInput(TextInput):
    def __init__(self, index, **kwargs):
        super().__init__(**kwargs)
        self.index = index

    def on_focus(self, instance, focused):
        if (not focused and self.text and self.valid_input() and
                self.text != self.format_value(self.parent.value[self.index])):
            if self.parent.color_space == 'Hex':
                self.parent.value = [self.text]
            else:
                self.parent.value[self.index] = float(self.text)
            self.parent.update_color()
        else:
            self.text = self.format_value(self.parent.value[self.index])

    def valid_input(self):
        if self.parent.color_space == 'Hex':
            if self.text.startswith('#'):
                hex_value = self.text[1:]
            else:
                hex_value = self.text
            if len(hex_value) == 3 or len(hex_value) == 6:
                try:
                    hex_value = int(hex_value, 16)
                except ValueError:
                    return False
            else:
                return False
        elif self.parent.color_space == 'sRGB':
            if not 0 <= float(self.text) <= 255:
                return False
        elif (self.parent.color_space == 'HSV' or
              self.parent.color_space == 'HSL'):
            if self.index == 0:
                if not 0 <= float(self.text) <= 359:
                    return False
            else:
                if not 0 <= float(self.text) <= 1:
                    return False
        elif (self.parent.color_space == 'CMY' or
              self.parent.color_space == 'CMYK'):
            if not 0 <= float(self.text) <= 1:
                return False
        return True

    @staticmethod
    def format_value(val, digits=3):
        if type(val) is str:
            return val
        formatter = '{:.' + str(digits) + 'g}'
        return formatter.format(round(val, digits) + 0)
