import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import sqlite3, webbrowser

# ======== Database Init ==============
conn = sqlite3.connect("ac_problem.db")
c = conn.cursor()

# Problem Table
c.execute("""
CREATE TABLE IF NOT EXISTS problems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    url TEXT,
    status TEXT
)
""")

# Code Table
c.execute("""
CREATE TABLE IF NOT EXISTS codes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    problem_id INTEGER,
    code TEXT,
    comment TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()

# ======== Functions =======

def refresh_problems():
    """Renew problem list"""
    listbox.delete(0, tk.END)
    c.execute("SELECT id, title, status FROM problems ORDER BY id DESC")
    global problems
    problems = c.fetchall()
    for pid, title, status in problems:
        listbox.insert(tk.END, f"{title} [{status}]")

def add_problem():
    """Add a new problem"""
    title = simpledialog.askstring("問題追加", "問題タイトル:")
    if not title: return
    url = simpledialog.askstring("URL", "問題URL:")
    status = simpledialog.askstring("ステータス", "自力 / AI / できなかった:")
    if status not in ["自力", "AI", "できなかった"]:
        status = "未分類"
    c.execute("INSERT INTO problems (title, url, status) VALUES (?, ?, ?)",
              (title, url, status))
    conn.commit()
    refresh_problems()
    
def open_url():
    """Open the chosen problem on a browser"""
    sel = listbox.curselection()
    if not sel: return
    pid, _, _ = problem[sel[0]]
    c.execute("SELECT url FROM problems WHERE id = ?", (pid,))
    url = c.fetchone()[0]
    if url:
        webbrowser.open(url)
    else:
        messagebox.shoinfo("URLなし", "URLが登録されていません。")

def show_problem_detail(event=None):
    """Display details on right paine"""
    sel = listbox.curselection()
    if not sel: return
    pid, title, status = problems[sel[0]]
    detail_title.config(text=f"{title} [{status}]")
    
    # Display commit log
    for w in code_frame.winfo_children():
        w.destroy()
    c.execute("SELECT code, comment, timestamp FROM codes WHERE problem_id = ? ORDER BY id ASC", (pid,))
    codes = c.fetchall()
    if not codes:
        tk.Label(code_frame, text="まだコードがありません", fg="gray").pack()
    else:
        for code, comment, ts in codes:
            box = tk.Frame(code_frame, bd=1, relief="groove", padx=4, pady=4)
            box.pack(fill="x", pady=3)
            tk.Label(box, text=f"{ts}", fg="gray").pack(anchor="w")
            tk.Label(box, text=f"コメント: {comment}", fg="blue").pack(anchor="w")
            code_text= tk.Text(box, height=5, width=50)
            code_text.insert("1.0", code)
            code_text.config(state="disabled")
            code_text.pack()

def add_code():
    """Add codes and comments on a selected problem"""
    sel = listbox.curselection()
    if not sel: return
    pid, _, _ = problem[sel[0]]
    code = simpledialog.askstring("コード追加", "コード内容を貼り付けてください:")
    if not code: return
    comment = simpledialog.askstring("コメント", "このコードに対するメモ:")
    c.execute("INSERT INTO codes (problem_id, code, comment) VALUES (?, ?, ?)",
              (pid, code, comment))
    conn.commit()
    show_problem_detail()

# ======== UI =========
root = tk.Tk()
root.title("AtCoder 問題記録帳")
root.geometry("800x500")

# Left: Problem List
left_frame = tk.Frame(root)
left_frame.pack(side="left", fill="y", padx=10, pady=10)

listbox = tk.Listbox(left_frame, width=40, height=25)
listbox.pack()
listbox.bind("<<ListboxSelect>>", show_problem_detail)

tk.Button(left_frame, text="問題追加", command=add_problem).pack(fill="x", pady=3)
tk.Button(left_frame, text="URLを開く", command=open_url).pack(fill="x", pady=3)
tk.Button(left_frame, text="コード追加", command=add_code).pack(fill="x", pady=3)

# Right: detail view
right_frame = tk.Frame(root)
right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

detail_title = tk.Label(right_frame, text=" (問題を選択してください) ", font=("Meiryo", 14))
detail_title.pack(anchor="w")

canvas = tk.Canvas(right_frame)
scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=canvas.yview)
code_frame = tk.Frame(canvas)

code_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=code_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pac(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

refresh_problems()
root.mainloop()