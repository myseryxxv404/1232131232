import tkinter as tk
from tkinter import messagebox, ttk
import random
import json
import os

# --- Основной класс приложения ---
class TaskGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор случайных задач")
        self.root.geometry("500x550")
        self.root.resizable(False, False)

        # 1. Список предопределённых задач
        self.tasks = [
            {"name": "Прочитать статью", "type": "учёба"},
            {"name": "Сделать зарядку", "type": "спорт"},
            {"name": "Написать отчёт", "type": "работа"},
            {"name": "Посмотреть обучающее видео", "type": "учёба"},
            {"name": "Погулять на свежем воздухе", "type": "спорт"},
            {"name": "Разобрать почту", "type": "работа"},
            {"name": "Выучить 10 новых слов", "type": "учёба"},
        ]

        # История сгенерированных задач (загружается из файла при старте)
        self.history = []
        self.load_history()

        # --- Создание интерфейса ---
        # Рамка для текущей задачи
        task_frame = tk.LabelFrame(root, text="Текущая задача", padx=10, pady=10)
        task_frame.pack(pady=10, fill="x")

        self.task_label = tk.Label(
            task_frame, text="Нажмите кнопку, чтобы получить задачу", 
            font=("Arial", 12), wraplength=400, justify="center"
        )
        self.task_label.pack()

        # Кнопка генерации
        self.generate_btn = tk.Button(
            root, text="Сгенерировать задачу", font=("Arial", 12), 
            bg="#4CAF50", fg="white", command=self.generate_task
        )
        self.generate_btn.pack(pady=10)

        # Рамка для истории и фильтра
        history_frame = tk.LabelFrame(root, text="История задач", padx=10, pady=10)
        history_frame.pack(pady=10, fill="both", expand=True)

        # Фильтр по типу задачи
        filter_frame = tk.Frame(history_frame)
        filter_frame.pack(pady=5, fill="x")
        
        tk.Label(filter_frame, text="Фильтр по типу:").pack(side="left")
        
        self.filter_var = tk.StringVar(value="все")
        filter_options = ["все"] + sorted(list({task["type"] for task in self.tasks}))
        
        self.filter_menu = ttk.OptionMenu(
            filter_frame, self.filter_var, "все", *filter_options, 
            command=self.apply_filter
        )
        self.filter_menu.pack(side="left", padx=5)

        # Список истории (с прокруткой)
        self.history_scroll = tk.Scrollbar(history_frame)
        self.history_scroll.pack(side="right", fill="y")

        self.history_listbox = tk.Listbox(
            history_frame, yscrollcommand=self.history_scroll.set, 
            font=("Arial", 10), height=12
        )
        self.history_listbox.pack(side="left", fill="both", expand=True)
        
        self.history_scroll.config(command=self.history_listbox.yview)

        # Кнопки управления историей
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)
        
        tk.Button(btn_frame, text="Сохранить историю", 
                  command=self.save_history).pack(side="left", padx=5)
        
        tk.Button(btn_frame, text="Очистить историю", 
                  command=self.clear_history).pack(side="left", padx=5)
        
    # 2. Генерация случайной задачи
    def generate_task(self):
        if not self.tasks:
            messagebox.showwarning("Предупреждение", "Список задач пуст. Добавьте задачи вручную.")
            return

        task = random.choice(self.tasks)
        
        # Добавляем в историю (если такой ещё нет в текущей сессии, можно убрать if для дублей)
        self.history.append(task)
        
        # Обновляем отображение истории и текущей задачи
        self.update_history_display()
        
        task_text = f"Задача: {task['name']} ({task['type'].capitalize()})"
        
        if len(task_text) > 80: # Если текст слишком длинный, обрезаем и добавляем ...
            task_text = task_text[:77] + "..."
            
        self.task_label.config(text=task_text)

    # 3. Отображение истории с учётом фильтра
    def update_history_display(self):
         # Очищаем список
         self.history_listbox.delete(0, tk.END)
         
         current_filter = self.filter_var.get()
         
         for task in reversed(self.history): # Показываем последние сверху
             if current_filter == "все" or task["type"] == current_filter:
                 entry = f"{task['name']} ({task['type']})"
                 self.history_listbox.insert(tk.END, entry)

    # 4. Применение фильтра
    def apply_filter(self, value):
         self.update_history_display()

    # 6. Проверка корректности ввода (добавление новой задачи)
    def add_custom_task_window(self):
         add_window = tk.Toplevel(self.root)
         add_window.title("Добавить новую задачу")
         add_window.geometry("300x150")
         
         tk.Label(add_window, text="Название задачи:").pack(pady=5)
         name_entry = tk.Entry(add_window)
         name_entry.pack(pady=5)
         
         type_var = tk.StringVar(value="разное")
         tk.Label(add_window, text="Тип задачи:").pack(pady=5)
         ttk.OptionMenu(add_window, type_var, "разное", *["разное","учёба","спорт","работа"]).pack(pady=5)
         
         def on_add():
             name = name_entry.get().strip()
             task_type = type_var.get()
             
             if not name:
                 messagebox.showerror("Ошибка", "Название задачи не может быть пустым!")
                 return
             
             self.tasks.append({"name": name, "type": task_type})
             messagebox.showinfo("Успех", f"Задача '{name}' добавлена в список.")
             add_window.destroy()
             
         tk.Button(add_window, text="Добавить задачу", command=on_add).pack(pady=10)

    # 5. Сохранение истории в JSON
    def save_history(self):
         if not self.history:
             messagebox.showinfo("Информация", "История пуста. Нечего сохранять.")
             return

         try:
             with open("history.json", "w", encoding="utf-8") as f:
                 json.dump(self.history, f, ensure_ascii=False, indent=4)
             messagebox.showinfo("Успех", "История успешно сохранена в файл 'history.json'")
         except Exception as e:
             messagebox.showerror("Ошибка сохранения", str(e))

    # Загрузка истории из JSON при старте
    def load_history(self):
         try:
             if os.path.exists("history.json"):
                 with open("history.json", "r", encoding="utf-8") as f:
                     self.history = json.load(f)
                 messagebox.showinfo("Загрузка", "История успешно загружена.")
         except Exception as e:
             messagebox.showerror("Ошибка загрузки", str(e))
             self.history = []

    # Очистка истории (в памяти и в файле)
    def clear_history(self):
         if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить всю историю?"):
             self.history = []
             self.update_history_display()
             
             try:
                 if os.path.exists("history.json"):
                     os.remove("history.json")
                     messagebox.showinfo("Очистка", "История очищена и файл удалён.")
             except Exception as e:
                 messagebox.showerror("Ошибка очистки файла", str(e))
                 
# --- Запуск приложения ---
if __name__ == "__main__":
    root = tk.Tk()
    app = TaskGeneratorApp(root)
    
    # Добавляем меню для добавления задач (пункт в меню)
    menubar = tk.Menu(root)
    filemenu = tk.Menu(menubar, tearoff=0)
    filemenu.add_command(label="Добавить новую задачу...", command=app.add_custom_task_window)
    filemenu.add_separator()
    filemenu.add_command(label="Выход", command=root.quit)
    menubar.add_cascade(label="Задачи", menu=filemenu)
    
    root.config(menu=menubar)
    root.mainloop()