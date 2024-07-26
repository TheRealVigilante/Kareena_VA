import tkinter as tk
from tkinter import messagebox
import pygame


class TimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Countdown Timer")
        self.root.geometry("400x250")

        self.time_var = tk.StringVar()

        self.label = tk.Label(root, text="Enter time (HH:MM:SS):", font=("Helvetica", 12))
        self.label.pack(pady=10)

        self.entry = tk.Entry(root, textvariable=self.time_var, font=("Helvetica", 12), width=10)
        self.entry.pack(pady=5)

        self.start_button = tk.Button(root, text="Start Timer", command=self.start_timer, font=("Helvetica", 12))
        self.start_button.pack(pady=10)

        self.time_display = tk.Label(root, text="", font=("Helvetica", 24))
        self.time_display.pack(pady=10)

        self.timer_running = False

        # Initialize Pygame mixer
        pygame.mixer.init()
        self.alarm_sound = pygame.mixer.Sound("Alarm.mp3")  # Replace with your alarm sound file

    def start_timer(self):
        if self.timer_running:
            return

        time_str = self.time_var.get()
        try:
            h, m, s = map(int, time_str.split(':'))
            total_seconds = h * 3600 + m * 60 + s
        except ValueError:
            messagebox.showerror("Invalid Time", "Please enter a valid time in HH:MM:SS format.")
            return

        self.time_var.set("")
        self.timer_running = True
        self.countdown(total_seconds)

    def countdown(self, remaining_seconds):
        if remaining_seconds <= 0:
            self.time_display.config(text="Time's up!")
            self.timer_running = False
            self.play_alarm()
            return

        h = remaining_seconds // 3600
        m = (remaining_seconds % 3600) // 60
        s = remaining_seconds % 60

        time_str = f"{h:02}:{m:02}:{s:02}"
        self.time_display.config(text=time_str)

        self.root.after(1000, self.countdown, remaining_seconds - 1)

    def play_alarm(self):
        self.alarm_sound.play()

def timer_main():
    root = tk.Tk()
    app = TimerApp(root)
    root.mainloop()