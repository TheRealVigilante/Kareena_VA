import toga
import time
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER


class StopWatchApp(toga.App):
    def __init__(self):
        super().__init__("Kareena VA", "org.kareena.stopwatch")
        self._running = False
        self._start_time = None
        self._elapsed = 0.0

    def startup(self):
        self._display = toga.Label(
            "00:00:00",
            style=Pack(padding=20, text_align=CENTER, font_size=36)
        )

        start_btn = toga.Button(
            "Start",
            on_press=self._start,
            style=Pack(padding=5, flex=1, background_color="#28a745", color="white")
        )

        reset_btn = toga.Button(
            "Reset",
            on_press=self._reset,
            style=Pack(padding=5, flex=1, background_color="#007bff", color="white")
        )

        btn_row = toga.Box(
            children=[start_btn, reset_btn],
            style=Pack(direction=ROW, padding=10)
        )

        box = toga.Box(
            children=[self._display, btn_row],
            style=Pack(direction=COLUMN, padding=20, alignment=CENTER)
        )

        self.main_window = toga.MainWindow(title="Stopwatch", size=(400, 200))
        self.main_window.content = box
        self.main_window.show()

    def _start(self, widget):
        if not self._running:
            self._running = True
            if self._start_time is None:
                self._start_time = time.time() - self._elapsed
            self._update()

    def _reset(self, widget):
        self._running = False
        self._start_time = None
        self._elapsed = 0.0
        self._display.text = "00:00:00"

    def _update(self):
        if self._running:
            self._elapsed = time.time() - self._start_time
            minutes, seconds = divmod(self._elapsed, 60)
            hours, minutes = divmod(minutes, 60)
            self._display.text = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
            self.loop.call_later(0.1, self._update)


def stopwatch_main():
    """Blocking call — opens the stopwatch window."""
    app = StopWatchApp()
    app.main_loop()
