import tkinter as tk
from tkinter import messagebox
import json
import os


class PhoneBookApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Phone Book")
        self.root.geometry("500x400")

        self.phonebook_file = "phonebook.json"
        self.phonebook = self.load_phonebook()

        # GUI Elements
        self.name_var = tk.StringVar()
        self.number_var = tk.StringVar()

        self.name_label = tk.Label(root, text="Name", font=("Helvetica", 12))
        self.name_label.pack(pady=5)
        self.name_entry = tk.Entry(root, textvariable=self.name_var, font=("Helvetica", 12), width=25)
        self.name_entry.pack(pady=5)

        self.number_label = tk.Label(root, text="Phone Number", font=("Helvetica", 12))
        self.number_label.pack(pady=5)
        self.number_entry = tk.Entry(root, textvariable=self.number_var, font=("Helvetica", 12), width=25)
        self.number_entry.pack(pady=5)

        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)

        self.save_button = tk.Button(button_frame, text="Save", command=self.save_number, font=("Helvetica", 12),
                                     width=10, bg="green", fg="white")
        self.save_button.grid(row=0, column=0, padx=5)

        self.delete_button = tk.Button(button_frame, text="Delete", command=self.delete_number, font=("Helvetica", 12),
                                       width=10, bg="red", fg="white")
        self.delete_button.grid(row=0, column=1, padx=5)

        self.choose_button = tk.Button(button_frame, text="Choose", command=self.choose_number, font=("Helvetica", 12),
                                       width=10, bg="blue", fg="white")
        self.choose_button.grid(row=0, column=2, padx=5)

        self.numbers_listbox = tk.Listbox(root, font=("Helvetica", 12), width=50)
        self.numbers_listbox.pack(pady=10)
        self.update_listbox()

    def load_phonebook(self):
        if not os.path.exists(self.phonebook_file):
            return {}
        with open(self.phonebook_file, "r") as f:
            return json.load(f)

    def save_phonebook(self):
        with open(self.phonebook_file, "w") as f:
            json.dump(self.phonebook, f)

    def update_listbox(self):
        self.numbers_listbox.delete(0, tk.END)
        for name, number in self.phonebook.items():
            self.numbers_listbox.insert(tk.END, f"{name}: {number}")

    def save_number(self):
        name = self.name_var.get().strip()
        number = self.number_var.get().strip()
        if name and number:
            self.phonebook[name] = number
            self.save_phonebook()
            self.update_listbox()
            self.name_var.set("")
            self.number_var.set("")
            messagebox.showinfo("Success", "Number saved successfully!")
        else:
            messagebox.showwarning("Input Error", "Please enter both name and number.")

    def delete_number(self):
        selected = self.numbers_listbox.curselection()
        if selected:
            name = self.numbers_listbox.get(selected[0]).split(":")[0]
            if name in self.phonebook:
                del self.phonebook[name]
                self.save_phonebook()
                self.update_listbox()
                messagebox.showinfo("Success", "Number deleted successfully!")
        else:
            messagebox.showwarning("Selection Error", "Please select a number to delete.")

    def choose_number(self):
        global final_num
        selected = self.numbers_listbox.curselection()
        if selected:
            number = self.numbers_listbox.get(selected[0]).split(":")[1].strip()
            messagebox.showinfo("Chosen Number", f"Selected Phone Number: {number}")
            self.root.destroy()  # Close the GUI after showing the chosen number
            final_num= number
        else:
            messagebox.showwarning("Selection Error", "Please select a number to choose.")

def phone_main():
    root = tk.Tk()
    app = PhoneBookApp(root)
    root.mainloop()
    return final_num