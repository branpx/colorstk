from kivy.app import App
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.lang.builder import Builder
from kivy.properties import (BooleanProperty,
                             ListProperty,
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
        self.new_button = self.ids.new_button
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
            action_view.remove_widget(self.new_button)
            action_view.add_widget(self.delete_button)

    def delete_palette(self, button=None):
        for palette in self.ids.palette_stack.selected_nodes:
            self.ids.palette_stack.remove_widget(palette)
            self.palettes.delete(palette.name)
        self.ids.palette_stack.clear_selection()
        self.ids.action_view.remove_widget(self.delete_button)
        self.ids.action_view.add_widget(self.new_button)
        self.mode = 'normal'


class ColorsScreen(KNSpaceBehavior, BoxLayout, Screen):
    mode = StringProperty()

    def __init__(self, **kwargs):
        super(ColorsScreen, self).__init__(**kwargs)
        self.mode = 'normal'
        self.delete_button = ActionButton(
            text='Delete', on_release=self.delete_color)

    def load_colors(self, palette):
        self.palette = palette
        for color in palette.colors:
            self.ids.color_stack.add_widget(PaletteColor(color=color))

    def on_mode(self, instance, mode):
        action_previous = self.ids.action_previous
        action_view = self.ids.action_view
        if mode == 'normal':
            action_previous.title = 'Colors'
        elif mode == 'selection':
            action_previous.title = 'Selection'
            action_view.add_widget(self.delete_button)

    def on_leave(self):
        self.palette = None
        self.ids.color_stack.clear_widgets()

    def delete_color(self, button=None):
        color_stack = self.ids.color_stack
        for color_widget in color_stack.selected_nodes:
            color_stack.remove_widget(color_widget)
            self.palette.colors.remove(color_widget.color)
        color_stack.clear_selection()
        self.ids.action_view.remove_widget(self.delete_button)
        self.mode = 'normal'


class SelectableStack(CompoundSelectionBehavior, StackLayout):
    def select_node(self, node):
        node.selected = True
        return super(SelectableStack, self).select_node(node)

    def deselect_node(self, node):
        node.selected = False
        super(SelectableStack, self).deselect_node(node)


class Palette(GridLayout):
    name = StringProperty()
    colors = ListProperty()
    selected = BooleanProperty(False)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            touch.grab(self)
            if knspace.palettes_screen.mode == 'normal':
                clock_event = Clock.schedule_once(self.trigger_selection, 1)
                touch.ud['trigger_selection'] = clock_event
            elif knspace.palettes_screen.mode == 'selection':
                self.parent.select_with_touch(self, touch)

    def on_touch_move(self, touch):
        if touch.grab_current is self and not self.collide_point(*touch.pos):
            Clock.unschedule(touch.ud.get('trigger_selection'))

    def on_touch_up(self, touch):
        Clock.unschedule(touch.ud.get('trigger_selection'))
        if touch.grab_current is self and self.collide_point(*touch.pos):
            if knspace.palettes_screen.mode == 'normal':
                screen_manager = App.get_running_app().root
                knspace.colors_screen.load_colors(self)
                screen_manager.current = 'colors'
            elif knspace.palettes_screen.mode == 'add':
                self.colors.append(knspace.lookup_screen.color.rgb)
                knspace.palettes_screen.mode = 'normal'
        touch.ungrab(self)

    def on_colors(self, instance, colors):
        knspace.palettes_screen.palettes.put(self.name, colors=self.colors)

    def on_selected(self, instance, selected):
        if selected:
            self.background_color = (0.4, 0.4, 0.4, 1)
        else:
            self.background_color = (0.2, 0.2, 0.2, 1)

    def trigger_selection(self, dt):
        knspace.palettes_screen.mode = 'selection'
        self.parent.select_with_touch(self)


class PaletteColor(Widget):
    color = ObjectProperty()
    selected = BooleanProperty(False)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            touch.grab(self)
            if knspace.colors_screen.mode == 'normal':
                clock_event = Clock.schedule_once(self.trigger_selection, 1)
                touch.ud['trigger_selection'] = clock_event
            elif knspace.colors_screen.mode == 'selection':
                self.parent.select_with_touch(self, touch)

    def on_touch_move(self, touch):
        if touch.grab_current is self and not self.collide_point(*touch.pos):
            Clock.unschedule(touch.ud.get('trigger_selection'))

    def on_touch_up(self, touch):
        Clock.unschedule(touch.ud.get('trigger_selection'))
        if touch.grab_current is self and self.collide_point(*touch.pos):
            if knspace.colors_screen.mode == 'normal':
                screen_manager = App.get_running_app().root
                knspace.lookup_screen.set_color(self.color)
                screen_manager.current = 'lookup'
        touch.ungrab(self)

    def on_selected(self, instance, selected):
        if selected:
            self.border_color = (0.8, 0.8, 0.8, 1)
        else:
            self.border_color = (0.3, 0.3, 0.3, 1)

    def trigger_selection(self, dt):
        knspace.colors_screen.mode = 'selection'
        self.parent.select_with_touch(self)


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
