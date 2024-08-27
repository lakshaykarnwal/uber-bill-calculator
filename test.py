import tkinter as tk

root = tk.Tk()
root.title("Test Window")
root.geometry("300x200")
root.configure(bg='white')

tk.Label(root, text="Hello, Tkinter!", bg='white', fg='black').pack(pady=20)
tk.Entry(root, bg='white', fg='black').pack(pady=20)

root.mainloop()
