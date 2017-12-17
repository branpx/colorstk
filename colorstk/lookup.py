from collections import deque
import json
import random
import re

import grapefruit
from kivy.app import App
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.lang.builder import Builder
from kivy.properties import (BooleanProperty,
                             ListProperty,
                             NumericProperty,
                             ObjectProperty,
                             StringProperty)
from kivy.uix.behaviors.knspace import knspace, KNSpaceBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget


Builder.load_file('lookup.kv')


class LookupScreen(KNSpaceBehavior, BoxLayout, Screen):
    named_colors = {value: name for name, value in
                    grapefruit.NAMED_COLOR.items()}
    color = ObjectProperty()
    color_name = StringProperty()
    websafe_color = ObjectProperty()
    greyscale_color = ObjectProperty()
    complementary_color = ObjectProperty()
    ryb_hue = NumericProperty()
    white_point = ListProperty()
    scheme_mode = StringProperty()
    color_spaces = ListProperty()
    detach_values = BooleanProperty()

    def __init__(self, **kwargs):
        config = App.get_running_app().config
        white_point_name = config.get('color', 'white_point')
        observer_angle = config.get('color', 'observer_angle')
        self.set_white_point(white_point_name, observer_angle)
        self.scheme_mode = config.get('color', 'scheme_mode').lower()
        self.color_spaces = json.loads(config.get('ui', 'color_spaces'))
        self.detach_values = int(config.get('ui', 'detach_values'))
        self.history = deque(maxlen=30)
        self.history_next = []
        self.color = grapefruit.Color((0, 0, 0), wref=self.white_point)
        self.set_color_info()
        super(LookupScreen, self).__init__(**kwargs)
        self.value_view = Factory.ValueView()
        self.tabbed_panel = TabbedPanel()
        self.info_tab = Factory.InfoTab()
        self.schemes_tab = Factory.SchemesTab()
        self.tools_tab = Factory.ToolsTab()
        self.load_content()
        self.load_value_displays()
        self.make_schemes()

    def on_color(self, instance, color):
        if not self.color.is_legal:
            return
        for value_display in self.value_view.ids.value_grid.children:
            value_display.value = self.get_value(value_display.color_space)
            value_display.update_inputs()
        self.set_color_info()
        self.make_schemes()

    def get_value(self, color_space):
            if color_space == 'Hex':
                return [self.color.html]
            elif color_space == 'sRGB':
                return list(self.color.ints)
            elif color_space == 'HSL':
                return list(self.color.hsl)
            elif color_space == 'HSV':
                return list(self.color.hsv)
            elif color_space == 'YIQ':
                return list(self.color.yiq)
            elif color_space == 'YUV':
                return list(self.color.yuv)
            elif color_space == 'CIE-XYZ':
                return list(self.color.xyz)
            elif color_space == 'CIE-LAB':
                return list(self.color.lab)
            elif color_space == 'CMY':
                return list(self.color.cmy)
            elif color_space == 'CMYK':
                return list(self.color.cmyk)

    def set_color_info(self):
        self.color_name = self.named_colors.get(self.color.html, 'N/A')
        self.websafe_color = grapefruit.Color(
            self.color.websafe, wref=self.white_point)
        self.greyscale_color = grapefruit.Color(
            self.color.greyscale, wref=self.white_point)
        self.complementary_color = self.color.complementary_color()
        self.ryb_hue = round(grapefruit.rgb_to_ryb(self.color.hsl_hue), 3)

    def make_schemes(self):
        for color_box, color in zip(
                self.schemes_tab.ids.monochrome_grid.children,
                self.color.make_monochrome_scheme()):
            color_box.color = color
        for color_box, color in zip(
                self.schemes_tab.ids.triadic_grid.children,
                self.color.make_triadic_scheme(mode=self.scheme_mode)):
            color_box.color = color
        for color_box, color in zip(
                self.schemes_tab.ids.tetradic_grid.children,
                self.color.make_tetradic_scheme(mode=self.scheme_mode)):
            color_box.color = color
        for color_box, color in zip(
                self.schemes_tab.ids.analogous_grid.children,
                self.color.make_analogous_scheme(mode=self.scheme_mode)):
            color_box.color = color

    def on_color_spaces(self, instance, color_spaces):
        self.value_view.ids.value_grid.clear_widgets()
        self.load_value_displays()

    def load_value_displays(self):
        for color_space in self.color_spaces:
            self.value_view.ids.value_grid.add_widget(
                ValueDisplay(color_space))

    def on_detach_values(self, instance, detach_values):
        self.tabbed_panel.clear_widgets()
        self.tabbed_panel.clear_tabs()
        self.ids.content.clear_widgets()
        self.load_content()

    def load_content(self):
        if not self.detach_values:
            self.value_view.background_color[3] = 0
            values_tab = TabbedPanelItem(
                text='Values', content=self.value_view)
            self.tabbed_panel.add_widget(values_tab)
            self.tabbed_panel.switch_to(values_tab)
        self.tabbed_panel.add_widget(self.info_tab)
        self.tabbed_panel.add_widget(self.schemes_tab)
        self.tabbed_panel.add_widget(self.tools_tab)
        if self.detach_values:
            self.value_view.background_color[3] = 1
            self.ids.content.add_widget(self.value_view)
            self.tabbed_panel.switch_to(self.info_tab)
        self.ids.content.add_widget(self.tabbed_panel)

    def set_color(self, value):
        self.color = grapefruit.Color(tuple(value), wref=self.white_point)

    def set_white_point(self, name, observer):
        if observer == 'CIE 1931':
            name = 'std_' + name
        elif observer == 'CIE 1964':
            name = 'sup_' + name
        self.white_point = grapefruit.WHITE_REFERENCE[name]

    def random_color(self):
        self.add_to_history(self.color)
        self.color = grapefruit.Color(tuple(random.random() for _ in range(3)))

    def blend_colors(self):
        blend_color1 = self.tools_tab.ids.color_select1.color
        blend_color2 = self.tools_tab.ids.color_select2.color
        if blend_color1.alpha and blend_color2.alpha:
            self.add_to_history(self.color)
            self.color = blend_color1.blend(blend_color2)

    def add_to_palette(self):
        knspace.palettes_screen.mode = 'add'
        App.get_running_app().root.current = 'palettes'

    def add_to_history(self, color, next_disable=True):
        self.history.append(color)
        self.ids.prev_button.disabled = False
        if next_disable:
            del self.history_next[:]
            self.ids.next_button.disabled = True

    def previous_color(self):
        if len(self.history):
            self.history_next.append(self.color)
            self.ids.next_button.disabled = False
            self.color = self.history.pop()
            if not self.history:
                self.ids.prev_button.disabled = True

    def next_color(self):
        if len(self.history_next):
            self.history.append(self.color)
            self.ids.prev_button.disabled = False
            self.color = self.history_next.pop()
            if not self.history_next:
                self.ids.next_button.disabled = True


class ValueDisplay(GridLayout):
    color_space = StringProperty()
    value = ListProperty()
    value_inputs = ListProperty()

    def __init__(self, color_space, **kwargs):
        super(ValueDisplay, self).__init__(**kwargs)
        self.color_space = color_space
        self.value = knspace.lookup_screen.get_value(color_space)
        for index in range(len(self.value)):
            if self.color_space == 'Hex':
                value_input = ValueInput(0, self.color_space, width='90dp')
            else:
                value_input = ValueInput(index, self.color_space)
            value_input.text = value_input.format_value(self.value[index])
            self.add_widget(value_input)
            self.value_inputs.append(value_input)

    def update_inputs(self):
        for value_input in self.value_inputs:
            value_input.text = value_input.format_value(
                self.value[value_input.index])
            value_input.scroll_x = 0

    def update_color(self):
        lookup_screen = knspace.lookup_screen
        white_point = lookup_screen.white_point
        lookup_screen.add_to_history(lookup_screen.color, next_disable=False)
        if self.color_space == 'Hex':
            lookup_screen.color = grapefruit.Color.from_html(
                *self.value, wref=white_point)
        elif self.color_space == 'sRGB':
            self.value = [val / 255 for val in self.value]
            lookup_screen.color = grapefruit.Color.from_rgb(
                *self.value, wref=white_point)
        elif self.color_space == 'HSL':
            lookup_screen.color = grapefruit.Color.from_hsl(
                *self.value, wref=white_point)
        elif self.color_space == 'HSV':
            lookup_screen.color = grapefruit.Color.from_hsv(
                *self.value, wref=white_point)
        elif self.color_space == 'YIQ':
            lookup_screen.color = grapefruit.Color.from_yiq(
                *self.value, wref=white_point)
        elif self.color_space == 'YUV':
            lookup_screen.color = grapefruit.Color.from_yuv(
                *self.value, wref=white_point)
        elif self.color_space == 'CIE-XYZ':
            lookup_screen.color = grapefruit.Color.from_xyz(
                *self.value, wref=white_point)
        elif self.color_space == 'CIE-LAB':
            lookup_screen.color = grapefruit.Color.from_lab(
                *self.value, wref=white_point)
        elif self.color_space == 'CMY':
            lookup_screen.color = grapefruit.Color.from_cmy(
                *self.value, wref=white_point)
        elif self.color_space == 'CMYK':
            lookup_screen.color = grapefruit.Color.from_cmyk(
                *self.value, wref=white_point)
        if lookup_screen.color.is_legal:
            del lookup_screen.history_next[:]
        else:
            lookup_screen.previous_color()
            lookup_screen.history_next.pop()
        if not lookup_screen.history_next:
            lookup_screen.ids.next_button.disabled = True


class ValueInput(TextInput):
    hex_pat = re.compile(u'^#?[0-9A-Fa-f]*$')
    float_pat = re.compile(u'^-?[0-9]*\\.?[0-9]*$')
    index = NumericProperty()

    def __init__(self, index, color_space, **kwargs):
        super(ValueInput, self).__init__(**kwargs)
        self.index = index
        if color_space in ('sRGB', 'HSV', 'HSL', 'CMY', 'CMYK'):
            self.input_filter = 'float'

    def on_focus(self, instance, focused):
        if not focused:
            if (self.text and self.text != self.format_value(
                    self.parent.value[self.index]) and self.valid_input()):
                self.parent.value[self.index] = self.value
                self.parent.update_color()
            else:
                self.text = self.format_value(self.parent.value[self.index])
                self.scroll_x = 0

    def insert_text(self, substring, from_undo=False):
        cursor_col = self.cursor[0]
        new_text = self.text[:cursor_col] + substring + self.text[cursor_col:]
        if self.parent.color_space == 'Hex':
            if not re.match(self.hex_pat, new_text):
                return
        elif self.parent.color_space in ('YIQ', 'YUV', 'CIE-XYZ', 'CIE-LAB'):
            if not re.match(self.float_pat, new_text):
                return
        return super(ValueInput, self).insert_text(
            substring, from_undo=from_undo)

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
        return True

    @property
    def value(self):
        try:
            value = float(self.text)
        except ValueError:
            return self.text
        if self.parent.color_space == 'sRGB':
            if value < 0:
                return 0
            elif value > 255:
                return 255
        elif (self.parent.color_space == 'HSV' or
              self.parent.color_space == 'HSL'):
            if self.index == 0:
                if value < 0:
                    return 0
                elif value > 359:
                    return 359
            else:
                if value < 0:
                    return 0
                elif value > 1:
                    return 1
        elif (self.parent.color_space == 'CMY' or
              self.parent.color_space == 'CMYK'):
            if value < 0:
                return 0
            elif value > 1:
                return 1
        return value

    @staticmethod
    def format_value(val, digits=3):
        if type(val) is str:
            return val
        formatter = '{:.' + str(digits) + 'g}'
        return formatter.format(round(val, digits) + 0)


class ColorBox(Widget):
    color = ObjectProperty((0, 0, 0, 0))

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            lookup_screen = knspace.lookup_screen
            lookup_screen.add_to_history(lookup_screen.color)
            lookup_screen.color = self.color


class ColorSelectBox(Widget):
    color = ObjectProperty(grapefruit.Color((0, 0, 0), alpha=0))

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            touch.grab(self)
            clock_event = Clock.schedule_once(self.view_color, 1)
            touch.ud['view_color'] = clock_event

    def on_touch_move(self, touch):
        if touch.grab_current is self and not self.collide_point(*touch.pos):
            Clock.unschedule(touch.ud.get('view_color'))

    def on_touch_up(self, touch):
        Clock.unschedule(touch.ud.get('view_color'))
        if touch.grab_current is self and self.collide_point(*touch.pos):
            self.color = knspace.lookup_screen.color
        touch.ungrab(self)

    def view_color(self, dt):
        if self.color.alpha:
            lookup_screen = knspace.lookup_screen
            lookup_screen.add_to_history(lookup_screen.color)
            lookup_screen.color = self.color
