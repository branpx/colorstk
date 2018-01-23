"""Implements saving and loading colors."""

from os.path import join

from kivy.app import App
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.garden.iconfonts import icon
from kivy.properties import (BooleanProperty,
                             ListProperty,
                             StringProperty)
from kivy.storage.jsonstore import JsonStore
from kivy.uix.actionbar import ActionButton
from kivy.uix.behaviors.compoundselection import CompoundSelectionBehavior
from kivy.uix.behaviors.knspace import knspace, KNSpaceBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.stacklayout import StackLayout
from kivy.uix.widget import Widget


class PalettesScreen(KNSpaceBehavior, BoxLayout, Screen):
    """A screen for creating and displaying color palettes."""
    mode = StringProperty()

    def __init__(self, **kwargs):
        """Initializes a `PalettesScreen` and loads saved palettes."""
        super(PalettesScreen, self).__init__(**kwargs)
        self.menu_icon = self.ids.action_previous.app_icon
        self.mode = 'normal'
        self.new_button = self.ids.new_button
        self.delete_button = ActionButton(
            text='%s'%icon('icon_delete'),
            font_size='20dp', color=[1, 0, 0, 1],
            markup=True, on_release=self.delete_palette)
        user_data_dir = App.get_running_app().user_data_dir
        self.palettes = JsonStore(join(user_data_dir, 'palettes.json'))

        for palette in self.palettes:
            self.ids.palette_stack.add_widget(Palette(
                name=palette, colors=self.palettes[palette]['colors']))

    def on_mode(self, instance, mode):
        """Sets the action bar properties to match the mode."""
        action_previous = self.ids.action_previous
        action_view = self.ids.action_view
        if mode == 'normal':
            action_previous.title = '   Palettes'
            action_previous.app_icon = self.menu_icon
            action_previous.with_previous = False
        elif mode == 'add':
            action_previous.title = 'Select palette'
            action_previous.app_icon = ''
            action_previous.with_previous = True
        elif mode == 'selection':
            action_previous.title = 'Selection'
            action_previous.app_icon = ''
            action_previous.with_previous = True
            action_view.remove_widget(self.new_button)
            action_view.add_widget(self.delete_button)

    def on_action_previous(self):
        """Chooses previous button behavior based on the mode."""
        if self.mode == 'normal':
            Factory.ScreenMenu().open()
        elif self.mode == 'add':
            App.get_running_app().root.current = 'lookup'
            self.mode = 'normal'
        elif self.mode == 'selection':
            self.ids.palette_stack.clear_selection()
            self.ids.action_view.remove_widget(self.delete_button)
            self.ids.action_view.add_widget(self.new_button)
            self.mode = 'normal'

    def delete_palette(self, button=None):
        """Removes and deletes a `Palettes` and its colors."""
        for palette in self.ids.palette_stack.selected_nodes:
            self.ids.palette_stack.remove_widget(palette)
            self.palettes.delete(palette.name)
        self.ids.palette_stack.clear_selection()
        self.ids.action_view.remove_widget(self.delete_button)
        self.ids.action_view.add_widget(self.new_button)
        self.mode = 'normal'


class ColorsScreen(KNSpaceBehavior, BoxLayout, Screen):
    """A `Screen` for displaying the colors in a `Palette`."""
    mode = StringProperty()

    def __init__(self, **kwargs):
        super(ColorsScreen, self).__init__(**kwargs)
        self.menu_icon = self.ids.action_previous.app_icon
        self.mode = 'normal'
        self.delete_button = ActionButton(
            text='%s'%icon('icon_delete'),
            font_size='20dp', color=[1, 0, 0, 1],
            markup=True, on_release=self.delete_color)

    def on_leave(self):
        self.palette = None
        self.ids.color_stack.clear_widgets()

    def on_mode(self, instance, mode):
        """Sets the action bar properties to match the mode."""
        action_previous = self.ids.action_previous
        action_view = self.ids.action_view
        if mode == 'normal':
            action_previous.title = 'Colors'
            action_previous.app_icon = self.menu_icon
        elif mode == 'selection':
            action_previous.title = 'Selection'
            action_previous.app_icon = ''
            action_view.add_widget(self.delete_button)

    def on_action_previous(self):
        """Chooses previous button behavior based on the mode."""
        if self.mode == 'normal':
            App.get_running_app().root.current = 'palettes'
        elif self.mode == 'selection':
            self.ids.color_stack.clear_selection()
            self.ids.action_view.remove_widget(self.delete_button)
            self.mode = 'normal'

    def load_colors(self, palette):
        """Loads the colors from a `Palette` to the screen.

        Args:
            palette: A `Palette` to load colors from.

        """
        self.palette = palette
        for color in palette.colors:
            self.ids.color_stack.add_widget(PaletteColor(color=color))

    def delete_color(self, button=None):
        """Deletes a color from its palette and removes it."""
        color_stack = self.ids.color_stack
        for color_widget in color_stack.selected_nodes:
            color_stack.remove_widget(color_widget)
            self.palette.colors.remove(color_widget.color)
        color_stack.clear_selection()
        self.ids.action_view.remove_widget(self.delete_button)
        self.mode = 'normal'


class SelectableStack(CompoundSelectionBehavior, StackLayout):
    """A `StackLayout` that allows selecting its children."""

    def select_node(self, node):
        node.selected = True
        return super(SelectableStack, self).select_node(node)

    def deselect_node(self, node):
        node.selected = False
        super(SelectableStack, self).deselect_node(node)


class Palette(GridLayout):
    """Stores colors and displays a preview of them."""

    name = StringProperty()
    colors = ListProperty()
    selected = BooleanProperty(False)

    def on_touch_down(self, touch):
        """Selects `self` if in selection mode."""
        if self.collide_point(*touch.pos):
            touch.grab(self)

            if knspace.palettes_screen.mode == 'normal':
                clock_event = Clock.schedule_once(self.trigger_selection, 1)
                touch.ud['trigger_selection'] = clock_event

            elif knspace.palettes_screen.mode == 'selection':
                self.parent.select_with_touch(self, touch)

    def on_touch_move(self, touch):
        """Unschedules the clock event if the touch moved outside."""
        if touch.grab_current is self and not self.collide_point(*touch.pos):
            Clock.unschedule(touch.ud.get('trigger_selection'))

    def on_touch_up(self, touch):
        """Adds color if in add mode, otherwise loads the colors."""
        Clock.unschedule(touch.ud.get('trigger_selection'))
        if touch.grab_current is self and self.collide_point(*touch.pos):
            if knspace.palettes_screen.mode == 'normal':
                screen_manager = App.get_running_app().root
                knspace.colors_screen.load_colors(self)
                screen_manager.current = 'colors'
            elif knspace.palettes_screen.mode == 'add':
                self.colors.append(list(knspace.lookup_screen.color.rgb))
                knspace.palettes_screen.mode = 'normal'
        touch.ungrab(self)

    def on_colors(self, instance, colors):
        knspace.palettes_screen.palettes.put(self.name, colors=colors)

    def on_selected(self, instance, selected):
        """Changes appearance based on selection status."""
        if selected:
            self.background_color = (0.4, 0.4, 0.4, 1)
        else:
            self.background_color = (0.2, 0.2, 0.2, 1)

    def trigger_selection(self, dt):
        """Triggers the `PalettesScreen` selection mode."""
        knspace.palettes_screen.mode = 'selection'
        self.parent.select_with_touch(self)


class PaletteColor(Widget):
    """Represents a color in a `Palette`."""

    color = ListProperty()
    selected = BooleanProperty(False)

    def on_touch_down(self, touch):
        """Selects `self` if in selection mode."""
        if self.collide_point(*touch.pos):
            touch.grab(self)
            if knspace.colors_screen.mode == 'normal':
                clock_event = Clock.schedule_once(self.trigger_selection, 1)
                touch.ud['trigger_selection'] = clock_event
            elif knspace.colors_screen.mode == 'selection':
                self.parent.select_with_touch(self, touch)

    def on_touch_move(self, touch):
        """Unschedules the clock event if the touch moved outside."""
        if touch.grab_current is self and not self.collide_point(*touch.pos):
            Clock.unschedule(touch.ud.get('trigger_selection'))

    def on_touch_up(self, touch):
        """Switches to the color if in normal mode."""
        Clock.unschedule(touch.ud.get('trigger_selection'))
        if touch.grab_current is self and self.collide_point(*touch.pos):
            if knspace.colors_screen.mode == 'normal':
                screen_manager = App.get_running_app().root
                knspace.lookup_screen.set_color(self.color)
                screen_manager.current = 'lookup'
        touch.ungrab(self)

    def on_selected(self, instance, selected):
        """Changes appearance based on selection status."""
        if selected:
            self.border_color = (0.8, 0.8, 0.8, 1)
        else:
            self.border_color = (0.3, 0.3, 0.3, 1)

    def trigger_selection(self, dt):
        """Triggers the `ColorsScreen` selection mode."""
        knspace.colors_screen.mode = 'selection'
        self.parent.select_with_touch(self)


class NewPalettePopup(Popup):
    """A `Popup` that allows creating a new `Palette` with a name."""

    def on_open(self):
        """Generates a default text for the name input."""
        default_name = 'palette' + str(len(knspace.palettes_screen.palettes)+1)
        self.ids.name_input.text = default_name
        self.ids.name_input.focus = True

    def add_palette(self, name_input):
        """Creates and adds a new `Palette` to the `PalettesScreen`."""
        if name_input.text not in knspace.palettes_screen.palettes:
            knspace.palettes_screen.palettes.put(
                name_input.text, colors=[])
            knspace.palettes_screen.ids.palette_stack.add_widget(
                Palette(name=name_input.text))
            self.dismiss()
        else:
            self.title = 'Palette already exists!'
            self.title_color = [1, 0, 0, 1]
