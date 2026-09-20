import json
import os
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW


PHONEBOOK_FILE = "phonebook.json"


def _load_phonebook():
    if not os.path.exists(PHONEBOOK_FILE):
        return {}
    with open(PHONEBOOK_FILE, "r") as f:
        return json.load(f)


def _save_phonebook(phonebook):
    with open(PHONEBOOK_FILE, "w") as f:
        json.dump(phonebook, f)


class PhoneBookApp(toga.App):
    def __init__(self, result_holder):
        super().__init__("Kareena VA", "org.kareena.phonebook")
        self._result_holder = result_holder
        self._phonebook = _load_phonebook()

    def startup(self):
        # --- Input fields ---
        self._name_input = toga.TextInput(
            placeholder="Name",
            style=Pack(flex=1, padding=5)
        )
        self._number_input = toga.TextInput(
            placeholder="Phone Number",
            style=Pack(flex=1, padding=5)
        )

        # --- Contact list ---
        self._table = toga.Table(
            headings=["Name", "Number"],
            data=self._table_data(),
            style=Pack(flex=1, padding=5)
        )

        # --- Buttons ---
        save_btn = toga.Button(
            "Save",
            on_press=self._save_contact,
            style=Pack(padding=5, flex=1)
        )
        delete_btn = toga.Button(
            "Delete",
            on_press=self._delete_contact,
            style=Pack(padding=5, flex=1)
        )
        choose_btn = toga.Button(
            "Choose",
            on_press=self._choose_contact,
            style=Pack(padding=5, flex=1)
        )

        btn_row = toga.Box(
            children=[save_btn, delete_btn, choose_btn],
            style=Pack(direction=ROW, padding=5)
        )

        box = toga.Box(
            children=[
                toga.Label("Name:", style=Pack(padding=(5, 5, 0, 5))),
                self._name_input,
                toga.Label("Phone Number:", style=Pack(padding=(5, 5, 0, 5))),
                self._number_input,
                btn_row,
                self._table,
            ],
            style=Pack(direction=COLUMN, padding=10)
        )

        self.main_window = toga.MainWindow(title="Phone Book", size=(500, 420))
        self.main_window.content = box
        self.main_window.show()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _table_data(self):
        return [(name, number) for name, number in self._phonebook.items()]

    def _refresh_table(self):
        self._table.data = self._table_data()

    # ------------------------------------------------------------------
    # Button handlers
    # ------------------------------------------------------------------

    def _save_contact(self, widget):
        name = self._name_input.value.strip()
        number = self._number_input.value.strip()
        if name and number:
            self._phonebook[name] = number
            _save_phonebook(self._phonebook)
            self._refresh_table()
            self._name_input.value = ""
            self._number_input.value = ""
            self.main_window.info_dialog("Success", "Contact saved successfully!")
        else:
            self.main_window.error_dialog("Input Error", "Please enter both a name and a phone number.")

    def _delete_contact(self, widget):
        selection = self._table.selection
        if selection:
            name = selection.name
            if name in self._phonebook:
                del self._phonebook[name]
                _save_phonebook(self._phonebook)
                self._refresh_table()
                self.main_window.info_dialog("Success", "Contact deleted successfully!")
        else:
            self.main_window.error_dialog("Selection Error", "Please select a contact to delete.")

    def _choose_contact(self, widget):
        selection = self._table.selection
        if selection:
            number = selection.number
            self._result_holder["number"] = number
            self.exit()
        else:
            self.main_window.error_dialog("Selection Error", "Please select a contact to choose.")


def phone_main():
    """Blocking call — opens the phonebook and returns the chosen number."""
    result = {}
    app = PhoneBookApp(result)
    app.main_loop()
    return result.get("number", "")
