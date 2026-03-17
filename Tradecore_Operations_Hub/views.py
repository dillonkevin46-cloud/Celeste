import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import database
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class TodoView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill="both", expand=True)
        self.create_widgets()
        self.refresh_grid()

    def create_widgets(self):
        # Top Frame for Actions & Progress
        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.pack(fill="x", padx=10, pady=10)

        # Progress Bar
        self.progress_label = ctk.CTkLabel(self.top_frame, text="Task Completion: 0%")
        self.progress_label.pack(side="left", padx=(10, 5))

        self.progress_bar = ctk.CTkProgressBar(self.top_frame, width=200)
        self.progress_bar.set(0)
        self.progress_bar.pack(side="left", padx=5)

        # Buttons
        self.btn_add = ctk.CTkButton(self.top_frame, text="Add Task", command=self.open_task_dialog)
        self.btn_add.pack(side="right", padx=5)

        self.btn_edit = ctk.CTkButton(self.top_frame, text="Edit Task", command=self.edit_selected_task)
        self.btn_edit.pack(side="right", padx=5)

        self.btn_delete = ctk.CTkButton(self.top_frame, text="Delete Task", command=self.delete_selected_task)
        self.btn_delete.pack(side="right", padx=5)

        self.btn_export = ctk.CTkButton(self.top_frame, text="Export to Excel", command=self.export_to_excel)
        self.btn_export.pack(side="right", padx=5)

        # Treeview (Data Grid)
        # Using standard ttk.Treeview as CustomTkinter doesn't have a native data grid yet
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b", borderwidth=0)
        style.map("Treeview", background=[("selected", "#1f538d")])
        style.configure("Treeview.Heading", background="#565b5e", foreground="white", font=("Arial", 10, "bold"))

        self.grid_frame = ctk.CTkFrame(self)
        self.grid_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        columns = ("ID", "Task Name", "Assignee", "Priority", "Due Date", "Status")
        self.tree = ttk.Treeview(self.grid_frame, columns=columns, show="headings")

        for col in columns:
            self.tree.heading(col, text=col)
            if col == "ID":
                self.tree.column(col, width=50, anchor="center")
            else:
                self.tree.column(col, anchor="w")

        # Scrollbar for Treeview
        self.scrollbar = ttk.Scrollbar(self.grid_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

    def refresh_grid(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        tasks = database.get_tasks()
        total_tasks = len(tasks)
        completed_tasks = 0

        for task in tasks:
            self.tree.insert("", "end", values=task)
            if task[5] == "Done":
                completed_tasks += 1

        if total_tasks > 0:
            percentage = completed_tasks / total_tasks
            self.progress_bar.set(percentage)
            self.progress_label.configure(text=f"Task Completion: {int(percentage * 100)}%")
        else:
            self.progress_bar.set(0)
            self.progress_label.configure(text="Task Completion: 0%")

    def open_task_dialog(self, task_data=None):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add Task" if task_data is None else "Edit Task")
        dialog.geometry("400x500")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Task Name:").pack(pady=(10, 0))
        entry_name = ctk.CTkEntry(dialog, width=300)
        entry_name.pack(pady=5)

        ctk.CTkLabel(dialog, text="Assignee:").pack(pady=(10, 0))
        assignees = database.get_assignees()
        combo_assignee = ctk.CTkComboBox(dialog, values=assignees, width=300)
        combo_assignee.pack(pady=5)

        ctk.CTkLabel(dialog, text="Priority:").pack(pady=(10, 0))
        combo_priority = ctk.CTkComboBox(dialog, values=["High", "Medium", "Low"], width=300)
        combo_priority.pack(pady=5)

        ctk.CTkLabel(dialog, text="Due Date (YYYY-MM-DD):").pack(pady=(10, 0))
        entry_due = ctk.CTkEntry(dialog, width=300)
        entry_due.pack(pady=5)

        ctk.CTkLabel(dialog, text="Status:").pack(pady=(10, 0))
        combo_status = ctk.CTkComboBox(dialog, values=["Pending", "Done"], width=300)
        combo_status.pack(pady=5)

        if task_data:
            entry_name.insert(0, task_data[1])
            combo_assignee.set(task_data[2])
            combo_priority.set(task_data[3])
            entry_due.insert(0, task_data[4])
            combo_status.set(task_data[5])

        def save_task():
            name = entry_name.get()
            assignee = combo_assignee.get()
            priority = combo_priority.get()
            due = entry_due.get()
            status = combo_status.get()

            if not name or not due:
                messagebox.showwarning("Warning", "Task Name and Due Date are required.")
                return

            if task_data:
                database.update_task(task_data[0], name, assignee, priority, due, status)
            else:
                database.add_task(name, assignee, priority, due, status)

            dialog.destroy()
            self.refresh_grid()

        ctk.CTkButton(dialog, text="Save", command=save_task).pack(pady=20)

    def edit_selected_task(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a task to edit.")
            return

        item = self.tree.item(selected[0])
        task_data = item['values']
        self.open_task_dialog(task_data)

    def delete_selected_task(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a task to delete.")
            return

        if messagebox.askyesno("Confirm", "Are you sure you want to delete this task?"):
            item = self.tree.item(selected[0])
            task_id = item['values'][0]
            database.delete_task(task_id)
            self.refresh_grid()

    def export_to_excel(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")],
            title="Export Tasks to Excel"
        )
        if not filepath:
            return

        tasks = database.get_tasks()
        df = pd.DataFrame(tasks, columns=["ID", "Task Name", "Assignee", "Priority", "Due Date", "Status"])

        try:
            df.to_excel(filepath, index=False, engine='openpyxl')
            messagebox.showinfo("Success", f"Tasks exported to {filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {e}")

class KpiView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill="both", expand=True)
        self.figure = None
        self.canvas = None
        self.ax = None
        self.create_widgets()

    def create_widgets(self):
        # Top half: Dynamic Combo Chart
        self.chart_frame = ctk.CTkFrame(self)
        self.chart_frame.pack(fill="x", padx=10, pady=10)

        # Build axes
        plt.style.use('dark_background')
        self.figure, self.ax = plt.subplots(figsize=(8, 3), dpi=100)
        self.figure.patch.set_facecolor('#2b2b2b')
        self.ax.set_facecolor('#2b2b2b')

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Bottom half: KPI Checkbox Grid
        self.grid_frame = ctk.CTkScrollableFrame(self)
        self.grid_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Action Buttons
        self.actions_frame = ctk.CTkFrame(self.grid_frame, fg_color="transparent")
        self.actions_frame.pack(fill="x", pady=(0, 10))

        self.btn_export = ctk.CTkButton(self.actions_frame, text="Export to Excel", command=self.export_to_excel)
        self.btn_export.pack(side="right", padx=5)

        self.checkboxes = {} # To store reference to stringvars

        self.build_kpi_grid()
        self.draw_chart()

    def build_kpi_grid(self):
        # Clear existing
        for widget in self.grid_frame.winfo_children():
            if widget != self.actions_frame:
                widget.destroy()

        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        db_cols = ["mon", "tue", "wed", "thu", "fri", "sat"]

        # Headers
        header_frame = ctk.CTkFrame(self.grid_frame)
        header_frame.pack(fill="x", pady=2)

        ctk.CTkLabel(header_frame, text="Task Name", width=200, anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        for day in days:
            ctk.CTkLabel(header_frame, text=day, width=60, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)

        kpi_data = database.get_kpi_tasks()

        for kpi in kpi_data:
            task_id = kpi[0]
            task_name = kpi[1]
            vals = kpi[2:8]

            row_frame = ctk.CTkFrame(self.grid_frame)
            row_frame.pack(fill="x", pady=2)

            ctk.CTkLabel(row_frame, text=task_name, width=200, anchor="w").pack(side="left", padx=5)

            self.checkboxes[task_id] = {}
            for i, val in enumerate(vals):
                var = ctk.IntVar(value=val)
                col_name = db_cols[i]

                # We need to capture the current state of variables in the lambda
                def make_toggle(tid, cname, v):
                    def toggle_kpi():
                        database.update_kpi_task(tid, cname, v.get())
                        self.draw_chart()
                    return toggle_kpi

                cb = ctk.CTkCheckBox(row_frame, text="", variable=var, width=60, command=make_toggle(task_id, col_name, var))
                cb.pack(side="left", padx=5)
                self.checkboxes[task_id][col_name] = var

    def draw_chart(self):
        kpi_data = database.get_kpi_tasks()
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

        # Draw Bars
        bars = self.ax.bar(days, percentages, color='#1f538d')

        # Target line
        self.ax.axhline(y=75, color='red', linestyle='--', linewidth=2, label='Target 75%')

        self.ax.set_ylim(0, 100)
        self.ax.set_ylabel('Completion %')
        self.ax.set_title('Daily KPI Completion')
        self.ax.legend(loc="upper right")

        self.figure.tight_layout()
        self.canvas.draw()

    def export_to_excel(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")],
            title="Export KPIs to Excel"
        )
        if not filepath:
            return

        kpis = database.get_kpi_tasks()
        df = pd.DataFrame(kpis, columns=["ID", "Task Name", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"])

        try:
            df.to_excel(filepath, index=False, engine='openpyxl')
            messagebox.showinfo("Success", f"KPIs exported to {filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {e}")
