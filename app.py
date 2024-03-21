from shiny import App

from ui import ui_main
from server import server

app = App(ui_main, server)
