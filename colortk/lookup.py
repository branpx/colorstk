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
    srgb = ListProperty((1, 1, 1))
    #hsl = ListProperty((0, 0, 0))
    #hsv = ListProperty((0, 0, 0))
    #yiq = ListProperty((0, 0, 0))
    #yuv = ListProperty((0, 0, 0))
    #cie_xyz = ListProperty((0, 0, 0))
    #cie_lab = ListProperty((0, 0, 0))
    #cmy = ListProperty((0, 0, 0))
    #cmyk = ListProperty((0, 0, 0, 0))
    color_name = StringProperty(('<COLOR NAME>'))
    #color_values = ObjectProperty(OrderedDict(sRGB=srgb,
    #                                          HSL=[0, 0, 0],
    #                                          HSV=[0, 0, 0],
    #                                          YIQ=[0, 0, 0],
    #                                          YUV=[0, 0, 0],
    #                                          CIE_XYZ=[0, 0, 0],
    #                                          CIE_LAB=[0, 0, 0],
    #                                          CMY=[0, 0, 0],
    #                                          CMYK=[0, 0, 0, 0]))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color_values = OrderedDict(sRGB=self.srgb,
                                        HSL=[0, 0, 0],
                                        HSV=[0, 0, 0],
                                        YIQ=[0, 0, 0],
                                        YUV=[0, 0, 0],
                                        CIE_XYZ=[0, 0, 0],
                                        CIE_LAB=[0, 0, 0],
                                        CMY=[0, 0, 0],
                                        CMYK=[0, 0, 0, 0])
        self.value_displays = []
        for color_space, value in self.color_values.items():
            value_display = ValueDisplay(value, color_space)
            self.ids.value_stack.add_widget(value_display)
            self.value_displays.append(value_display)

    def on_srgb(self, instance, value):
        self.color_values['HSL'][:] = grapefruit.rgb_to_hsl(*self.srgb)
        self.color_values['HSV'][:] = grapefruit.rgb_to_hsv(*self.srgb)
        self.color_values['YIQ'][:] = grapefruit.rgb_to_yiq(*self.srgb)
        self.color_values['YUV'][:] = grapefruit.rgb_to_yuv(*self.srgb)
        self.color_values['CIE_XYZ'][:] = grapefruit.rgb_to_xyz(*self.srgb)
        self.color_values['CIE_LAB'][:] = grapefruit.xyz_to_lab(
            *self.color_values['CIE_XYZ'])
        self.color_values['CMY'][:] = grapefruit.rgb_to_cmy(*self.srgb)
        self.color_values['CMYK'][:] = grapefruit.cmy_to_cmyk(
            *self.color_values['CMY'])
        for value_display in self.value_displays:
            value_display.update_inputs()


class ValueDisplay(StackLayout):
    def __init__(self, value, color_space, **kwargs):
        super().__init__(**kwargs)
        self.value = value
        self.ids.value_label.text = color_space
        self.value_inputs = []
        for index in range(len(value)):
            value_input = ValueInput(value, index)
            self.add_widget(value_input)
            self.value_inputs.append(value_input)

    def update_inputs(self):
        for value_input in self.value_inputs:
            value_input.text = str(value_input.value[value_input.index])


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
