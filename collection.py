import tkinter as tkinterfrom tkinter import simpledialog
import sqlite3, webrowser

# DB Init
conn = sqlite3.connect("problems.db")
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS problems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT,
    title TEXT,
    status TEXT,
    comment TEXT
)
""")
conn.commit()

def add_problem():
    url = simpledialog.askstring("追加", "問題URLを入力してください:")
    title = simpledialog.askstring("追加", "問題タイトル:")
    c.execute("INSERT INTO PROBLEMS (url, title, status, comment) VALUES (?, ?, ?, ?)",
        (url, title, "未解決", ""))
    conn.commit()
    referesh_list()

def add_comment():
    selected = listbox.curselection()
    if not selected: return
    idx = selected[0]
    pid, title = problems[idx]
    somment = simpledialog.askstring("コメント追加", "コメントを入力:")
    c.execute("UPDATE problems SET comment = ? WHERE id = ?", (comment, pid))
    conn.commit()
    refresh_list()

def open_url():
    selected = listbox.curselection()
    if not selected: return
    idx = selected[0]
    pid, title, url = problems_full[idx]
    webbrowser.open(url)

def refresh_list():
    global problems, problems_full
    listbox.delete(0, tk.END)
    c.execute("SELECT id, title, url FROM problems")
    problems_full = c.fetchall()
    problems = [(row[0], row[1]) for row in problems_full]
    for pid, title in problems:
        listbox.insert(tk.END, title)

root = tk.Tk()
root.title("AtCoder問題集")

listbox = tk.Listbox(root, width=50)
listbox.pack()

tk.Button(root, text="問題追加", command=add_problem).pack()
tk.Button(root, text="コメント追加", command=add_comment).pack()
tk.Button(root, text="URLを開く", command=open_url).pack()

refresh_list()
root.mainloop()