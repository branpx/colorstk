from kivy.app import App
from kivy.lang.builder import Builder
from kivy.properties import ListProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen


Builder.load_file('palettes.kv')


class PalettesScreen(BoxLayout, Screen):
    palettes = ListProperty()
    mode = StringProperty('normal')

    def on_palettes(self, instance, palettes):
        self.ids.palette_stack.add_widget(palettes[-1])


class ColorsScreen(Screen):
    pass


class Palette(GridLayout):
    name = StringProperty()
    colors = ListProperty()

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            screen_manager = App.get_running_app().root
            screen_manager.current = 'colors'


class NewPalettePopup(Popup):
    def __init__(self, palettes_screen, **kwargs):
        super(NewPalettePopup, self).__init__(**kwargs)
        self.palettes_screen = palettes_screen
        self.ids.name_input.bind(on_text_validate=self.add_palette)

    def on_open(self):
        default_name = 'palette' + str(len(self.palettes_screen.palettes)+1)
        self.ids.name_input.text = default_name
        self.ids.name_input.focus = True

    def add_palette(self, name_input):
        self.palettes_screen.palettes.append(Palette(name=name_input.text))
        self.dismiss()
