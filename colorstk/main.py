from kivy.app import App
from kivy.lang.builder import Builder
from kivy.properties import BooleanProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager

import canvas
import lookup
import palettes
import picker
import settings


Builder.load_file('main.kv')


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
        super().on_touch_down(touch)


class ColorsTKApp(App):
    def build(self):
        root_widget = RootWidget()
        root_widget.ids.screen_manager.add_widget(lookup.LookupScreen(name='lookup'))
        root_widget.ids.screen_manager.add_widget(picker.PickerScreen(name='picker'))
        root_widget.ids.screen_manager.add_widget(palettes.PalettesScreen(name='palettes'))
        root_widget.ids.screen_manager.add_widget(canvas.CanvasScreen(name='canvas'))
        root_widget.ids.screen_manager.add_widget(settings.SettingsScreen(name='settings'))
        return root_widget


if __name__ == '__main__':
    ColorsTKApp().run()
