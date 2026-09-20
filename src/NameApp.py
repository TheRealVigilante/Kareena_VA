import toga
from toga.style import Pack
from toga.style.pack import COLUMN, CENTER


class NameApp(toga.App):
    def __init__(self, result_holder):
        super().__init__("Kareena VA", "org.kareena.name")
        self._result_holder = result_holder

    def startup(self):
        self._name_input = toga.TextInput(
            placeholder="Type your name here...",
            style=Pack(flex=1, padding=5)
        )

        confirm_btn = toga.Button(
            "Confirm",
            on_press=self._save_name,
            style=Pack(padding=5)
        )

        box = toga.Box(
            children=[
                toga.Label(
                    "What should I call you?",
                    style=Pack(padding=(10, 5), text_align=CENTER)
                ),
                self._name_input,
                confirm_btn,
            ],
            style=Pack(direction=COLUMN, padding=20, alignment=CENTER)
        )

        self.main_window = toga.MainWindow(title="Kareena VA — Enter Name", size=(400, 180))
        self.main_window.content = box
        self.main_window.show()

    def _save_name(self, widget):
        name = self._name_input.value.strip()
        if name:
            self._result_holder["name"] = name
            self.exit()


def main_name_app():
    """Blocking call — opens the name window and returns the entered name."""
    result = {}
    app = NameApp(result)
    app.main_loop()
    return result.get("name", "")
