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
    color_name = StringProperty(('<COLOR NAME>'))
    color = ObjectProperty()

    def __init__(self, **kwargs):
        self.color = grapefruit.Color((1, 1, 1))
        super().__init__(**kwargs)
        displays = [('sRGB', self.color.rgb), ('HSL', self.color.hsl),
                    ('HSV', self.color.hsv), ('YIQ', self.color.yiq),
                    ('YUV', self.color.yuv), ('CIE-XYZ', self.color.xyz),
                    ('CIE-LAB', self.color.lab), ('CMY', self.color.cmy),
                    ('CMYK', self.color.cmyk)]
        self.color_values = OrderedDict(displays)
        for color_space, value in self.color_values.items():
            self.ids.value_stack.add_widget(
                ValueDisplay(self, color_space, value))

    def on_color(self, instance, color):
        for value_display in self.ids.value_stack.children:
            if value_display.color_space == 'sRGB':
                value_display.value = list(self.color.rgb)
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


class ValueDisplay(StackLayout):
    def __init__(self, lookup_screen, color_space, value, **kwargs):
        self.color_space = color_space
        self.color = lookup_screen.color
        self.lookup_screen = lookup_screen
        self.value = list(value)
        super().__init__(**kwargs)
        self.value_inputs = []
        for index in range(len(value)):
            value_input = ValueInput(
                index, text=str(round(self.value[index], 3)))
            self.add_widget(value_input)
            self.value_inputs.append(value_input)

    def update_inputs(self):
        for value_input in self.value_inputs:
            value_input.text = str(round(self.value[value_input.index], 3))

    def update_color(self):
        if self.color_space == 'sRGB':
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
        self.color = self.lookup_screen.color


class ValueInput(TextInput):
    def __init__(self, index, **kwargs):
        super().__init__(**kwargs)
        self.index = index

    def on_focus(self, instance, focused):
        if (not focused and self.text and
            float(self.text) != round(self.parent.value[self.index], 3)):
            self.parent.value[self.index] = float(self.text)
            self.parent.update_color()
        else:
            self.text = str(round(self.parent.value[self.index], 3))
