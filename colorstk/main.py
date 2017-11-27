from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen

import canvas
import lookup
import palettes
import picker
import settings


class RootWidget(FloatLayout):
    pass


class AboutScreen(Screen):
    pass


class ColorsTKApp(App):
    def build(self):
        return RootWidget()

    def on_start(self):
        screen_manager = self.root.ids.screen_manager
        screen_manager.add_widget(lookup.LookupScreen(name='lookup'))
        screen_manager.add_widget(picker.PickerScreen(name='picker'))
        screen_manager.add_widget(palettes.PalettesScreen(name='palettes'))
        screen_manager.add_widget(canvas.CanvasScreen(name='canvas'))
        screen_manager.add_widget(settings.SettingsScreen(name='settings'))
        screen_manager.add_widget(AboutScreen(name='about'))


if __name__ == '__main__':
    app = ColorsTKApp()
    app.load_kv('main.kv')
    app.run()
