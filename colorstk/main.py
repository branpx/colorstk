from kivy.app import App
from kivy.uix.screenmanager import (NoTransition,
                                    Screen,
                                    ScreenManager)

import canvas
import lookup
import palettes
import picker
import settings


class AboutScreen(Screen):
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
        screen_manager.add_widget(AboutScreen(name='about'))
        return screen_manager


if __name__ == '__main__':
    app = ColorsTKApp()
    app.load_kv('main.kv')
    app.run()
