from kivy.lang.builder import Builder
from kivy.uix.screenmanager import Screen


Builder.load_file('lookup.kv')


class LookupScreen(Screen):
    color = (1, 0, 0, 1)
