# Импорт необходимых библиотек
import tkinter as tk  # Импортируем tkinter для создания GUI
from tkinter import ttk  # Импортируем ttk для стилизованных виджетов
import nltk  # Импортируем nltk для обработки естественного языка
from collections import Counter  # Импортируем Counter для подсчета частоты слов
import language_tool_python  # Импортируем language_tool_python для проверки орфографии
import requests  # Импортируем requests для HTTP-запросов
import webbrowser  # Импортируем webbrowser для открытия URL в браузере

# Загрузка необходимых данных для nltk
nltk.download('punkt')  # Загружаем 'punkt' пакет для токенизации текста

# Инициализация инструмента проверки орфографии для русского языка
tool = language_tool_python.LanguageTool('ru')  # Создаем объект LanguageTool для русского языка

# Текст для информационной страницы
info_text = """Эта программа предназначена для проверки текста на орфографические ошибки, а также для выявления плагиата путем поиска совпадений текста в Википедии. 

Здесь будет предоставлено руководство по некоторым функциям, которые смогут улучшить пользовательский опыт от приложения.

- Для того, чтобы вставить заранее заготовленный текст, нужно переключить раскладку на английский язык и нажать сочетание клавиш ctrl+v.
- Ошибки в тексте можно исправить просто кликнув на любой из предложенных вариантов исправления, ошибка автоматически замениться на правильный вариант.
- При использовании функции проверки на плагиат, Вы можете перейти на страницу Википедии, где было найдено совпадение, просто кликнув на ссылку.
"""

# Функция для обработки фокуса текстовой области
def handle_focus(event, area, default_text, color_on_focus='white', color_on_focus_out='gray'):
    if area.get("1.0", "end-1c") == default_text and event.type == tk.EventType.FocusIn:  # Если текст по умолчанию и событие - фокус на область
        area.delete("1.0", "end")  # Удаляем текст по умолчанию
        area.config(fg=color_on_focus)  # Меняем цвет текста на цвет для фокуса
    elif not area.get("1.0", "end-1c") and event.type == tk.EventType.FocusOut:  # Если область пуста и событие - потеря фокуса
        area.insert("1.0", default_text)  # Вставляем текст по умолчанию
        area.config(fg=color_on_focus_out)  # Меняем цвет текста на цвет для потери фокуса

# Функция замены текста
def replace_text(start, end, replacement):
    text_area.delete(start, end)  # Удаляем текст в заданном диапазоне
    text_area.insert(start, replacement)  # Вставляем новый текст в указанное начало

# Функция проверки текста
def check_text():
    text = text_area.get("1.0", tk.END).strip()  # Получаем текст из текстовой области и убираем пробелы
    result_area.config(state=tk.NORMAL)  # Включаем редактирование результата
    result_area.delete("1.0", tk.END)  # Очищаем область результата
    
    # Очистка предыдущих выделений
    text_area.tag_remove("highlight", "1.0", tk.END)  # Убираем все предыдущие выделения
    
    # Проверка орфографии и пунктуации
    matches = tool.check(text)  # Проверяем текст с помощью LanguageTool
    if matches:  # Если найдены ошибки
        result_area.insert(tk.END, "Орфографические ошибки:\n\n")  # Вставляем заголовок ошибок
        for match in matches:  # Проходимся по всем найденным ошибкам
            start_index = f"1.0+{match.offset}c"  # Начальный индекс ошибки
            end_index = f"1.0+{match.offset + match.errorLength}c"  # Конечный индекс ошибки
            text_area.tag_add("highlight", start_index, end_index)  # Выделяем ошибку в тексте
            result_area.insert(tk.END, f"{match.message}\nВарианты исправления: ")  # Вставляем сообщение об ошибке
            for i, replacement in enumerate(match.replacements):  # Перечисляем варианты исправления
                btn = tk.Button(result_area, text=replacement, command=lambda s=start_index, e=end_index, r=replacement: replace_text(s, e, r), relief="flat", bg=result_area.cget("bg"), fg="white", font=("Helvetica", 12), borderwidth=0)
                btn.configure(cursor="hand2")  # Настраиваем кнопку с вариантом исправления
                result_area.window_create(tk.END, window=btn)  # Вставляем кнопку в область результата
                if i < len(match.replacements) - 1:  # Если это не последний вариант
                    result_area.insert(tk.END, ", ")  # Добавляем запятую между вариантами
            result_area.insert(tk.END, "\n\n")  # Переход на новую строку после каждого варианта
    else:  # Если ошибок не найдено
        result_area.insert(tk.END, "Ошибок не найдено\n")  # Вставляем сообщение об отсутствии ошибок
    result_area.config(state=tk.DISABLED)  # Запрещаем редактирование результата

# Функция поиска часто повторяемых слов
def find_common_words():
    text = text_area.get("1.0", tk.END).strip()  # Получаем текст из текстовой области и убираем пробелы
    words = nltk.word_tokenize(text)  # Токенизируем текст
    words = [word.lower() for word in words if word.isalnum()]  # Приводим все слова к нижнему регистру и оставляем только алфавитные
    word_counts = Counter(words)  # Подсчитываем частоту каждого слова
    
    common_words = {word: count for word, count in word_counts.items() if count >= 4}  # Оставляем слова, которые встречаются 4 и более раз
    
    common_words_area.delete("1.0", tk.END)  # Очищаем область для часто повторяемых слов
    if common_words:  # Если такие слова есть
        for word, count in common_words.items():  # Перебираем все слова и их частоты
            common_words_area.insert(tk.END, f"{word} - {count}\n")  # Вставляем слово и его частоту
    else:  # Если таких слов нет
        common_words_area.insert(tk.END, "Нет часто повторяемых слов (4 и более раз).\n")  # Вставляем сообщение об отсутствии часто повторяемых слов

# Функция отображения часто повторяемых слов
def show_common_words():
    main_frame.pack_forget()  # Скрываем основную рамку
    common_words_frame.pack(fill=tk.BOTH, expand=True)  # Показываем рамку с часто повторяемыми словами
    find_common_words()  # Вызываем функцию поиска часто повторяемых слов

# Функция отображения проверки на плагиат
def show_plagiarism():
    main_frame.pack_forget()  # Скрываем основную рамку
    plagiarism_frame.pack(fill=tk.BOTH, expand=True)  # Показываем рамку с проверкой на плагиат
    plagiarism_result_area.delete("1.0", tk.END)  # Очищаем область результата проверки на плагиат
    plagiarism_result_area.insert("1.0", text_area.get("1.0", tk.END))  # Вставляем текст из основной текстовой области

# Функция отображения основной рамки
def show_main_frame():
    common_words_frame.pack_forget()  # Скрываем рамку с часто повторяемыми словами
    plagiarism_frame.pack_forget()  # Скрываем рамку с проверкой на плагиат
    info_frame.pack_forget()  # Скрываем информационную рамку
    main_frame.pack(fill=tk.BOTH, expand=True)  # Показываем основную рамку

# Функция копирования текста в буфер обмена
def copy_text():
    root.clipboard_clear()  # Очищаем буфер обмена
    root.clipboard_append(text_area.get("1.0", tk.END))  # Копируем текст из текстовой области в буфер обмена

# Функция вставки текста из буфера обмена
def paste_text(event=None):
    try:
        text = root.clipboard_get()  # Получаем текст из буфера обмена
        text_area.insert(tk.INSERT, text)  # Вставляем текст в текстовую область
    except tk.TclError:
        pass
    return 'break'  # Прерываем событие вставки

# Функция проверки текста на плагиат
def check_plagiarism():
    text = text_area.get("1.0", tk.END).strip()  # Получаем текст из текстовой области и убираем пробелы
    plagiarism_result_area.config(state=tk.NORMAL)  # Включаем редактирование результата
    plagiarism_result_area.delete("1.0", tk.END)  # Очищаем область результата

    # Поиск совпадений в Википедии
    response = requests.get(f"https://ru.wikipedia.org/w/api.php?action=query&list=search&srsearch={text}&format=json")  # Отправляем запрос к API Википедии
    if response.status_code == 200:  # Если запрос успешен
        data = response.json()  # Получаем JSON данные из ответа
        search_results = data.get("query", {}).get("search", [])  # Извлекаем результаты поиска
        if search_results:  # Если найдены совпадения
            for result in search_results:  # Перебираем все результаты поиска
                title = result.get("title")  # Извлекаем заголовок статьи
                snippet = result.get("snippet")  # Извлекаем фрагмент статьи
                pageid = result.get("pageid")  # Извлекаем ID страницы
                link = f"https://ru.wikipedia.org/?curid={pageid}"  # Формируем URL статьи
                plagiarism_result_area.insert(tk.END, f"Совпадение найдено: {title}\n{snippet}...\nСсылка: {link}\n\n")  # Вставляем данные о совпадении в область результата
        else:  # Если совпадений нет
            plagiarism_result_area.insert(tk.END, "Совпадений не найдено.\n")  # Вставляем сообщение об отсутствии совпадений
    else:  # Если запрос неуспешен
        plagiarism_result_area.insert(tk.END, "Ошибка при запросе к Википедии.\n")  # Вставляем сообщение об ошибке
    plagiarism_result_area.config(state=tk.NORMAL)  # Запрещаем редактирование результата

# Функция отображения информационной страницы
def show_info():
    main_frame.pack_forget()  # Скрываем основную рамку
    info_frame.pack(fill=tk.BOTH, expand=True)  # Показываем информационную рамку

# Создание основного окна приложения
root = tk.Tk()  # Создаем основное окно
root.title("Проверка текста и плагиата")  # Устанавливаем заголовок окна
root.geometry("800x600")  # Устанавливаем размер окна

# Создание меню
menu_bar = tk.Menu(root)  # Создаем объект меню
root.config(menu=menu_bar)  # Устанавливаем меню в окне

# Добавление пунктов меню
file_menu = tk.Menu(menu_bar, tearoff=0)  # Создаем подменю "Файл"
menu_bar.add_cascade(label="Файл", menu=file_menu)  # Добавляем подменю в главное меню
file_menu.add_command(label="Копировать", command=copy_text)  # Добавляем команду "Копировать" в подменю
file_menu.add_command(label="Вставить", command=paste_text)  # Добавляем команду "Вставить" в подменю
file_menu.add_separator()  # Добавляем разделитель
file_menu.add_command(label="Выход", command=root.quit)  # Добавляем команду "Выход" в подменю

# Добавление пункта меню "Информация"
menu_bar.add_command(label="Информация", command=show_info)  # Добавляем команду "Информация" в главное меню

# Создание основной рамки
main_frame = ttk.Frame(root)  # Создаем основную рамку
main_frame.pack(fill=tk.BOTH, expand=True)  # Устанавливаем основную рамку в окне

# Создание рамки для проверки орфографии
text_area = tk.Text(main_frame, wrap=tk.WORD, font=("Helvetica", 12))  # Создаем текстовую область для ввода текста
text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)  # Устанавливаем текстовую область в рамке
text_area.insert("1.0", "Введите текст для проверки...")  # Вставляем текст по умолчанию
text_area.bind("<FocusIn>", lambda event: handle_focus(event, text_area, "Введите текст для проверки..."))  # Привязываем обработчик фокуса
text_area.bind("<FocusOut>", lambda event: handle_focus(event, text_area, "Введите текст для проверки..."))  # Привязываем обработчик потери фокуса

# Создание кнопки для проверки текста
check_button = ttk.Button(main_frame, text="Проверить текст", command=check_text)  # Создаем кнопку для проверки текста
check_button.pack(pady=5)  # Устанавливаем кнопку в рамке

# Создание области для вывода результатов проверки
result_area = tk.Text(main_frame, wrap=tk.WORD, font=("Helvetica", 12), state=tk.DISABLED)  # Создаем текстовую область для вывода результатов
result_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)  # Устанавливаем область результатов в рамке

# Создание рамки для часто повторяемых слов
common_words_frame = ttk.Frame(root)  # Создаем рамку для часто повторяемых слов
common_words_area = tk.Text(common_words_frame, wrap=tk.WORD, font=("Helvetica", 12), state=tk.DISABLED)  # Создаем текстовую область для часто повторяемых слов
common_words_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)  # Устанавливаем область для часто повторяемых слов в рамке

# Создание рамки для проверки на плагиат
plagiarism_frame = ttk.Frame(root)  # Создаем рамку для проверки на плагиат
plagiarism_result_area = tk.Text(plagiarism_frame, wrap=tk.WORD, font=("Helvetica", 12), state=tk.DISABLED)  # Создаем текстовую область для результатов проверки на плагиат
plagiarism_result_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)  # Устанавливаем область результатов проверки на плагиат в рамке

# Создание информационной рамки
info_frame = ttk.Frame(root)  # Создаем информационную рамку
info_label = tk.Label(info_frame, text=info_text, wraplength=780, justify=tk.LEFT, font=("Helvetica", 12))  # Создаем метку для информационного текста
info_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)  # Устанавливаем метку в рамке

# Создание нижней панели с кнопками
button_frame = ttk.Frame(root)  # Создаем рамку для кнопок
button_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=10)  # Устанавливаем рамку внизу окна

# Добавление кнопок на нижнюю панель
common_words_button = ttk.Button(button_frame, text="Часто повторяемые слова", command=show_common_words)  # Создаем кнопку для часто повторяемых слов
common_words_button.pack(side=tk.LEFT, padx=5)  # Устанавливаем кнопку на панели

plagiarism_button = ttk.Button(button_frame, text="Проверка на плагиат", command=show_plagiarism)  # Создаем кнопку для проверки на плагиат
plagiarism_button.pack(side=tk.LEFT, padx=5)  # Устанавливаем кнопку на панели

main_frame_button = ttk.Button(button_frame, text="Назад", command=show_main_frame)  # Создаем кнопку для возврата на основную рамку
main_frame_button.pack(side=tk.RIGHT, padx=5)  # Устанавливаем кнопку на панели

# Запуск основного цикла обработки событий
root.mainloop()  # Запускаем главный цикл Tkinter
