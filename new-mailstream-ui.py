from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.uix.textinput import TextInput
import sparkpostsatellite
import os


class MyGrid(GridLayout):

    def __init__(self, **kwargs):
        super(MyGrid, self).__init__(**kwargs)
        self.cols = 1

        self.add_widget(Label(text="", size_hint_y=self.size_hint_y * 0.4))

        self.inside_layout = GridLayout()
        self.inside_layout.cols = 2
        self.inside_layout.orientation = "tb-lr"

        # Build top interface
        self.textinput = TextInput(text='Subaccount_Name', multiline=False, size_hint_y=self.size_hint_y * 0.1)
        self.inside_layout.add_widget(Label(text='Subaccount Name: ', size_hint_y=self.size_hint_y * 0.1))
        self.inside_layout.add_widget(self.textinput)
        button = Button(text="Create Subaccount", size_hint_y=self.size_hint_y * 0.2, on_press=self.add_subaccount)
        self.add_widget(self.inside_layout)
        self.add_widget(button)
        self.text_label = Label(text="")
        self.add_widget(self.text_label)
        self.add_widget(Label(text=""))

    def add_subaccount(self, instance):
        self.text_label.text = "Created Subaccount:  " + self.textinput.text
        central_api_key = os.environ.get("CENTRAL_API_KEY")
        satellite_api_key = os.environ.get("SATELLITE_API_KEY")
        sparkpostsatellite.add_new_mailstream(self.textinput.text, central_api_key, satellite_api_key)


class MyApp(App):
    def build(self):
        return MyGrid()


if __name__ == "__main__":
    app = MyApp()
    app.run()
