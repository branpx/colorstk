from kivy.app import App
from kivy.lang.builder import Builder
from kivy.properties import ListProperty
from kivy.uix.actionbar import ActionButton
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen


Builder.load_file('palettes.kv')


class PalettesScreen(Screen):
    palettes = ListProperty()

    def on_pre_enter(self):
        root = App.get_running_app().root
        root.ids.action_previous.title = 'Palettes'
        self.new_button = ActionButton(text='New')
        self.new_button.bind(on_release=NewPalettePopup().open)
        root.ids.action_view.add_widget(self.new_button)

    def on_pre_leave(self):
        root = App.get_running_app().root
        root.ids.screen_menu.toggled = False
        root.ids.action_view.remove_widget(self.new_button)


class NewPalettePopup(Popup):
    pass
