import toga
import pygame
from toga.style import Pack
from toga.style.pack import COLUMN, CENTER


class TimerApp(toga.App):
    def __init__(self):
        super().__init__("Kareena VA", "org.kareena.timer")
        self._running = False

        # Initialise pygame mixer for alarm sound
        pygame.mixer.init()
        self._alarm = pygame.mixer.Sound("Alarm.mp3")

    def startup(self):
        self._time_input = toga.TextInput(
            placeholder="HH:MM:SS",
            style=Pack(flex=1, padding=5)
        )

        self._display = toga.Label(
            "",
            style=Pack(padding=10, text_align=CENTER, font_size=24)
        )

        start_btn = toga.Button(
            "Start Timer",
            on_press=self._start_timer,
            style=Pack(padding=5)
        )

        box = toga.Box(
            children=[
                toga.Label(
                    "Enter time (HH:MM:SS):",
                    style=Pack(padding=(10, 5), text_align=CENTER)
                ),
                self._time_input,
                start_btn,
                self._display,
            ],
            style=Pack(direction=COLUMN, padding=20, alignment=CENTER)
        )

        self.main_window = toga.MainWindow(title="Countdown Timer", size=(400, 260))
        self.main_window.content = box
        self.main_window.show()

    def _start_timer(self, widget):
        if self._running:
            return
        time_str = self._time_input.value.strip()
        try:
            h, m, s = map(int, time_str.split(":"))
            total_seconds = h * 3600 + m * 60 + s
        except ValueError:
            self.main_window.error_dialog("Invalid Time", "Please enter a valid time in HH:MM:SS format.")
            return

        self._time_input.value = ""
        self._running = True
        self._countdown(total_seconds)

    def _countdown(self, remaining):
        if remaining <= 0:
            self._display.text = "Time's up!"
            self._running = False
            self._alarm.play()
            return

        h = remaining // 3600
        m = (remaining % 3600) // 60
        s = remaining % 60
        self._display.text = f"{h:02}:{m:02}:{s:02}"

        # Schedule next tick after 1 second using Toga's async loop
        self.loop.call_later(1, self._countdown, remaining - 1)


def timer_main():
    """Blocking call — opens the countdown timer window."""
    app = TimerApp()
    app.main_loop()
