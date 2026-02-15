import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
import os

# ---------------- DATABASE SETUP ----------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "bmi_records.db")

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        weight REAL,
        height REAL,
        bmi REAL,
        category TEXT,
        date TEXT
    )
    """)
    conn.commit()
except sqlite3.OperationalError as e:
    messagebox.showerror("Database Error", f"Could not open database: {e}\nTry moving the folder out of OneDrive.")

# ---------------- VARIABLE DECLARATIONS ----------------

name_entry: tk.Entry
weight_entry: tk.Entry
height_entry: tk.Entry

# ---------------- BMI LOGIC ----------------

def get_category(bmi):
    if bmi < 18.5: return "Underweight"
    elif bmi < 25: return "Normal"
    elif bmi < 30: return "Overweight"
    else: return "Obese"

def calculate_bmi():
    try:
        name = name_entry.get().strip()
        weight = float(weight_entry.get())
        height_cm = float(height_entry.get())

        if not name:
            messagebox.showerror("Input Error", "Please enter name")
            return

        if not (1 <= weight <= 300) or not (50 <= height_cm <= 250):
            messagebox.showerror("Input Error", "Please enter realistic height/weight values.")
            return

        height_m = height_cm / 100
        bmi = round(weight / (height_m ** 2), 2)
        category = get_category(bmi)

        result_var.set(f"BMI: {bmi} | Category: {category}")

        cursor.execute("""
        INSERT INTO records (name, weight, height, bmi, category, date)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (name, weight, height_cm, bmi, category, datetime.now().strftime("%Y-%m-%d %H:%M")))
        conn.commit()
        messagebox.showinfo("Saved", f"Record for {name} stored successfully!")

    except ValueError:
        messagebox.showerror("Input Error", "Enter valid numeric values")

# ---------------- HISTORY VIEW ----------------

def show_history():
    name = name_entry.get().strip()
    if not name:
        messagebox.showerror("Error", "Enter name first to see history")
        return

    cursor.execute("SELECT weight, height, bmi, category, date FROM records WHERE name=?", (name,))
    rows = cursor.fetchall()

    if not rows:
        messagebox.showinfo("No Data", "No records found for this name.")
        return

    history_win = tk.Toplevel(root)
    history_win.title(f"History: {name}")
    history_win.geometry("500x300")

    tree = ttk.Treeview(history_win, columns=("W", "H", "BMI", "Cat", "Date"), show="headings")
    tree.pack(fill="both", expand=True)

    for col, head in zip(tree["columns"], ["Weight", "Height", "BMI", "Category", "Date"]):
        tree.heading(col, text=head)
        tree.column(col, width=80)

    for r in rows:
        tree.insert("", "end", values=r)

# ---------------- GRAPH ----------------

def show_graph():
    name = name_entry.get().strip()
    if not name:
        messagebox.showerror("Error", "Enter name first")
        return

    cursor.execute("SELECT bmi, date FROM records WHERE name=? ORDER BY id", (name,))
    rows = cursor.fetchall()

    if len(rows) < 2:
        messagebox.showinfo("Trend", "Need at least 2 records to plot a trend.")
        return

    bmi_vals = [r[0] for r in rows]
    # Shorten date for better display on X-axis
    dates = [r[1].split(" ")[0] for r in rows] 

    plt.figure(figsize=(8, 5))
    plt.plot(dates, bmi_vals, marker="o", linestyle="-", color="b")
    plt.title(f"BMI Progress for {name}")
    plt.xlabel("Date")
    plt.ylabel("BMI Value")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# ---------------- GUI ----------------

root = tk.Tk()
root.title(" BMI Tracker") # Personal touch for you, Ishu!
root.geometry("420x400")

tk.Label(root, text="Smart BMI Tracker", font=("Arial", 16, "bold")).pack(pady=10)

# Entry Fields
fields = [("Name", "name_entry"), ("Weight (kg)", "weight_entry"), ("Height (cm)", "height_entry")]
for label_text, var_name in fields:
    tk.Label(root, text=label_text).pack()
    entry = tk.Entry(root)
    entry.pack(pady=2)
    globals()[var_name] = entry

result_var = tk.StringVar(value="Enter details and calculate")
tk.Label(root, textvariable=result_var, font=("Arial", 11, "italic"), fg="darkblue").pack(pady=15)

# Buttons
btn_style = {"width": 25, "pady": 5}
tk.Button(root, text="Calculate & Save BMI", command=calculate_bmi, bg="#e1f5fe", **btn_style).pack(pady=2)
tk.Button(root, text="View History Table", command=show_history, **btn_style).pack(pady=2)
tk.Button(root, text="Show Progress Graph", command=show_graph, **btn_style).pack(pady=2)

tk.Label(root, text="Tip: Track weekly for better accuracy", fg="gray", font=("Arial", 8)).pack(side="bottom", pady=10)

def on_closing():
    conn.close()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
