import tkinter as tk
class NameApp:
    def setup(self, root):
        self.root = root
        self.root.title("Name Input GUI")
        self.root.geometry("400x200")

        # Create a frame for better organization
        frame = tk.Frame(root, padx=20, pady=20)
        frame.pack(expand=True)

        # Create a label
        label = tk.Label(frame, text="Enter your name:", font=("Arial", 14))
        label.pack(pady=10)

        # Create an entry widget
        self.entry = tk.Entry(frame, font=("Arial", 12), width=30)
        self.entry.pack(pady=5)

        # Create a button to save the name
        button = tk.Button(frame, text="Save Name", font=("Arial", 12), command=self.save_name)
        button.pack(pady=10)

    def save_name(self):
        global name
        name = self.entry.get()
        self.root.destroy()  # Close the GUI window

def main_name_app():
    root = tk.Tk()
    app = NameApp()
    app.setup(root)
    root.mainloop()
    return name

if __name__ == "__main__":
    main_name_app()
