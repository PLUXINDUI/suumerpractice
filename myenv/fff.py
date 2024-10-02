import tkinter as tk
from tkinter import ttk
import nltk
from collections import Counter
import language_tool_python
import requests
import webbrowser

# Инициализация библиотеки nltk
nltk.download('punkt')

# Инициализация инструмента проверки орфографии и пунктуации
tool = language_tool_python.LanguageTool('ru')

# Переменная для информации
info_text = """Эта программа предназначена для проверки текста на орфографические ошибки, а также для выявления плагиата путем поиска совпадений текста в Википедии. 

Здесь будет предоставлено руководство по некоторым функцииям, которые смогут улучшить пользовательский опыт от приложения.

- Для того, чтобы вставить заранее заготовленный текст, нужно переключить раскладку на английский язык и нажать сочетание клавиш ctrl+v.
- Ошибки в тексте можно исправить просто кликнув на любой из предложенных вариантов исправления, ошибка автоматически замениться на правильный вариант.
- При использовании функции проверки на плагиат, Вы можете перейти на страницу Википедии, где было найдено совпадение, просто кликнув на ссылку.
"""

def handle_focus(event, area, default_text, color_on_focus='white', color_on_focus_out='gray'):
    if area.get("1.0", "end-1c") == default_text and event.type == tk.EventType.FocusIn:
        area.delete("1.0", "end")
        area.config(fg=color_on_focus)
    elif not area.get("1.0", "end-1c") and event.type == tk.EventType.FocusOut:
        area.insert("1.0", default_text)
        area.config(fg=color_on_focus_out)

def handle_key(event, area, default_text, color_on_focus='white'):
    if area.get("1.0", "end-1c") == default_text:
        area.delete("1.0", "end")
        area.config(fg=color_on_focus)

# Функция замены текста
def replace_text(start, end, replacement):
    text_area.delete(start, end)
    text_area.insert(start, replacement)

# Функция проверки текста
def check_text():
    text = text_area.get("1.0", tk.END).strip()
    result_area.config(state=tk.NORMAL)  # Включить редактирование
    result_area.delete("1.0", tk.END)
    
    # Очистка предыдущих выделений
    text_area.tag_remove("highlight", "1.0", tk.END)
    
    # Проверка орфографии и пунктуации
    matches = tool.check(text)
    if matches:
        result_area.insert(tk.END, "Орфографические ошибки:\n\n")
        for match in matches:
            start_index = f"1.0+{match.offset}c"
            end_index = f"1.0+{match.offset + match.errorLength}c"
            text_area.tag_add("highlight", start_index, end_index)
            result_area.insert(tk.END, f"{match.message}\nВарианты исправления: ")
            for i, replacement in enumerate(match.replacements):
                btn = tk.Button(result_area, text=replacement, command=lambda s=start_index, e=end_index, r=replacement:  
                                replace_text(s, e, r), relief="flat", bg=result_area.cget("bg"), fg="white", font=("Helvetica", 12), borderwidth=0)
                btn.configure(cursor="hand2")
                result_area.window_create(tk.END, window=btn)
                if i < len(match.replacements) - 1:
                    result_area.insert(tk.END, ", ")
            result_area.insert(tk.END, "\n\n")
    else:
        result_area.insert(tk.END, "Ошибок не найдено\n")
    result_area.config(state=tk.DISABLED)  # Запретить редактирование

# Нахождение часто повторяемых слов
def find_common_words():
    text = text_area.get("1.0", tk.END).strip()
    words = nltk.word_tokenize(text)
    words = [word.lower() for word in words if word.isalnum()]
    word_counts = Counter(words)
    
    common_words = {word: count for word, count in word_counts.items() if count >= 4}
    
    common_words_area.delete("1.0", tk.END)
    if common_words:
        for word, count in common_words.items():
            common_words_area.insert(tk.END, f"{word} - {count}\n")
    else:
        common_words_area.insert(tk.END, "Нет часто повтояремых слов (4 и более раз).\n")

def show_common_words():
    main_frame.pack_forget()
    common_words_frame.pack(fill=tk.BOTH, expand=True)
    find_common_words()

def show_plagiarism():
    main_frame.pack_forget()
    plagiarism_frame.pack(fill=tk.BOTH, expand=True)
    plagiarism_result_area.delete("1.0", tk.END)
    plagiarism_result_area.insert("1.0", text_area.get("1.0", tk.END))

def show_main_frame():
    common_words_frame.pack_forget()
    plagiarism_frame.pack_forget()
    info_frame.pack_forget()
    main_frame.pack(fill=tk.BOTH, expand=True)

def clear_text_areas():
    text_area.delete("1.0", tk.END)
    text_area.insert("1.0", "Введите свой текст...")
    text_area.config(fg='gray')
    result_area.config(state=tk.NORMAL)
    result_area.delete("1.0", tk.END)
    result_area.insert("1.0", "Здесь будут показаны варианты исправления ошибок...")
    result_area.config(fg='gray', state=tk.DISABLED)
    plagiarism_result_area.config(state=tk.NORMAL)
    plagiarism_result_area.delete("1.0", tk.END)
    plagiarism_result_area.config(state=tk.DISABLED)

def copy_text():
    root.clipboard_clear()
    root.clipboard_append(text_area.get("1.0", tk.END))

def paste_text(event=None):
    try:
        text = root.clipboard_get()
        text_area.insert(tk.INSERT, text)
    except tk.TclError:
        pass
    return 'break'

def check_plagiarism():
    text = text_area.get("1.0", tk.END).strip()
    plagiarism_result_area.config(state=tk.NORMAL)  # Включить редактирование
    plagiarism_result_area.delete("1.0", tk.END)
    plagiarism_result_area.insert(tk.END, "Проверка на плагиат...\n\n")
    
    # Добавление проверяемого текста
    plagiarism_result_area.insert(tk.END, text + "\n\n")
    
    # Разбиение текста на слова
    words = nltk.word_tokenize(text)
    num_words = len(words)
    
    # Проверка на плагиат с использованием API Википедии
    search_url = "https://ru.wikipedia.org/w/api.php"
    best_match = None
    best_match_length = 0
    
    for i in range(num_words - 11):
        phrase = ' '.join(words[i:i+12])
        if is_institution_or_ministry(phrase) or is_common_information(phrase):
            continue
        params = {
            "action": "query",
            "list": "search",
            "srsearch": f'"{phrase}"',
            "format": "json"
        }
        response = requests.get(search_url, params=params)
        if response.status_code == 200:
            search_results = response.json().get("query", {}).get("search", [])
            for result in search_results:
                title = result.get("title")
                snippet = result.get("snippet")
                page_url = f"https://ru.wikipedia.org/wiki/{title.replace(' ', '_')}"
                match_length = len(nltk.word_tokenize(snippet))
                if match_length > best_match_length:
                    best_match = page_url
                    best_match_length = match_length
    
    if best_match:
        plagiarism_result_area.insert(tk.END, "Найдено совпадение в Википедии:\n\n")
        link = f"{best_match}"
        plagiarism_result_area.insert(tk.END, f"{link}\n", ("link",))
        plagiarism_result_area.tag_configure("link", foreground="white", underline=True)
        plagiarism_result_area.tag_bind("link", "<Button-1>", lambda e, url=best_match: open_url(url))
    else:
        plagiarism_result_area.insert(tk.END, "Совпадений не найдено.\n")
    plagiarism_result_area.config(state=tk.NORMAL)

def is_institution_or_ministry(phrase):
    institutions_ministries = [
        "Министерство", "Университет", "Академия", "Институт", "Колледж", "Школа", "Гимназия", "Факультет"
    ]
    return any(word in phrase for word in institutions_ministries)

def is_common_information(phrase):
    common_info = ["год", "день", "месяц", "январь", "февраль", "март", "апрель", "май", "июнь", "июль", "август", "сентябрь", "октябрь", "ноябрь", "декабрь", "Россия", "Москва", "глава", "президент", "министр"]
    return any(word in phrase for word in common_info)

def open_url(url):
    webbrowser.open_new_tab(url)

def show_info():
    main_frame.pack_forget()
    info_frame.pack(fill=tk.BOTH, expand=True)
    info_text_area.config(state=tk.NORMAL)
    info_text_area.delete("1.0", tk.END)
    info_text_area.insert("1.0", info_text)
    info_text_area.config(state=tk.DISABLED)

# Создание интерфейса с помощью tkinter
root = tk.Tk()
root.title("Проверка текста")
root.geometry("800x600")
root.configure(bg='#5D3FD3')

style = ttk.Style()
style.configure("TButton", padding=6, relief="flat", background="#D3D3D3", foreground="black", font=("Helvetica", 12, "bold"), borderwidth=1)
style.map("TButton", background=[('active', '#A9A9A9')])

def create_rounded_button(master, text, command):
    return tk.Button(master, text=text, command=command, relief="flat", bg="#D3D3D3", fg="black", font=("Helvetica", 12, "bold"), highlightthickness=0, bd=0)

# Основная страница
main_frame = tk.Frame(root, bg='#5D3FD3')
main_frame.pack(fill=tk.BOTH, expand=True)

text_area = tk.Text(main_frame, wrap=tk.WORD, width=60, height=15, font=("Helvetica", 12), bg='#000000', fg='gray', insertbackground='white')
text_area.insert("1.0", "Введите свой текст...")
text_area.bind("<FocusIn>", lambda event: handle_focus(event, text_area, "Введите свой текст..."))
text_area.bind("<FocusOut>", lambda event: handle_focus(event, text_area, "Введите свой текст..."))
text_area.bind("<Key>", lambda event: handle_key(event, text_area, "Введите свой текст..."))
text_area.bind("<Control-v>", paste_text)
text_area.bind("<Control-Cyrillic_em>", paste_text)  # Ctrl+М на русской раскладке
text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

result_area = tk.Text(main_frame, wrap=tk.WORD, width=60, height=10, font=("Helvetica", 12), bg='#000000', fg='gray', insertbackground='white')
result_area.insert("1.0", "Здесь будут показаны варианты исправления ошибок...")
result_area.bind("<FocusIn>", lambda event: handle_focus(event, result_area, "Здесь будут показаны варианты исправления ошибок..."))
result_area.bind("<FocusOut>", lambda event: handle_focus(event, result_area, "Здесь будут показаны варианты исправления ошибок..."))
result_area.config(state=tk.DISABLED)  # Запретить редактирование
result_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

button_frame = tk.Frame(main_frame, bg='#5D3FD3')
button_frame.pack(pady=10)

check_button = create_rounded_button(button_frame, text="Проверить текст", command=check_text)
check_button.pack(side=tk.LEFT, padx=10)

common_words_button = create_rounded_button(button_frame, text="Часто повторяемые слова", command=show_common_words)
common_words_button.pack(side=tk.LEFT, padx=10)

plagiarism_button = create_rounded_button(button_frame, text="Проверка на плагиат", command=show_plagiarism)
plagiarism_button.pack(side=tk.LEFT, padx=10)

copy_button = create_rounded_button(button_frame, text="Копировать", command=copy_text)
copy_button.pack(side=tk.LEFT, padx=10)

clear_button = create_rounded_button(button_frame, text="Очистить", command=clear_text_areas)
clear_button.pack(side=tk.LEFT, padx=10)

info_button = create_rounded_button(button_frame, text="?", command=show_info)
info_button.pack(side=tk.LEFT, padx=10)

# Настройка выделения текста
text_area.tag_configure("highlight", background="yellow", foreground="black")

# Настройка мигающего курсора
def blink_cursor():
    if text_area.focus_get() == text_area:
        current_color = text_area.cget("insertbackground")
        new_color = "#FF00FF" if current_color == "white" else "white"
        text_area.config(insertbackground=new_color)
    root.after(500, blink_cursor)

blink_cursor()

# Страница с часто повторяемыми словами
common_words_frame = tk.Frame(root, bg='#5D3FD3')

common_words_area = tk.Text(common_words_frame, wrap=tk.WORD, width=60, height=20, font=("Helvetica", 12), bg='#000000', fg='white', insertbackground='white')
common_words_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

back_button_common = create_rounded_button(common_words_frame, text="Назад", command=show_main_frame)
back_button_common.pack(pady=10)

# Страница с проверкой на плагиат
plagiarism_frame = tk.Frame(root, bg='#5D3FD3')

plagiarism_result_area = tk.Text(plagiarism_frame, wrap=tk.WORD, width=60, height=20, font=("Helvetica", 12), bg='#000000', fg='white', insertbackground='white')
plagiarism_result_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

check_plagiarism_button = create_rounded_button(plagiarism_frame, text="Проверить на плагиат", command=check_plagiarism)
check_plagiarism_button.pack(pady=10)

back_button_plagiarism = create_rounded_button(plagiarism_frame, text="Назад", command=show_main_frame)
back_button_plagiarism.pack(pady=10)

# Страница с информацией
info_frame = tk.Frame(root, bg='#5D3FD3')

info_text_area = tk.Text(info_frame, wrap=tk.WORD, width=60, height=20, font=("Helvetica", 12), bg='#000000', fg='white', insertbackground='white')
info_text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
info_text_area.insert("1.0", info_text)
info_text_area.config(state=tk.DISABLED)

back_button_info = create_rounded_button(info_frame, text="Назад", command=show_main_frame)
back_button_info.pack(pady=10)

root.mainloop()

