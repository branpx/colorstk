from kivy.app import App
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.lang.builder import Builder
from kivy.properties import (ListProperty,
                             ObjectProperty,
                             StringProperty)
from kivy.storage.jsonstore import JsonStore
from kivy.uix.actionbar import ActionButton
from kivy.uix.behaviors.compoundselection import CompoundSelectionBehavior
from kivy.uix.behaviors.knspace import knspace, KNSpaceBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.stacklayout import StackLayout
from kivy.uix.widget import Widget


Builder.load_file('palettes.kv')


class PalettesScreen(KNSpaceBehavior, BoxLayout, Screen):
    mode = StringProperty()

    def __init__(self, **kwargs):
        super(PalettesScreen, self).__init__(**kwargs)
        self.mode = 'normal'
        self.delete_button = ActionButton(
            text='Delete', on_release=self.delete_palette)
        self.palettes = JsonStore('palettes.json')
        for palette in self.palettes:
            self.ids.palette_stack.add_widget(Palette(
                name=palette, colors=self.palettes[palette]['colors']))

    def on_mode(self, instance, mode):
        action_previous = self.ids.action_previous
        action_view = self.ids.action_view
        if mode == 'normal':
            action_previous.title = 'Palettes'
            action_previous.with_previous = False
        elif mode == 'add':
            action_previous.title = 'Select palette'
            action_previous.with_previous = True
        elif mode == 'selection':
            action_previous.title = 'Selection'
            action_previous.with_previous = True
            action_view.add_widget(self.delete_button)

    def delete_palette(self, button=None):
        for palette in self.ids.palette_stack.selected_nodes:
            self.ids.palette_stack.remove_widget(palette)
            self.palettes.delete(palette.name)
        self.ids.palette_stack.clear_selection()
        self.ids.action_view.remove_widget(self.delete_button)
        self.mode = 'normal'


class ColorsScreen(KNSpaceBehavior, BoxLayout, Screen):
    def load_colors(self, palette):
        for color in palette.colors:
            self.ids.color_stack.add_widget(PaletteColor(color=color))

    def on_leave(self):
        self.ids.color_stack.clear_widgets()


class SelectableStack(CompoundSelectionBehavior, StackLayout):
    def select_node(self, node):
        node.background_color = (0.4, 0.4, 0.4, 1)
        return super(SelectableStack, self).select_node(node)

    def deselect_node(self, node):
        node.background_color = (0.2, 0.2, 0.2, 1)
        super(SelectableStack, self).deselect_node(node)


class Palette(GridLayout):
    name = StringProperty()
    colors = ListProperty()

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if knspace.palettes_screen.mode == 'normal':
                clock_event = Clock.schedule_once(self.trigger_selection, 1)
                touch.ud['trigger_selection'] = clock_event
            elif knspace.palettes_screen.mode == 'selection':
                self.parent.select_with_touch(self, touch)

    def on_touch_up(self, touch):
        Clock.unschedule(touch.ud.get('trigger_selection'))
        if self.collide_point(*touch.pos):
            if knspace.palettes_screen.mode == 'normal':
                screen_manager = App.get_running_app().root
                knspace.colors_screen.load_colors(self)
                screen_manager.current = 'colors'
            elif knspace.palettes_screen.mode == 'add':
                self.colors.append(list(knspace.lookup_screen.color))
                knspace.palettes_screen.mode = 'normal'

    def on_colors(self, instance, colors):
        knspace.palettes_screen.palettes.put(self.name, colors=self.colors)

    def trigger_selection(self, dt):
        knspace.palettes_screen.mode = 'selection'
        self.parent.select_with_touch(self)


class PaletteColor(Widget):
    color = ObjectProperty()


class NewPalettePopup(Popup):
    def on_open(self):
        default_name = 'palette' + str(len(knspace.palettes_screen.palettes)+1)
        self.ids.name_input.text = default_name
        self.ids.name_input.focus = True

    def add_palette(self, name_input):
        if name_input.text not in knspace.palettes_screen.palettes:
            knspace.palettes_screen.palettes.put(
                name_input.text, colors=[])
            knspace.palettes_screen.ids.palette_stack.add_widget(
                Palette(name=name_input.text))
            self.dismiss()
        else:
            self.title = 'Palette already exists!'
            self.title_color = [1, 0, 0, 1]
