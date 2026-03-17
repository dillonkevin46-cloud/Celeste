import customtkinter as ctk
from tkinter import messagebox, filedialog
import database
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkcalendar
import datetime

# ---------------------------------------------------------
# TO-DO VIEW
# ---------------------------------------------------------
class TodoView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True)
        self.current_month = datetime.datetime.now().strftime("%B %Y")
        self.is_archived = False
        self.create_widgets()
        self.refresh_grid()

    def create_widgets(self):
        # Header Frame
        self.header_frame = ctk.CTkFrame(self, corner_radius=10)
        self.header_frame.pack(fill="x", padx=20, pady=(20, 10))

        # Title
        self.title_label = ctk.CTkLabel(self.header_frame, text="Automated To-Do List", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.pack(side="left", padx=20, pady=15)

        # Progress
        self.progress_label = ctk.CTkLabel(self.header_frame, text="0%")
        self.progress_label.pack(side="right", padx=(5, 20))
        self.progress_bar = ctk.CTkProgressBar(self.header_frame, width=200)
        self.progress_bar.set(0)
        self.progress_bar.pack(side="right", padx=5)

        # Action Buttons
        self.actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.actions_frame.pack(fill="x", padx=20, pady=(0, 10))

        # Month Filter
        months = database.get_all_months()
        if not months:
            months = [self.current_month]

        self.month_filter = ctk.CTkComboBox(self.actions_frame, values=months, command=self.on_month_change, width=150)
        self.month_filter.set(self.current_month)
        self.month_filter.pack(side="left")

        self.btn_add = ctk.CTkButton(self.actions_frame, text="+ Add Task", command=self.open_task_dialog, width=120)
        self.btn_add.pack(side="left", padx=10)

        self.btn_delete = ctk.CTkButton(self.actions_frame, text="- Delete Selected", command=self.delete_selected_tasks, width=120, fg_color="#C8504B", hover_color="#8E3533")
        self.btn_delete.pack(side="left", padx=5)

        self.btn_archive = ctk.CTkButton(self.actions_frame, text="Archive Month", command=self.archive_month, width=120, fg_color="#565b5e", hover_color="#303335")
        self.btn_archive.pack(side="left", padx=10)

        self.btn_export = ctk.CTkButton(self.actions_frame, text="Export to Excel", command=self.export_to_excel, width=120)
        self.btn_export.pack(side="right")

        # Data Grid Header
        self.grid_header = ctk.CTkFrame(self, corner_radius=0, fg_color=("gray85", "gray25"))
        self.grid_header.pack(fill="x", padx=20)

        headers = ["Select", "Task Name", "Assignee", "Priority", "Due Date", "Status"]
        widths = [50, 300, 150, 100, 100, 100]
        for h, w in zip(headers, widths):
            ctk.CTkLabel(self.grid_header, text=h, width=w, anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10, pady=5)

        # Data Grid Body
        self.scrollable_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scrollable_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.task_checkboxes = {} # Map ID to Selection BooleanVar
        self.status_checkboxes = {} # Map ID to Status BooleanVar

        self.update_ui_state()

    def update_ui_state(self):
        self.is_archived = database.is_month_archived(self.current_month)

        state = "disabled" if self.is_archived else "normal"
        self.btn_add.configure(state=state)
        self.btn_delete.configure(state=state)
        self.btn_archive.configure(state=state)

    def on_month_change(self, choice):
        self.current_month = choice
        self.update_ui_state()
        self.refresh_grid()

    def archive_month(self):
        if messagebox.askyesno("Confirm Archive", f"Are you sure you want to archive {self.current_month}?\n\nThis will lock the current month and generate recurring KPI tasks for the next month."):
            database.archive_month(self.current_month)

            # Refresh month list
            months = database.get_all_months()
            self.month_filter.configure(values=months)

            self.update_ui_state()
            self.refresh_grid()
            messagebox.showinfo("Archived", f"{self.current_month} has been locked.")

    def refresh_grid(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.task_checkboxes.clear()
        self.status_checkboxes.clear()

        tasks = database.get_tasks(self.current_month)
        total_tasks = len(tasks)
        completed_tasks = 0

        for task in tasks:
            task_id, task_name, assignee, priority, due_date, status = task
            is_done = (status == "Done")
            if is_done:
                completed_tasks += 1

            row_frame = ctk.CTkFrame(self.scrollable_frame, corner_radius=5, fg_color=("gray95", "gray20"))
            row_frame.pack(fill="x", pady=2)

            # Selection Checkbox
            select_var = ctk.BooleanVar(value=False)
            self.task_checkboxes[task_id] = select_var
            ctk.CTkCheckBox(row_frame, text="", variable=select_var, width=50, state="disabled" if self.is_archived else "normal").pack(side="left", padx=10, pady=5)

            # Task Details
            ctk.CTkLabel(row_frame, text=task_name, width=300, anchor="w").pack(side="left", padx=10)
            ctk.CTkLabel(row_frame, text=assignee, width=150, anchor="w").pack(side="left", padx=10)
            ctk.CTkLabel(row_frame, text=priority, width=100, anchor="w").pack(side="left", padx=10)
            ctk.CTkLabel(row_frame, text=due_date, width=100, anchor="w").pack(side="left", padx=10)

            # Status Checkbox
            status_var = ctk.BooleanVar(value=is_done)
            self.status_checkboxes[task_id] = status_var

            def make_toggle(tid, svar):
                def toggle():
                    new_status = "Done" if svar.get() else "Pending"
                    database.update_task_status(tid, new_status)
                    self.update_progress()
                return toggle

            ctk.CTkCheckBox(row_frame, text="Done", variable=status_var, width=100, state="disabled" if self.is_archived else "normal", command=make_toggle(task_id, status_var)).pack(side="left", padx=10)

        # Update Progress
        if total_tasks > 0:
            percentage = completed_tasks / total_tasks
            self.progress_bar.set(percentage)
            self.progress_label.configure(text=f"{int(percentage * 100)}%")
        else:
            self.progress_bar.set(0)
            self.progress_label.configure(text="0%")

    def update_progress(self):
        total_tasks = len(self.status_checkboxes)
        if total_tasks == 0:
            self.progress_bar.set(0)
            self.progress_label.configure(text="0%")
            return

        completed_tasks = sum(1 for var in self.status_checkboxes.values() if var.get())
        percentage = completed_tasks / total_tasks
        self.progress_bar.set(percentage)
        self.progress_label.configure(text=f"{int(percentage * 100)}%")

    def delete_selected_tasks(self):
        to_delete = [tid for tid, var in self.task_checkboxes.items() if var.get()]
        if not to_delete:
            messagebox.showinfo("Info", "No tasks selected for deletion.")
            return

        if messagebox.askyesno("Confirm", f"Delete {len(to_delete)} selected task(s)?"):
            for tid in to_delete:
                database.delete_task(tid)
            self.refresh_grid()

    def open_task_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add New Task")
        dialog.geometry("400x450")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Task Name:").pack(pady=(10, 0))
        entry_name = ctk.CTkEntry(dialog, width=300)
        entry_name.pack(pady=5)

        ctk.CTkLabel(dialog, text="Assignee:").pack(pady=(10, 0))
        assignees = database.get_assignee_names()
        if not assignees:
            assignees = ["No Assignees Found"]
        combo_assignee = ctk.CTkComboBox(dialog, values=assignees, width=300)
        combo_assignee.pack(pady=5)

        ctk.CTkLabel(dialog, text="Priority:").pack(pady=(10, 0))
        combo_priority = ctk.CTkComboBox(dialog, values=["High", "Medium", "Low"], width=300)
        combo_priority.pack(pady=5)

        ctk.CTkLabel(dialog, text="Due Date:").pack(pady=(10, 0))

        cal_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        cal_frame.pack(pady=5)
        # Using tkcalendar DateEntry
        date_entry = tkcalendar.DateEntry(cal_frame, width=30, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        date_entry.pack()

        def save_task():
            name = entry_name.get()
            assignee = combo_assignee.get()
            priority = combo_priority.get()
            due = date_entry.get()

            if not name or not due:
                messagebox.showwarning("Warning", "Task Name and Due Date are required.")
                return

            database.add_task(self.current_month, name, assignee, priority, due, "Pending")
            dialog.destroy()
            self.refresh_grid()

        ctk.CTkButton(dialog, text="Save Task", command=save_task).pack(pady=20)

    def export_to_excel(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")], title="Export Tasks")
        if not filepath:
            return
        tasks = database.get_tasks(self.current_month)
        df = pd.DataFrame(tasks, columns=["ID", "Task Name", "Assignee", "Priority", "Due Date", "Status"])
        try:
            df.to_excel(filepath, index=False, engine='openpyxl')
            messagebox.showinfo("Success", f"Exported to {filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {e}")

# ---------------------------------------------------------
# KPI VIEW
# ---------------------------------------------------------
class KpiView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True)
        self.current_month = datetime.datetime.now().strftime("%B %Y")
        self.is_archived = False
        self.figure = None
        self.canvas = None
        self.ax = None
        self.create_widgets()

    def create_widgets(self):
        # Top half: Dynamic Combo Chart
        self.chart_frame = ctk.CTkFrame(self, corner_radius=10)
        self.chart_frame.pack(fill="x", padx=20, pady=(20, 10))

        # Build axes
        plt.style.use('dark_background')
        self.figure, self.ax = plt.subplots(figsize=(8, 3), dpi=100)
        self.figure.patch.set_facecolor('#2b2b2b')
        self.ax.set_facecolor('#2b2b2b')

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        # Bottom half: Actions & Grid
        self.actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.actions_frame.pack(fill="x", padx=20, pady=(0, 10))

        months = database.get_all_months()
        if not months:
            months = [self.current_month]

        self.month_filter = ctk.CTkComboBox(self.actions_frame, values=months, command=self.on_month_change, width=150)
        self.month_filter.set(self.current_month)
        self.month_filter.pack(side="left")

        self.btn_add_kpi = ctk.CTkButton(self.actions_frame, text="+ Add KPI Task", command=self.add_kpi_dialog, width=120)
        self.btn_add_kpi.pack(side="left", padx=10)

        self.btn_archive = ctk.CTkButton(self.actions_frame, text="Archive Month", command=self.archive_month, width=120, fg_color="#565b5e", hover_color="#303335")
        self.btn_archive.pack(side="left", padx=5)

        self.btn_export = ctk.CTkButton(self.actions_frame, text="Export to Excel", command=self.export_to_excel, width=120)
        self.btn_export.pack(side="right")

        # Scrollable Grid
        self.grid_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.grid_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.update_ui_state()
        self.build_kpi_grid()

    def update_ui_state(self):
        self.is_archived = database.is_month_archived(self.current_month)

        state = "disabled" if self.is_archived else "normal"
        self.btn_add_kpi.configure(state=state)
        self.btn_archive.configure(state=state)

    def on_month_change(self, choice):
        self.current_month = choice
        self.update_ui_state()
        self.build_kpi_grid()

    def archive_month(self):
        if messagebox.askyesno("Confirm Archive", f"Are you sure you want to archive {self.current_month}?\n\nThis will lock the current month and generate recurring KPI tasks for the next month."):
            database.archive_month(self.current_month)
            months = database.get_all_months()
            self.month_filter.configure(values=months)
            self.update_ui_state()
            self.build_kpi_grid()
            messagebox.showinfo("Archived", f"{self.current_month} has been locked.")

    def build_kpi_grid(self):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        db_cols = ["mon", "tue", "wed", "thu", "fri", "sat"]

        # Headers
        header_frame = ctk.CTkFrame(self.grid_frame, fg_color=("gray85", "gray25"), corner_radius=0)
        header_frame.pack(fill="x", pady=2)

        ctk.CTkLabel(header_frame, text="Task Name", width=250, anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10, pady=5)
        for day in days:
            ctk.CTkLabel(header_frame, text=day, width=60, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header_frame, text="Actions", width=120, font=ctk.CTkFont(weight="bold")).pack(side="right", padx=10)

        kpi_data = database.get_kpi_tasks(self.current_month)

        for kpi in kpi_data:
            task_id = kpi[0]
            task_name = kpi[1]
            vals = kpi[2:8]

            row_frame = ctk.CTkFrame(self.grid_frame, fg_color=("gray95", "gray20"), corner_radius=5)
            row_frame.pack(fill="x", pady=2)

            ctk.CTkLabel(row_frame, text=task_name, width=250, anchor="w").pack(side="left", padx=10, pady=5)

            for i, val in enumerate(vals):
                var = ctk.IntVar(value=val)
                col_name = db_cols[i]

                def make_toggle(tid, cname, v):
                    def toggle_kpi():
                        database.update_kpi_task_day(tid, cname, v.get())
                        self.draw_chart()
                    return toggle_kpi

                cb = ctk.CTkCheckBox(row_frame, text="", variable=var, width=60, state="disabled" if self.is_archived else "normal", command=make_toggle(task_id, col_name, var))
                cb.pack(side="left", padx=5)

            # Actions (Edit/Delete)
            actions_sub = ctk.CTkFrame(row_frame, fg_color="transparent")
            actions_sub.pack(side="right", padx=10)

            btn_edit = ctk.CTkButton(actions_sub, text="Edit", width=50, state="disabled" if self.is_archived else "normal", command=lambda tid=task_id, tname=task_name: self.edit_kpi_dialog(tid, tname))
            btn_edit.pack(side="left", padx=2)

            btn_del = ctk.CTkButton(actions_sub, text="Del", width=50, state="disabled" if self.is_archived else "normal", fg_color="#C8504B", hover_color="#8E3533", command=lambda tid=task_id: self.delete_kpi(tid))
            btn_del.pack(side="left", padx=2)

        self.draw_chart()

    def add_kpi_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add KPI Task")
        dialog.geometry("300x150")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="KPI Task Name:").pack(pady=(20, 5))
        entry_name = ctk.CTkEntry(dialog, width=250)
        entry_name.pack(pady=5)

        def save():
            name = entry_name.get()
            if name:
                database.add_kpi_task(self.current_month, name)
                dialog.destroy()
                self.build_kpi_grid()

        ctk.CTkButton(dialog, text="Save", command=save).pack(pady=10)

    def edit_kpi_dialog(self, task_id, current_name):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit KPI Task")
        dialog.geometry("300x150")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="KPI Task Name:").pack(pady=(20, 5))
        entry_name = ctk.CTkEntry(dialog, width=250)
        entry_name.insert(0, current_name)
        entry_name.pack(pady=5)

        def save():
            name = entry_name.get()
            if name:
                database.update_kpi_task_name(task_id, name)
                dialog.destroy()
                self.build_kpi_grid()

        ctk.CTkButton(dialog, text="Update", command=save).pack(pady=10)

    def delete_kpi(self, task_id):
        if messagebox.askyesno("Confirm", "Delete this KPI task?"):
            database.delete_kpi_task(task_id)
            self.build_kpi_grid()

    def draw_chart(self):
        kpi_data = database.get_kpi_tasks(self.current_month)
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

        if not kpi_data:
            percentages = [0]*6
        else:
            total_tasks = len(kpi_data)
            counts = [0]*6
            for kpi in kpi_data:
                for i in range(6):
                    counts[i] += kpi[i+2]

            percentages = [(c / total_tasks) * 100 for c in counts]

        self.ax.clear()

        # Color based on theme
        bar_color = '#7A1B1B' # Matched sidebar dark red
        bars = self.ax.bar(days, percentages, color=bar_color)

        # Target line
        self.ax.axhline(y=75, color='#1F6AA5', linestyle='-', linewidth=2, label='Target 75%')

        self.ax.set_ylim(0, 100)
        self.ax.set_ylabel('Completion %', color='white')
        self.ax.tick_params(colors='white')

        self.figure.tight_layout()
        self.canvas.draw()

    def export_to_excel(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
        if not filepath: return
        kpis = database.get_kpi_tasks(self.current_month)
        df = pd.DataFrame(kpis, columns=["ID", "Task Name", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"])
        try:
            df.to_excel(filepath, index=False, engine='openpyxl')
            messagebox.showinfo("Success", f"KPIs exported to {filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {e}")

# ---------------------------------------------------------
# SETTINGS VIEW
# ---------------------------------------------------------
class SettingsView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True)

        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(0, weight=1)

        # User Management Section
        self.user_frame = ctk.CTkFrame(self, corner_radius=10)
        self.user_frame.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=20)
        self.build_user_management()

        # Assignee Management Section
        self.assignee_frame = ctk.CTkFrame(self, corner_radius=10)
        self.assignee_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=20)
        self.build_assignee_management()

    # --- Users ---
    def build_user_management(self):
        for widget in self.user_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.user_frame, text="User Management", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15)

        list_frame = ctk.CTkScrollableFrame(self.user_frame, fg_color="transparent")
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        users = database.get_users()
        for u in users:
            uid, uname, upass = u
            row = ctk.CTkFrame(list_frame, fg_color=("gray95", "gray20"))
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=uname, width=150, anchor="w").pack(side="left", padx=10, pady=5)

            btn_del = ctk.CTkButton(row, text="Del", width=40, fg_color="#C8504B", hover_color="#8E3533", command=lambda x=uid: self.delete_user(x))
            btn_del.pack(side="right", padx=5)

            btn_edit = ctk.CTkButton(row, text="Edit", width=40, command=lambda x=uid, y=uname, z=upass: self.user_dialog(x, y, z))
            btn_edit.pack(side="right", padx=5)

        ctk.CTkButton(self.user_frame, text="+ Add User", command=lambda: self.user_dialog(), fg_color="#7A1B1B", hover_color="#5a1414").pack(pady=15)

    def user_dialog(self, uid=None, uname="", upass=""):
        dialog = ctk.CTkToplevel(self)
        dialog.title("User" if uid else "New User")
        dialog.geometry("300x250")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Username:").pack(pady=(20, 5))
        e_name = ctk.CTkEntry(dialog, width=200)
        e_name.insert(0, uname)
        e_name.pack()

        ctk.CTkLabel(dialog, text="Password:").pack(pady=(10, 5))
        e_pass = ctk.CTkEntry(dialog, width=200, show="*")
        e_pass.insert(0, upass)
        e_pass.pack()

        def save():
            n, p = e_name.get(), e_pass.get()
            if n and p:
                if uid: database.update_user(uid, n, p)
                else: database.add_user(n, p)
                dialog.destroy()
                self.build_user_management()

        ctk.CTkButton(dialog, text="Save", command=save, fg_color="#7A1B1B", hover_color="#5a1414").pack(pady=20)

    def delete_user(self, uid):
        if messagebox.askyesno("Confirm", "Delete user?"):
            database.delete_user(uid)
            self.build_user_management()

    # --- Assignees ---
    def build_assignee_management(self):
        for widget in self.assignee_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.assignee_frame, text="Assignee Management", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15)

        list_frame = ctk.CTkScrollableFrame(self.assignee_frame, fg_color="transparent")
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        assignees = database.get_assignees()
        for a in assignees:
            aid, aname = a
            row = ctk.CTkFrame(list_frame, fg_color=("gray95", "gray20"))
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=aname, width=150, anchor="w").pack(side="left", padx=10, pady=5)

            btn_del = ctk.CTkButton(row, text="Del", width=40, fg_color="#C8504B", hover_color="#8E3533", command=lambda x=aid: self.delete_assignee(x))
            btn_del.pack(side="right", padx=5)

            btn_edit = ctk.CTkButton(row, text="Edit", width=40, command=lambda x=aid, y=aname: self.assignee_dialog(x, y))
            btn_edit.pack(side="right", padx=5)

        ctk.CTkButton(self.assignee_frame, text="+ Add Assignee", command=lambda: self.assignee_dialog(), fg_color="#7A1B1B", hover_color="#5a1414").pack(pady=15)

    def assignee_dialog(self, aid=None, aname=""):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Assignee" if aid else "New Assignee")
        dialog.geometry("300x150")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Name:").pack(pady=(20, 5))
        e_name = ctk.CTkEntry(dialog, width=200)
        e_name.insert(0, aname)
        e_name.pack()

        def save():
            n = e_name.get()
            if n:
                if aid: database.update_assignee(aid, n)
                else: database.add_assignee(n)
                dialog.destroy()
                self.build_assignee_management()

        ctk.CTkButton(dialog, text="Save", command=save, fg_color="#7A1B1B", hover_color="#5a1414").pack(pady=15)

    def delete_assignee(self, aid):
        if messagebox.askyesno("Confirm", "Delete assignee?"):
            database.delete_assignee(aid)
            self.build_assignee_management()
