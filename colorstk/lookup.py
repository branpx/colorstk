"""Implements looking up colors."""

from collections import deque
import json
import random
import re

import grapefruit
from kivy.app import App
from kivy.clock import Clock
from kivy.factory import Factory
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


class LookupScreen(KNSpaceBehavior, BoxLayout, Screen):
    """A `Screen` to look up and view colors and their values."""

    # Load named colors from grapefruit as {value: name} pairs
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
    value_range = StringProperty()
    color_spaces = ListProperty()
    detach_values = BooleanProperty()

    def __init__(self, **kwargs):
        """Sets config properties and initializes a `LookupScreen`."""
        # Load initial configuration
        config = App.get_running_app().config
        white_point_name = config.get('color', 'white_point')
        observer_angle = config.get('color', 'observer_angle')
        self.set_white_point(white_point_name, observer_angle)
        self.scheme_mode = config.get('color', 'scheme_mode').lower()
        self.value_range = config.get('ui', 'value_range')
        self.color_spaces = json.loads(config.get('ui', 'color_spaces'))
        self.detach_values = int(config.get('ui', 'detach_values'))

        self.history = deque(maxlen=30)
        self.history_next = []
        self.color = grapefruit.Color((0, 0, 0), wref=self.white_point)
        self.set_color_info()
        super(LookupScreen, self).__init__(**kwargs)

        self.value_view = Factory.ValueView()
        self.tabbed_panel = FullWidthTabbedPanel()
        self.info_tab = Factory.InfoTab()
        self.schemes_tab = Factory.SchemesTab()
        self.tools_tab = Factory.ToolsTab()

        self.load_content()
        self.load_value_displays()
        self.make_schemes()

    def on_color(self, instance, color):
        """Sets values, info, and schemes."""
        if not self.color.is_legal:
            return
        for value_display in self.value_view.ids.value_grid.children:
            value_display.value = self.get_value(value_display.color_space)
            value_display.update_inputs()
        self.set_color_info()
        self.make_schemes()

    def get_value(self, color_space):
        """Returns the color value for the corresponding color space.

        Args:
            color_space: The name of the color space to get the value of.

        Returns:
            A list containing the value for the color.

        """
        if color_space == 'Hex':
            return [self.color.html]
        elif color_space == 'sRGB':
            if self.value_range == '0-255':
                return list(self.color.ints)
            elif self.value_range == '0-1':
                return list(self.color.rgb)
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
        """Sets color info properties for the current color."""
        self.color_name = self.named_colors.get(self.color.html, 'N/A')
        self.websafe_color = grapefruit.Color(
            self.color.websafe, wref=self.white_point)
        self.greyscale_color = grapefruit.Color(
            self.color.greyscale, wref=self.white_point)
        self.complementary_color = self.color.complementary_color()
        self.ryb_hue = round(grapefruit.rgb_to_ryb(self.color.hsl_hue), 3)

    def make_schemes(self):
        """Makes color schemes and displays the colors."""
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

    def on_value_range(self, instance, value_range):
        """Reloads the sRGB `ValueDisplay`."""
        for value_display in self.value_view.ids.value_grid.children:
            if value_display.color_space == 'sRGB':
                value_display.value = self.get_value(value_display.color_space)
                value_display.update_inputs()

    def on_color_spaces(self, instance, color_spaces):
        """Removes `ValueDisplay` widgets and reloads them."""
        self.value_view.ids.value_grid.clear_widgets()
        self.load_value_displays()

    def load_value_displays(self):
        """Loads `ValueDisplay` widgets based on configuration."""
        for color_space in self.color_spaces:
            self.value_view.ids.value_grid.add_widget(
                ValueDisplay(color_space))

    def on_detach_values(self, instance, detach_values):
        """Clears content and reloads it."""
        self.tabbed_panel.clear_widgets()
        self.tabbed_panel.clear_tabs()
        self.ids.content.clear_widgets()
        self.load_content()

    def load_content(self):
        """Loads the `TabbedPanel` based on configuration."""
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
        """Sets the white point based on observer angle and point name.

        Args:
            name: The name of the white point.
            observer: The observer angle of the white point.

        """
        if observer == 'CIE 1931':
            name = 'std_' + name
        elif observer == 'CIE 1964':
            name = 'sup_' + name
        self.white_point = grapefruit.WHITE_REFERENCE[name]

    def random_color(self):
        self.add_to_history(self.color)
        self.color = grapefruit.Color(tuple(random.random() for _ in range(3)))

    def blend_colors(self):
        """Blends stored colors together and switches to the color."""
        blend_color1 = self.tools_tab.ids.color_select1.color
        blend_color2 = self.tools_tab.ids.color_select2.color
        # Only blend if both colors are visible.
        if blend_color1.alpha and blend_color2.alpha:
            self.add_to_history(self.color)
            self.color = blend_color1.blend(blend_color2)

    def add_to_palette(self):
        """Opens the `PalettesScreen` in add mode."""
        knspace.palettes_screen.mode = 'add'
        App.get_running_app().root.current = 'palettes'

    def add_to_history(self, color, next_disable=True):
        """Appends the current color to history.

        Args:
            color: The color object to add to history
            next_disable: A boolean value that determines whether
                to disable the next button. Defaults to True.

        """
        self.history.append(color)
        self.ids.prev_button.disabled = False
        if next_disable:
            del self.history_next[:]
            self.ids.next_button.disabled = True

    def previous_color(self):
        """Switches to the previous color in history."""
        if len(self.history):
            self.history_next.append(self.color)
            self.ids.next_button.disabled = False
            self.color = self.history.pop()
            if not self.history:
                self.ids.prev_button.disabled = True

    def next_color(self):
        """Switches to the next color in history."""
        if len(self.history_next):
            self.history.append(self.color)
            self.ids.prev_button.disabled = False
            self.color = self.history_next.pop()
            if not self.history_next:
                self.ids.next_button.disabled = True


class ValueDisplay(GridLayout):
    """Displays a color space and its values."""

    color_space = StringProperty()
    value = ListProperty()
    value_inputs = ListProperty()

    def __init__(self, color_space, **kwargs):
        """Initializes a `ValueDisplay` based on the color space.

        Args:
            color_space: The name of the color space
                that the `ValueDisplay` will represent.

        """
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
        """Updates each `ValueInput` in turn."""
        for value_input in self.value_inputs:
            value_input.text = value_input.format_value(
                self.value[value_input.index])
            value_input.scroll_x = 0

    def update_color(self):
        """Updates color with a new color from the value property."""
        lookup_screen = knspace.lookup_screen
        white_point = lookup_screen.white_point
        lookup_screen.add_to_history(lookup_screen.color, next_disable=False)

        if self.color_space == 'Hex':
            lookup_screen.color = grapefruit.Color.from_html(
                *self.value, wref=white_point)
        elif self.color_space == 'sRGB':
            if lookup_screen.value_range == '0-255':
                # Convert RGB values from range 0-255 to range 0-1.
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

        # Disabling next is held off until new color is set to check if
        # it is legal. Revert to previous color if not legal.
        if lookup_screen.color.is_legal:
            del lookup_screen.history_next[:]
        else:
            lookup_screen.previous_color()
            lookup_screen.history_next.pop()
        if not lookup_screen.history_next:
            lookup_screen.ids.next_button.disabled = True


class ValueInput(TextInput):
    """Accepts input and displays values based on a color space."""

    hex_pat = re.compile(u'^#?[0-9A-Fa-f]*$')
    float_pat = re.compile(u'^-?[0-9]*\\.?[0-9]*$')
    index = NumericProperty()

    def __init__(self, index, color_space, **kwargs):
        """Initializes a `ValueInput` based on the color space.

        Args:
            index: The index in the value list corresponding
                to the value of the `ValueInput`.
            color_space: The name of the color space
                that the `ValueInput` will represent.

        """
        super(ValueInput, self).__init__(**kwargs)
        self.index = index
        if color_space in ('sRGB', 'HSV', 'HSL', 'CMY', 'CMYK'):
            self.input_filter = 'float'

    def on_focus(self, instance, focused):
        """Checks the value for validity and sets it."""
        if not focused:
            # Make sure the input text is not empty,
            # isn't the same as the current value, and is valid.
            if (self.text and self.text != self.format_value(
                    self.parent.value[self.index]) and self.valid_input()):
                self.parent.value[self.index] = self.get_value()
                self.parent.update_color()
            else:
                self.text = self.format_value(self.parent.value[self.index])
                self.scroll_x = 0

    def insert_text(self, substring, from_undo=False):
        """Filters invalid input characters for certain color spaces."""
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
        """Returns whether the format of the value is valid.

        Returns:
            True if valid, False if invalid.

        """
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

    def get_value(self):
        """Returns the value, constraining it if neccessary.

        Returns:
            The value as a string if it cannot be converted to a float.
            Otherwise, the value as a float or, if the value is outside
            the range for the color space, an integer value at the
            upper or lower end of the range.

        """
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
        """Returns a value rounded to a number of significant digits.

        Args:
            val: The numeric value to format.
            digits: The number of significant digits
                to format to. Defaults to 3.

        Returns:
            `val` if `val` is a string. Otherwise,
            the formatted numeric value.

        """
        if type(val) is str:
            return val
        formatter = '{:.' + str(digits) + 'g}'
        return formatter.format(round(val, digits) + 0)


class FullWidthTabbedPanel(TabbedPanel):
    """A `TabbedPanel` with tab headers filling the tab strip width."""

    tab_width_min = NumericProperty('75dp')

    def on_width(self, instance, width):
        self.set_tab_width()

    def on_tab_list(self, instance, tab_list):
        self.set_tab_width()

    def set_tab_width(self):
        """Sets the width of the tab headers to fill the tab strip."""
        try:
            new_tab_width = self.width / len(self.tab_list)
        except ZeroDivisionError:
            new_tab_width = self.width

        if new_tab_width >= self.tab_width_min:
            self.tab_width = new_tab_width
        else:
            self.tab_width = self.tab_width_min


class ColorBox(Widget):
    """Holds and displays a color object."""

    color = ObjectProperty((0, 0, 0, 0))

    def on_touch_down(self, touch):
        """Switches to the color."""
        if self.collide_point(*touch.pos):
            lookup_screen = knspace.lookup_screen
            lookup_screen.add_to_history(lookup_screen.color)
            lookup_screen.color = self.color


class ColorSelectBox(Widget):
    """Sets and holds a color object that can be used later."""

    color = ObjectProperty(grapefruit.Color((0, 0, 0), alpha=0))

    def on_touch_down(self, touch):
        """Schedules a clock event for long touch."""
        if self.collide_point(*touch.pos):
            touch.grab(self)
            clock_event = Clock.schedule_once(self.view_color, 1)
            touch.ud['view_color'] = clock_event

    def on_touch_move(self, touch):
        """Unschedules the clock event if the touch moved outside."""
        if touch.grab_current is self and not self.collide_point(*touch.pos):
            Clock.unschedule(touch.ud.get('view_color'))

    def on_touch_up(self, touch):
        """Sets the color to the current `LookupScreen` color."""
        Clock.unschedule(touch.ud.get('view_color'))
        if touch.grab_current is self and self.collide_point(*touch.pos):
            self.color = knspace.lookup_screen.color
        touch.ungrab(self)

    def view_color(self, dt):
        """Switches to the color."""
        if self.color.alpha:
            lookup_screen = knspace.lookup_screen
            lookup_screen.add_to_history(lookup_screen.color)
            lookup_screen.color = self.color
