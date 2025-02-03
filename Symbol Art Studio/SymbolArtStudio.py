import tkinter as tk
from tkinter import colorchooser, messagebox, filedialog, ttk

class PaintApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SymbolArtStudio")

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}")

        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.current_symbol = '*'
        self.symbols = {
            'Базові': ['*', '#', '@', '+', '.', 'o', '■', '□', '●', '○', '▲', '▼', '♦', '♥', '♠', '♣'],
            'Латиниця (великі)': list('ABCDEFGHIJKLMNOPQRSTUVWXYZ'),
            'Латиниця (малі)': list('abcdefghijklmnopqrstuvwxyz'),
            'Кирилиця (великі)': list('АБВГДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯ'),
            'Кирилиця (малі)': list('абвгдеєжзиіїйклмнопрстуфхцчшщьюя'),
            'Цифри': list('0123456789'),
            'Валюти': ['$', '€', '£', '¥', '₴', '₿', '₴']
        }
        self.current_color = 'black'
        self.drawing = False
        self.canvas_width = 100
        self.canvas_height = 40
        self.eraser_mode = False

        self.history = []
        self.history_position = -1

        self.setup_gui()
        self.save_state()

    def setup_gui(self):
        # Налаштування меню
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Новий", command=self.clear_canvas)
        file_menu.add_command(label="Відкрити", command=self.load_drawing)
        file_menu.add_command(label="Зберегти", command=self.save_drawing)
        file_menu.add_separator()
        file_menu.add_command(label="Вийти", command=self.root.quit)

        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Редагування", menu=edit_menu)
        edit_menu.add_command(label="Відмінити", command=self.undo)
        edit_menu.add_command(label="Повторити", command=self.redo)

        canvas_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Полотно", menu=canvas_menu)
        canvas_menu.add_command(label="Змінити розмір", command=self.change_canvas_size)

        # Панель інструментів
        toolbar = tk.Frame(self.root)
        toolbar.grid(row=0, column=0, sticky='ew', padx=5, pady=5)

        self.symbol_button = tk.Menubutton(toolbar, text="Символ: " + self.current_symbol, relief=tk.RAISED)
        self.symbol_button.pack(side=tk.LEFT, padx=2)

        self.symbol_menu = tk.Menu(self.symbol_button, tearoff=0)
        self.symbol_button.configure(menu=self.symbol_menu)

        for category, symbols in self.symbols.items():
            submenu = tk.Menu(self.symbol_menu, tearoff=0)
            self.symbol_menu.add_cascade(label=category, menu=submenu)
            for symbol in symbols:
                submenu.add_command(label=symbol, command=lambda s=symbol: self.change_symbol(s))

        self.color_btn = tk.Button(toolbar, text="Колір", command=self.choose_color,
                                   bg=self.current_color, fg='white' if self.current_color == 'black' else 'black')
        self.color_btn.pack(side=tk.LEFT, padx=5)

        # Додаємо кнопку ластика
        self.eraser_btn = tk.Button(toolbar, text="Ластик", command=self.toggle_eraser)
        self.eraser_btn.pack(side=tk.LEFT, padx=5)

        # Frame для обмеження розміру текстового віджета
        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        self.canvas_frame.grid_propagate(False)

        # Додаємо скролбари
        self.v_scrollbar = tk.Scrollbar(self.canvas_frame, orient='vertical')
        self.h_scrollbar = tk.Scrollbar(self.canvas_frame, orient='horizontal')
        self.v_scrollbar.pack(side='right', fill='y')
        self.h_scrollbar.pack(side='bottom', fill='x')

        # Текстовий віджет
        self.text_widget = tk.Text(self.canvas_frame,
                                   wrap=tk.NONE,
                                   font=('Courier New', 12),
                                   selectbackground='white',
                                   selectforeground='black',
                                   inactiveselectbackground='white',
                                   width=self.canvas_width + 2,  # +2 для границь
                                   height=self.canvas_height + 2,  # +2 для границь
                                   yscrollcommand=self.v_scrollbar.set,
                                   xscrollcommand=self.h_scrollbar.set)

        self.text_widget.pack(side='left', fill='both', expand=True)

        # Налаштування скролбарів
        self.v_scrollbar.config(command=self.text_widget.yview)
        self.h_scrollbar.config(command=self.text_widget.xview)

        self.text_widget.configure(state='disabled')

        self.text_widget.bind('<Button-1>', self.start_drawing)
        self.text_widget.bind('<B1-Motion>', self.draw)
        self.text_widget.bind('<ButtonRelease-1>', self.stop_drawing)

        self.update_frame_size()
        self.clear_canvas()

    def toggle_eraser(self):
        self.eraser_mode = not self.eraser_mode
        self.eraser_btn.configure(relief=tk.SUNKEN if self.eraser_mode else tk.RAISED)

    def draw_borders(self):
        self.text_widget.config(state='normal')
        # Верхня границя
        self.text_widget.delete("1.0", "1.end")
        self.text_widget.insert("1.0", '┌' + '─' * self.canvas_width + '┐\n')

        # Бокові границі
        for i in range(self.canvas_height):
            line_num = i + 2
            self.text_widget.delete(f"{line_num}.0")
            self.text_widget.insert(f"{line_num}.0", '│')
            self.text_widget.delete(f"{line_num}.{self.canvas_width + 1}")
            self.text_widget.insert(f"{line_num}.{self.canvas_width + 1}", '│\n')

        # Нижня границя
        last_line = self.canvas_height + 2
        self.text_widget.delete(f"{last_line}.0", f"{last_line}.end")
        self.text_widget.insert(f"{last_line}.0", '└' + '─' * self.canvas_width + '┘\n')

        self.text_widget.config(state='disabled')

    def clear_canvas(self):
        self.text_widget.config(state='normal')
        self.text_widget.delete(1.0, tk.END)

        # Додаємо верхню границю
        self.text_widget.insert(tk.END, '┌' + '─' * self.canvas_width + '┐\n')

        # Додаємо основне полотно з боковими границями
        for _ in range(self.canvas_height):
            self.text_widget.insert(tk.END, '│' + ' ' * self.canvas_width + '│\n')

        # Додаємо нижню границю
        self.text_widget.insert(tk.END, '└' + '─' * self.canvas_width + '┘\n')

        self.text_widget.config(state='disabled')
        self.save_state()

    def start_drawing(self, event):
        self.drawing = True
        self.draw(event)

    def draw(self, event):
        if not self.drawing:
            return

        index = self.text_widget.index(f"@{event.x},{event.y}")
        line, col = map(int, index.split('.'))

        # Перевіряємо чи знаходимося в межах полотна (враховуючи границі)
        if 1 < line < self.canvas_height + 2 and 0 < col < self.canvas_width + 1:
            self.text_widget.config(state='normal')
            self.text_widget.delete(f"{line}.{col}")

            if self.eraser_mode:
                self.text_widget.insert(f"{line}.{col}", ' ')
                # Видаляємо тег кольору якщо він є
                for tag in self.text_widget.tag_names(f"{line}.{col}"):
                    if tag.startswith("color_"):
                        self.text_widget.tag_remove(tag, f"{line}.{col}")
            else:
                self.text_widget.insert(f"{line}.{col}", self.current_symbol)
                tag_name = f"color_{line}_{col}"
                self.text_widget.tag_add(tag_name, f"{line}.{col}")
                self.text_widget.tag_config(tag_name, foreground=self.current_color)

            self.text_widget.config(state='disabled')

    def stop_drawing(self, event):
        if self.drawing:
            self.drawing = False
            self.save_state()

    def change_symbol(self, symbol):
        self.current_symbol = symbol
        self.symbol_button.configure(text="Символ: " + symbol)

    def choose_color(self):
        color = colorchooser.askcolor(color=self.current_color)[1]
        if color:
            self.current_color = color
            self.color_btn.configure(bg=color, fg='white' if color == 'black' else 'black')

    def update_frame_size(self):
        char_width = self.text_widget.winfo_reqwidth() // (self.canvas_width + 2)
        char_height = self.text_widget.winfo_reqheight() // (self.canvas_height + 2)
        frame_width = (char_width * (self.canvas_width + 2)) + self.v_scrollbar.winfo_reqwidth() + 10
        frame_height = (char_height * (self.canvas_height + 2)) + self.h_scrollbar.winfo_reqheight() + 10
        self.canvas_frame.configure(width=frame_width, height=frame_height)

    def change_canvas_size(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Змінити розмір полотна")

        tk.Label(dialog, text="Ширина:").grid(row=0, column=0, padx=5, pady=5)
        width_entry = tk.Entry(dialog)
        width_entry.insert(0, str(self.canvas_width))
        width_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(dialog, text="Висота:").grid(row=1, column=0, padx=5, pady=5)
        height_entry = tk.Entry(dialog)
        height_entry.insert(0, str(self.canvas_height))
        height_entry.grid(row=1, column=1, padx=5, pady=5)

        def apply():
            try:
                new_width = int(width_entry.get())
                new_height = int(height_entry.get())
                if new_width > 0 and new_height > 0:
                    self.canvas_width = new_width
                    self.canvas_height = new_height
                    self.text_widget.configure(width=new_width + 2, height=new_height + 2)
                    self.update_frame_size()
                    self.clear_canvas()
                    dialog.destroy()
                else:
                    messagebox.showerror("Помилка", "Розміри повинні бути більше 0")
            except ValueError:
                messagebox.showerror("Помилка", "Введіть коректні числові значення")

        tk.Button(dialog, text="Застосувати", command=apply).grid(row=2, column=0, columnspan=2, pady=10)

    def save_drawing(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text files", "*.txt"),
                                                            ("All files", "*.*")])
        if file_path:
            content = self.text_widget.get(1.0, tk.END)
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)

    def load_drawing(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"),
                                                          ("All files", "*.*")])
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                self.text_widget.config(state='normal')
                self.text_widget.delete(1.0, tk.END)
                self.text_widget.insert(1.0, content)
                self.text_widget.config(state='disabled')
                self.draw_borders()  # Відновлюємо границі після завантаження
            self.save_state()

    def save_state(self):
        content = self.text_widget.get(1.0, tk.END)
        self.history = self.history[:self.history_position + 1]
        self.history.append(content)
        self.history_position = len(self.history) - 1

    def undo(self):
            if self.history_position > 0:
                self.history_position -= 1
                content = self.history[self.history_position]
                self.text_widget.config(state='normal')
                self.text_widget.delete(1.0, tk.END)
                self.text_widget.insert(1.0, content)
                self.text_widget.config(state='disabled')

    def redo(self):
            if self.history_position < len(self.history) - 1:
                self.history_position += 1
                content = self.history[self.history_position]
                self.text_widget.config(state='normal')
                self.text_widget.delete(1.0, tk.END)
                self.text_widget.insert(1.0, content)
                self.text_widget.config(state='disabled')

def main():  # <- це правильно (без відступу)
    root = tk.Tk()
    app = PaintApp(root)
    root.mainloop()

if __name__ == "__main__":  # <- це правильно (без відступу)
    main()
