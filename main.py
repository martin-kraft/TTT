from kivy.config import Config
#Config.set('graphics', 'position', 'custom')
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from PlayingField import PlayingField
from StatView import StatView
from PlayerHub import PlayerHub

Window.size = (1440, 600)

class TTTApp(App):
    def build(self):
        root = BoxLayout()

        # Player managment; used to manage games
        # extract information about played games
        playerHub = PlayerHub()

        root.add_widget(PlayingField(playerHub))
        root.add_widget(StatView(playerHub))
        return root

if __name__ == '__main__':
    TTTApp().run()