# -*- coding: utf-8 -*-
"""
Вспомогательные функции работы с файлами и буфером обмена для UI.

Не зависят от движка шифра — только от tkinter. Вызываются из обработчиков
вкладок (cipher_tab, crack_tab).
"""

from tkinter import filedialog, messagebox


# Кодировки, которые перебираем при открытии текстового файла.
# UTF-8 — современный стандарт; CP1251 и KOI8-R — наследие русских ОС.
_READ_ENCODINGS = ('utf-8', 'utf-8-sig', 'cp1251', 'koi8-r')


def load_file_into(text_widget):
    """
    Открыть диалог "выбрать файл" и загрузить его содержимое в text_widget.

    Перебирает несколько кодировок, чтобы файл открылся даже если он сохранён
    не в UTF-8 (например, старые русские файлы в CP1251).
    """
    path = filedialog.askopenfilename(
        title='Выберите файл с текстом',
        filetypes=[('Текстовые файлы', '*.txt'), ('Все файлы', '*.*')],
    )
    if not path:
        return  # пользователь нажал "Отмена"

    for encoding in _READ_ENCODINGS:
        try:
            with open(path, 'r', encoding=encoding) as f:
                content = f.read()
        except UnicodeDecodeError:
            continue  # пробуем следующую кодировку
        except OSError as e:
            messagebox.showerror(
                'Ошибка открытия файла',
                f'Не удалось открыть файл:\n{e}',
            )
            return
        # Удалось прочитать — вставляем и выходим
        text_widget.delete('1.0', 'end')
        text_widget.insert('1.0', content)
        return

    messagebox.showerror(
        'Ошибка кодировки',
        'Не удалось определить кодировку файла.\n'
        'Попробуйте сохранить его в UTF-8 и открыть ещё раз.',
    )


def save_widget_to_file(text_widget):
    """
    Сохранить содержимое text_widget в файл, выбранный пользователем.
    Всегда пишет UTF-8.
    """
    content = text_widget.get('1.0', 'end-1c')
    if not content.strip():
        messagebox.showinfo(
            'Нечего сохранять',
            'Поле результата пустое — сначала выполните операцию.',
        )
        return

    path = filedialog.asksaveasfilename(
        title='Сохранить результат',
        defaultextension='.txt',
        filetypes=[('Текстовый файл UTF-8', '*.txt'), ('Все файлы', '*.*')],
    )
    if not path:
        return

    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        messagebox.showinfo('Готово', f'Файл сохранён:\n{path}')
    except OSError as e:
        messagebox.showerror(
            'Ошибка сохранения',
            f'Не удалось сохранить файл:\n{e}',
        )


def copy_widget_to_clipboard(root, text_widget):
    """
    Скопировать содержимое text_widget в системный буфер обмена.

    После clipboard_append обязательно вызываем update() — иначе в некоторых
    системах (особенно Windows) буфер не сохраняется после выхода из программы.
    """
    content = text_widget.get('1.0', 'end-1c')
    if not content:
        return
    root.clipboard_clear()
    root.clipboard_append(content)
    root.update()

    # Кратковременная индикация в заголовке окна — без модального окошка.
    original_title = root.title()
    root.title('✓ Скопировано в буфер обмена')
    root.after(1200, lambda: root.title(original_title))
