import json

from kivy.app import App
from kivy.properties import BooleanProperty, ListProperty
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import (NoTransition,
                                    Screen,
                                    ScreenManager)
from kivy.uix.settings import SettingItem, SettingsWithNoMenu
from kivy.uix.togglebutton import ToggleButton

import lookup
import palettes


class AboutPopup(Popup):
    pass


class OptionsTogglePopup(Popup):
    pass


class SettingOptionsToggle(SettingItem):
    options = ListProperty()
    multi_toggle = BooleanProperty(False)

    def on_release(self):
        self.create_popup()

    def set_option(self, toggle_button):
        if self.multi_toggle:
            value_list = json.loads(self.value)
            if toggle_button.state == 'down':
                value_list.append(toggle_button.text)
            elif toggle_button.state == 'normal':
                value_list.remove(toggle_button.text)
            self.value = json.dumps(value_list)
        else:
            self.value = toggle_button.text
            self.popup.dismiss()

    def create_popup(self):
        self.popup = OptionsTogglePopup(title=self.title)
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
        self.use_kivy_settings = False
        self.settings_cls = SettingsWithNoMenu
        screen_manager = ScreenManager(transition=NoTransition())
        screen_manager.add_widget(lookup.LookupScreen(name='lookup'))
        screen_manager.add_widget(palettes.PalettesScreen(name='palettes'))
        screen_manager.add_widget(palettes.ColorsScreen(name='colors'))
        return screen_manager

    def build_config(self, config):
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
        settings.register_type('options_toggle', SettingOptionsToggle)
        json_panel = json.dumps([
            {'type': 'bool',
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
            {'type': 'options_toggle',
             'title': 'White point',
             'desc': 'White reference point for CIE-LAB/CIE-XYZ conversions',
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
        settings.add_json_panel('Settings', self.config, data=json_panel)


if __name__ == '__main__':
    app = ColorsTKApp()
    app.load_kv('main.kv')
    app.run()
