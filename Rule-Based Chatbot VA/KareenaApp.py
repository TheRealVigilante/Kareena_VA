import threading
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

import assistant_core as core
import NameApp


class KareenaApp(toga.App):
    def __init__(self):
        super().__init__("Kareena VA", "org.kareena.main")
        self._stop_event = threading.Event()
        self._voice_thread = None

    # ------------------------------------------------------------------
    # Startup
    # ------------------------------------------------------------------

    def startup(self):
        # --- Chat log ---
        self._chat_log = toga.MultilineTextInput(
            readonly=True,
            style=Pack(flex=1, padding=5)
        )

        # --- Status bar ---
        self._status_label = toga.Label(
            "Status: Idle",
            style=Pack(padding=(0, 5, 5, 5))
        )

        # --- Buttons ---
        listen_btn = toga.Button(
            "🎤  Start Listening",
            on_press=self._start_listening,
            style=Pack(flex=1, padding=5)
        )
        stop_btn = toga.Button(
            "🔇  Stop",
            on_press=self._stop_listening,
            style=Pack(flex=1, padding=5)
        )
        exit_btn = toga.Button(
            "✕  Exit",
            on_press=self._exit_app,
            style=Pack(flex=1, padding=5)
        )

        btn_row = toga.Box(
            children=[listen_btn, stop_btn, exit_btn],
            style=Pack(direction=ROW, padding=5)
        )

        # --- Root layout ---
        root_box = toga.Box(
            children=[
                toga.Label(
                    "KAREENA VA",
                    style=Pack(padding=(10, 0, 5, 0), text_align="center", font_size=18)
                ),
                self._chat_log,
                self._status_label,
                btn_row,
            ],
            style=Pack(direction=COLUMN, padding=10)
        )

        self.main_window = toga.MainWindow(title="Kareena VA", size=(520, 560))
        self.main_window.content = root_box
        self.main_window.show()

        # Inject GUI callbacks into the core module
        core.set_gui_callbacks(
            log_fn=self._append_log,
            status_fn=self._set_status
        )

        # Ask for the user's name then greet
        self._thread(self._init_assistant)

    # ------------------------------------------------------------------
    # GUI helpers (called from background threads — Toga is thread-safe
    # for label/text updates via call_soon_threadsafe)
    # ------------------------------------------------------------------

    def _append_log(self, text):
        """Append a line to the chat log from any thread."""
        self.loop.call_soon_threadsafe(self._do_append_log, text)

    def _do_append_log(self, text):
        current = self._chat_log.value or ""
        self._chat_log.value = current + text + "\n"

    def _set_status(self, text):
        """Update the status label from any thread."""
        self.loop.call_soon_threadsafe(self._do_set_status, text)

    def _do_set_status(self, text):
        self._status_label.text = f"Status: {text}"

    # ------------------------------------------------------------------
    # Assistant lifecycle
    # ------------------------------------------------------------------

    def _thread(self, fn, *args):
        """Run fn(*args) in a daemon thread."""
        t = threading.Thread(target=fn, args=args, daemon=True)
        t.start()
        return t

    def _init_assistant(self):
        """Run once at startup: collect name, greet, then begin loop."""
        core.set_user_name(NameApp.main_name_app())
        core.greet()
        core.speak("I am Kareena, your virtual assistant. How can I help you?")
        core.intro()
        core.speak("Now, please tell me your first command.")
        core.take_query(self._stop_event)

    def _start_listening(self, widget):
        """Re-start the voice loop if it was stopped."""
        if self._voice_thread and self._voice_thread.is_alive():
            self._append_log("Already listening.")
            return
        self._stop_event.clear()
        self._voice_thread = self._thread(core.take_query, self._stop_event)
        self._set_status("Listening...")

    def _stop_listening(self, widget):
        self._stop_event.set()
        self._set_status("Stopped")
        self._append_log("Kareena: Voice loop stopped. Press 'Start Listening' to resume.")

    def _exit_app(self, widget):
        self._stop_event.set()
        core.terminate()
        self.exit()


def main():
    app = KareenaApp()
    app.main_loop()


if __name__ == "__main__":
    main()
