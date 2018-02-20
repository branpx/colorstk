#!/usr/bin/env python

import json
from os.path import dirname, join

from kivy.app import App
from kivy.garden import iconfonts
from kivy.lang.builder import Builder
from kivy.properties import (BooleanProperty,
                             ListProperty,
                             NumericProperty,
                             ObjectProperty,
                             StringProperty)
from kivy.uix.behaviors.knspace import knspace
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.modalview import ModalView
from kivy.uix.screenmanager import NoTransition, ScreenManager
from kivy.uix.settings import SettingItem, SettingsWithNoMenu
from kivy.uix.togglebutton import ToggleButton

try:
    import lookup, palettes
except ImportError:
    from colorstk import lookup, palettes


class PopupWithActionBar(BoxLayout, ModalView):
    """A `Popup` with an action bar at the top."""

    title = StringProperty()
    icon = StringProperty()


class AboutPopup(PopupWithActionBar):
    """A `PopupWithActionBar` showing license information."""

    pass


class OptionsTogglePopup(PopupWithActionBar):
    """A `PopupWithActionBar` for toggling options."""

    setting_item = ObjectProperty()
    max_height = NumericProperty()

    def set_height(self, content_height):
        """Sets the height to fit the content."""
        full_height = self.ids.action_bar.height + content_height
        if full_height > self.max_height:
            self.height = self.max_height
        else:
            self.height = full_height

    def on_dismiss(self):
        self.setting_item.write_option()


class SettingToggle(SettingItem):
    """A `SettingItem` that allows toggling a single option."""

    values = ListProperty(['0', '1'])

    def on_touch_down(self, touch):
        """Toggles the option."""
        super(SettingToggle, self).on_touch_down(touch)
        if self.collide_point(*touch.pos):
            self.ids.check_box.active = not self.ids.check_box.active


class SettingOptionsToggle(SettingItem):
    """A `SettingItem` that allows toggling options from a list."""

    temp_value = ObjectProperty()
    options = ListProperty()
    multi_toggle = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(SettingOptionsToggle, self).__init__(**kwargs)
        self.temp_value = self.value

    def on_release(self):
        self.create_popup()

    def set_option(self, toggle_button):
        """Sets a temporary value for the toggled option.

        Args:
            toggle_button: The `ToggleButton` that was toggled.

        """
        if self.multi_toggle:
            value_list = json.loads(self.temp_value)
            if toggle_button.state == 'down':
                value_list.append(toggle_button.text)
            elif toggle_button.state == 'normal':
                value_list.remove(toggle_button.text)
            # Preserve the order of the options.
            value_list = [option for option in self.options
                          if option in value_list]
            self.temp_value = json.dumps(value_list)
        else:
            self.temp_value = toggle_button.text
            self.popup.dismiss()

    def write_option(self):
        self.value = self.temp_value

    def create_popup(self):
        """Creates an `OptionsTogglePopup` and adds toggle buttons."""
        self.popup = OptionsTogglePopup(title=self.title, setting_item=self)
        for option in self.options:
            state = 'down' if option in self.value else 'normal'
            toggle_button = ToggleButton(
                text=option, size_hint_y=None, height='50dp', state=state)
            if not self.multi_toggle:
                toggle_button.group = str(self.uid)
            toggle_button.bind(on_release=self.set_option)
            self.popup.ids.toggle_button_grid.add_widget(toggle_button)
        self.popup.open()


class ColorsTKApp(App):
    def build(self):
        """Initializes `ColorsTKApp`."""
        self.use_kivy_settings = False
        self.settings_cls = SettingsWithNoMenu
        self.title = 'Colors Toolkit'
        self.icon = 'media/colorstk_icon.png'
        self.pkg_dir = dirname(__file__)

        iconfonts.register('colorstk',
                           join(self.pkg_dir, 'data/icons'),
                           join(self.pkg_dir, 'data/icons.fontd'))
        Builder.load_file(join(self.pkg_dir, 'main.kv'))
        Builder.load_file(join(self.pkg_dir, 'lookup.kv'))
        Builder.load_file(join(self.pkg_dir, 'palettes.kv'))

        screen_manager = ScreenManager(transition=NoTransition())
        screen_manager.add_widget(lookup.LookupScreen(name='lookup'))
        screen_manager.add_widget(palettes.PalettesScreen(name='palettes'))
        screen_manager.add_widget(palettes.ColorsScreen(name='colors'))
        return screen_manager

    def build_config(self, config):
        """Sets default values in the configuration."""
        config.setdefaults('ui', {
            'detach_values': 0,
            'color_spaces': json.dumps(
                ['Hex', 'sRGB', 'HSL', 'HSV', 'CIE-XYZ', 'CIE-LAB'])
        })
        config.setdefaults('color', {
            'white_point': 'D65',
            'observer_angle': 'CIE 1931',
            'scheme_mode': 'RYB'
        })

    def build_settings(self, settings):
        """Adds the settings panel and creates the settings popup."""
        settings.register_type('toggle', SettingToggle)
        settings.register_type('options_toggle', SettingOptionsToggle)
        json_panel = json.dumps([
            {'type': 'title',
             'title': 'Interface'},
            {'type': 'toggle',
             'title': 'Detach values',
             'desc': 'Display values to the left of the tabbed panel',
             'section': 'ui',
             'key': 'detach_values'},
            {'type': 'options_toggle',
             'title': 'Color spaces',
             'desc': 'Color space values to display',
             'section': 'ui',
             'key': 'color_spaces',
             'multi_toggle': True,
             'options': ['Hex', 'sRGB', 'HSL', 'HSV', 'YIQ', 'YUV',
                         'CIE-XYZ', 'CIE-LAB', 'CMY', 'CMYK']},
            {'type': 'title',
             'title': 'Color Settings'},
            {'type': 'options_toggle',
             'title': 'White point',
             'desc': 'White reference point for CIE-LAB conversions',
             'section': 'color',
             'key': 'white_point',
             'options': ['A', 'B', 'C', 'D50', 'D55', 'D65', 'D75', 'E',
                         'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8',
                         'F9', 'F10', 'F11', 'F12']},
            {'type': 'options_toggle',
             'title': 'Observer angle',
             'desc': 'Field of view for white point coordinates',
             'section': 'color',
             'key': 'observer_angle',
             'options': ['CIE 1931', 'CIE 1964']},
            {'type': 'options_toggle',
             'title': 'Scheme mode',
             'desc': 'Color wheel to use for schemes/complementary color',
             'section': 'color',
             'key': 'scheme_mode',
             'options': ['RGB', 'RYB']}
        ])
        settings.add_json_panel('', self.config, data=json_panel)

        self.settings_popup = PopupWithActionBar(
            title='Settings', icon=join(self.pkg_dir, 'data/settings.png'))
        self.settings_popup.add_widget(settings)

    def display_settings(self, settings):
        self.settings_popup.open()

    def on_config_change(self, config, section, key, value):
        """Sets the property for the corresponding config value."""
        lookup_screen = knspace.lookup_screen
        if key == 'detach_values':
            lookup_screen.detach_values = int(value)
        elif key == 'color_spaces':
            lookup_screen.color_spaces = json.loads(value)
        elif key == 'white_point':
            lookup_screen.set_white_point(
                value, config.get('color', 'observer_angle'))
        elif key == 'observer_angle':
            lookup_screen.set_white_point(
                config.get('color', 'white_point'), value)
        elif key == 'scheme_mode':
            lookup_screen.scheme_mode = value.lower()

    def get_application_config(self):
        """Returns the path to the application configuration file."""
        config_path = join(self.user_data_dir, '%(appname)s.ini')
        return super(ColorsTKApp, self).get_application_config(config_path)


def main():
    ColorsTKApp().run()


if __name__ == '__main__':
    main()
