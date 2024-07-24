import tkinter as tk
import time


class StopwatchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Stopwatch")
        self.root.geometry("400x200")

        self.time_var = tk.StringVar()
        self.time_var.set("00:00:00")

        self.label = tk.Label(root, textvariable=self.time_var, font=("Helvetica", 48), bg="black", fg="white")
        self.label.pack(pady=20)

        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)

        self.start_button = tk.Button(button_frame, text="Start", command=self.start, font=("Helvetica", 12), width=10,
                                      bg="green", fg="white")
        self.start_button.grid(row=0, column=0, padx=5)

        self.reset_button = tk.Button(button_frame, text="Reset", command=self.reset, font=("Helvetica", 12), width=10,
                                      bg="blue", fg="white")
        self.reset_button.grid(row=0, column=1, padx=5)

        self.running = False
        self.start_time = None
        self.elapsed_time = 0
        self.timer_id = None

    def start(self):
        if not self.running:
            self.running = True
            if self.start_time is None:
                self.start_time = time.time() - self.elapsed_time
            self.update()

    def reset(self):
        self.running = False
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        self.start_time = None
        self.elapsed_time = 0
        self.time_var.set("00:00:00")

    def update(self):
        if self.running:
            self.elapsed_time = time.time() - self.start_time
            minutes, seconds = divmod(self.elapsed_time, 60)
            hours, minutes = divmod(minutes, 60)
            time_str = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
            self.time_var.set(time_str)
            self.timer_id = self.root.after(100, self.update)

def stopwatch_main():
    root = tk.Tk()
    app = StopwatchApp(root)
    root.mainloop()
