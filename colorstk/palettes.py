from kivy.app import App
from kivy.factory import Factory
from kivy.lang.builder import Builder
from kivy.properties import (ListProperty,
                             ObjectProperty,
                             StringProperty)
from kivy.storage.jsonstore import JsonStore
from kivy.uix.behaviors.knspace import knspace, KNSpaceBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget


Builder.load_file('palettes.kv')


class PalettesScreen(KNSpaceBehavior, BoxLayout, Screen):
    palettes = ListProperty()
    mode = StringProperty()

    def __init__(self, **kwargs):
        super(PalettesScreen, self).__init__(**kwargs)
        self.mode = 'normal'
        self.palette_store = JsonStore('palettes.json')
        for palette in self.palette_store:
            self.palettes.append(Palette(
                name=palette, colors=self.palette_store[palette]['colors']))

    def on_palettes(self, instance, palettes):
        self.ids.palette_stack.add_widget(palettes[-1])

    def on_mode(self, instance, mode):
        action_previous = self.ids.action_previous
        if mode == 'normal':
            action_previous.title = 'Palettes'
            action_previous.with_previous = False
        elif mode == 'add':
            action_previous.title = 'Select palette'
            action_previous.with_previous = True


class ColorsScreen(KNSpaceBehavior, BoxLayout, Screen):
    def load_colors(self, palette):
        for color in palette.colors:
            self.ids.color_stack.add_widget(PaletteColor(color=color))

    def on_leave(self):
        self.ids.color_stack.clear_widgets()


class Palette(GridLayout):
    name = StringProperty()
    colors = ListProperty()

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if knspace.palettes_screen.mode == 'normal':
                screen_manager = App.get_running_app().root
                knspace.colors_screen.load_colors(self)
                screen_manager.current = 'colors'
            elif knspace.palettes_screen.mode == 'add':
                self.colors.append(list(knspace.lookup_screen.color))
                knspace.palettes_screen.mode = 'normal'

    def on_colors(self, instance, colors):
        knspace.palettes_screen.palette_store.put(
            self.name, colors=self.colors)


class PaletteColor(Widget):
    color = ObjectProperty()


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
        if name_input.text not in knspace.palettes_screen.palette_store:
            self.palettes_screen.palettes.append(Palette(name=name_input.text))
            knspace.palettes_screen.palette_store.put(
                name_input.text, colors=[])
            self.dismiss()
        else:
            self.title = 'Palette already exists!'
            self.title_color = [1, 0, 0, 1]
