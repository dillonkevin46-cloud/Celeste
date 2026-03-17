import customtkinter as ctk
import database
from auth import LoginWindow
from views import TodoView, KpiView

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Tradecore Operations Hub")
        self.geometry("1100x700")

        # Initialize Database
        database.init_db()

        # Start with login screen
        self.login_window = LoginWindow(self, self.show_main_app)

    def show_main_app(self):
        # Configure grid layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Create sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Tradecore\nOps Hub",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 30))

        self.btn_todo = ctk.CTkButton(
            self.sidebar_frame,
            text="To-Do List",
            command=self.show_todo_view
        )
        self.btn_todo.grid(row=1, column=0, padx=20, pady=10)

        self.btn_kpi = ctk.CTkButton(
            self.sidebar_frame,
            text="KPI Tracker",
            command=self.show_kpi_view
        )
        self.btn_kpi.grid(row=2, column=0, padx=20, pady=10)

        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(
            self.sidebar_frame,
            values=["Light", "Dark", "System"],
            command=self.change_appearance_mode_event
        )
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 20))

        # Main content area
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew")

        # Create views
        self.todo_view = TodoView(self.main_frame)
        self.kpi_view = KpiView(self.main_frame)

        # Show initial view
        self.show_todo_view()
        self.appearance_mode_optionemenu.set("System")

    def show_todo_view(self):
        self.kpi_view.pack_forget()
        self.todo_view.pack(fill="both", expand=True)
        self.btn_todo.configure(fg_color=["#3B8ED0", "#1F6AA5"])
        self.btn_kpi.configure(fg_color="transparent")
        self.todo_view.refresh_grid()

    def show_kpi_view(self):
        self.todo_view.pack_forget()
        self.kpi_view.pack(fill="both", expand=True)
        self.btn_kpi.configure(fg_color=["#3B8ED0", "#1F6AA5"])
        self.btn_todo.configure(fg_color="transparent")
        self.kpi_view.draw_chart()

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

if __name__ == "__main__":
    app = App()
    app.mainloop()
