from kivy.app import App
from kivy.uix.screenmanager import (NoTransition,
                                    Screen,
                                    ScreenManager)
from kivy.uix.popup import Popup

import canvas
import lookup
import palettes
import picker
import settings


class AboutPopup(Popup):
    pass


class ColorsTKApp(App):
    def build(self):
        screen_manager = ScreenManager(transition=NoTransition())
        screen_manager.add_widget(lookup.LookupScreen(name='lookup'))
        screen_manager.add_widget(picker.PickerScreen(name='picker'))
        screen_manager.add_widget(palettes.PalettesScreen(name='palettes'))
        screen_manager.add_widget(palettes.ColorsScreen(name='colors'))
        screen_manager.add_widget(canvas.CanvasScreen(name='canvas'))
        screen_manager.add_widget(settings.SettingsScreen(name='settings'))
        return screen_manager


if __name__ == '__main__':
    app = ColorsTKApp()
    app.load_kv('main.kv')
    app.run()
