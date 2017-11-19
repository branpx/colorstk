from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

import canvas
import lookup
import palettes
import picker
import settings


class ColorTKApp(App):
    def build(self):
        screen_manager = ScreenManager()
        screen_manager.add_widget(lookup.LookupScreen(name='lookup'))
        screen_manager.add_widget(picker.PickerScreen(name='picker'))
        screen_manager.add_widget(palettes.PalettesScreen(name='palettes'))
        screen_manager.add_widget(canvas.CanvasScreen(name='canvas'))
        screen_manager.add_widget(settings.SettingsScreen(name='settings'))
        return screen_manager


if __name__ == '__main__':
    ColorTKApp().run()
