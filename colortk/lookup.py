from kivy.lang.builder import Builder
from kivy.properties import ListProperty
from kivy.uix.screenmanager import Screen


Builder.load_file('lookup.kv')


class LookupScreen(Screen):
    srgb = ListProperty((1, 1, 1))
    color_name = '<COLOR NAME>'
