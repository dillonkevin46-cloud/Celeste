import customtkinter as ctk
from database import authenticate
from tkinter import messagebox

class LoginWindow(ctk.CTkFrame):
    def __init__(self, parent, on_login_success):
        super().__init__(parent)
        self.parent = parent
        self.on_login_success = on_login_success

        self.pack(fill="both", expand=True)

        self.create_widgets()

    def create_widgets(self):
        # Center frame
        self.center_frame = ctk.CTkFrame(self, corner_radius=10)
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Title
        self.title_label = ctk.CTkLabel(
            self.center_frame,
            text="Tradecore Operations Hub",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(pady=(20, 20), padx=40)

        # Username
        self.username_entry = ctk.CTkEntry(
            self.center_frame,
            placeholder_text="Username",
            width=200
        )
        self.username_entry.pack(pady=(0, 10), padx=40)

        # Password
        self.password_entry = ctk.CTkEntry(
            self.center_frame,
            placeholder_text="Password",
            show="*",
            width=200
        )
        self.password_entry.pack(pady=(0, 20), padx=40)

        # Login Button
        self.login_button = ctk.CTkButton(
            self.center_frame,
            text="Login",
            command=self.attempt_login,
            width=200
        )
        self.login_button.pack(pady=(0, 20), padx=40)

        # Bind Enter key
        self.password_entry.bind("<Return>", lambda event: self.attempt_login())
        self.username_entry.bind("<Return>", lambda event: self.attempt_login())

    def attempt_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return

        if authenticate(username, password):
            self.destroy()
            self.on_login_success()
        else:
            messagebox.showerror("Error", "Invalid username or password")
