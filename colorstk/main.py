from kivy.app import App
from kivy.properties import BooleanProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager

import canvas
import lookup
import palettes
import picker
import settings


class RootWidget(FloatLayout):
    pass


class ScreenMenu(GridLayout):
    toggled = BooleanProperty(False)

    def on_toggled(self, instance, toggled):
        if self.toggled:
            self.disabled = False
            self.opacity = 1
        else:
            self.disabled = True
            self.opacity = 0

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            self.toggled = False
        super(ScreenMenu, self).on_touch_down(touch)


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


if __name__ == '__main__':
    app = ColorsTKApp()
    app.load_kv('main.kv')
    app.run()
