import tkinter as tk
from tkinter import messagebox
import secrets
import string

# ---------- PASSWORD LOGIC ----------

def build_charset():
    chars = ""

    if lower_var.get():
        chars += string.ascii_lowercase
    if upper_var.get():
        chars += string.ascii_uppercase
    if digit_var.get():
        chars += string.digits
    if symbol_var.get():
        chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"

    # remove excluded characters
    exclude = exclude_entry.get()
    chars = "".join(c for c in chars if c not in exclude)

    return chars


def enforce_rules(password, charset):
    """Ensure at least one char from each selected type"""
    required = []

    if lower_var.get():
        required.append(secrets.choice(string.ascii_lowercase))
    if upper_var.get():
        required.append(secrets.choice(string.ascii_uppercase))
    if digit_var.get():
        required.append(secrets.choice(string.digits))
    if symbol_var.get():
        required.append(secrets.choice("!@#$%^&*"))

    # replace random positions with required chars
    pw_list = list(password)
    for r in required:
        pos = secrets.randbelow(len(pw_list))
        pw_list[pos] = r

    return "".join(pw_list)


def strength_score(pw):
    score = 0
    if len(pw) >= 12: score += 1
    if any(c.islower() for c in pw): score += 1
    if any(c.isupper() for c in pw): score += 1
    if any(c.isdigit() for c in pw): score += 1
    if any(not c.isalnum() for c in pw): score += 1

    if score <= 2:
        return "Weak"
    elif score <= 4:
        return "Medium"
    else:
        return "Strong"


def generate_password():
    try:
        length = int(length_entry.get())

        if length < 8 or length > 64:
            raise ValueError("Length must be between 8 and 64")

        if not any([lower_var.get(), upper_var.get(), digit_var.get(), symbol_var.get()]):
            raise ValueError("Select at least one character type")

        charset = build_charset()
        if not charset:
            raise ValueError("Character set became empty due to exclusions")

        pw = "".join(secrets.choice(charset) for _ in range(length))
        pw = enforce_rules(pw, charset)

        password_var.set(pw)
        strength_var.set("Strength: " + strength_score(pw))

    except Exception as e:
        messagebox.showerror("Error", str(e))


def copy_clipboard():
    pw = password_var.get()
    if not pw:
        return
    root.clipboard_clear()
    root.clipboard_append(pw)
    messagebox.showinfo("Copied", "Password copied to clipboard")


# ---------- GUI ----------

root = tk.Tk()
root.title("Secure Password Generator")
root.geometry("420x420")

tk.Label(root, text="Advanced Password Generator",
         font=("Arial", 15, "bold")).pack(pady=10)

# Length
frame_len = tk.Frame(root)
frame_len.pack()
tk.Label(frame_len, text="Password Length: ").pack(side="left")
length_entry = tk.Entry(frame_len, width=6)
length_entry.insert(0, "16")
length_entry.pack(side="left")

# Options
lower_var = tk.BooleanVar(value=True)
upper_var = tk.BooleanVar(value=True)
digit_var = tk.BooleanVar(value=True)
symbol_var = tk.BooleanVar(value=True)

tk.Checkbutton(root, text="Include lowercase", variable=lower_var).pack(anchor="w", padx=40)
tk.Checkbutton(root, text="Include uppercase", variable=upper_var).pack(anchor="w", padx=40)
tk.Checkbutton(root, text="Include digits", variable=digit_var).pack(anchor="w", padx=40)
tk.Checkbutton(root, text="Include symbols", variable=symbol_var).pack(anchor="w", padx=40)

# Exclude characters
tk.Label(root, text="Exclude characters (optional)").pack(pady=(10,0))
exclude_entry = tk.Entry(root)
exclude_entry.pack()

# Generate button
tk.Button(root, text="Generate Password",
          command=generate_password,
          height=2).pack(pady=15)

# Output
password_var = tk.StringVar()
tk.Entry(root, textvariable=password_var,
         font=("Consolas", 12),
         width=32).pack()

# Strength label
strength_var = tk.StringVar()
tk.Label(root, textvariable=strength_var,
         font=("Arial", 11, "bold")).pack(pady=5)

# Clipboard button
tk.Button(root, text="Copy to Clipboard",
          command=copy_clipboard).pack(pady=8)

# Footer tip
tk.Label(root,
         text="Tip: Use 16+ chars with all sets for strong security",
         fg="gray").pack(pady=10)

root.mainloop()
