# -*- coding: utf-8 -*-
"""
Вкладка "Зашифровать" / "Расшифровать".

Одна и та же разметка для обоих режимов — отличается только подпись кнопки
и функция движка, которую она вызывает.
"""

import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

from core import (
    caesar_encrypt, caesar_decrypt,
    normalize_key, prepare_text,
    RUSSIAN_ALPHABET_SIZE, LATIN_ALPHABET_SIZE,
)
from .file_helpers import (
    load_file_into, save_widget_to_file, copy_widget_to_clipboard,
)


class CipherTab:
    """
    Один экземпляр = одна вкладка (либо для шифрования, либо для расшифровки).

    mode:
        'encrypt' — кнопка "Зашифровать", вызывает caesar_encrypt
        'decrypt' — кнопка "Расшифровать", вызывает caesar_decrypt
    """

    def __init__(self, parent, root, mode, set_busy):
        self.root = root
        self.mode = mode
        self.set_busy = set_busy  # колбэк блокировки UI на время работы

        self._build(parent)

    # ----- Сборка интерфейса -------------------------------------------------
    def _build(self, parent):
        # --- Поле ввода ---
        frame_in = ttk.LabelFrame(parent, text='Исходный текст', padding=6)
        frame_in.pack(fill='both', expand=True, padx=6, pady=(6, 3))

        self.input_text = scrolledtext.ScrolledText(
            frame_in, wrap='word', height=10, font=('Consolas', 10), undo=True,
        )
        self.input_text.pack(fill='both', expand=True)

        btns_in = ttk.Frame(frame_in)
        btns_in.pack(fill='x', pady=(4, 0))
        ttk.Button(
            btns_in, text='📂 Загрузить из файла',
            command=lambda: load_file_into(self.input_text),
        ).pack(side='left')
        ttk.Button(
            btns_in, text='🗑 Очистить',
            command=lambda: self.input_text.delete('1.0', 'end'),
        ).pack(side='left', padx=(6, 0))

        # --- Параметры (язык + ключ) ---
        frame_params = ttk.Frame(parent)
        frame_params.pack(fill='x', padx=6, pady=4)

        ttk.Label(frame_params, text='Язык:').pack(side='left')
        self.lang_var = tk.StringVar(value='ru')
        ttk.Radiobutton(
            frame_params, text='Русский (32 буквы)',
            variable=self.lang_var, value='ru',
        ).pack(side='left', padx=(6, 0))
        ttk.Radiobutton(
            frame_params, text='English (26 letters)',
            variable=self.lang_var, value='en',
        ).pack(side='left', padx=(6, 0))

        ttk.Label(frame_params, text='  Ключ:').pack(side='left', padx=(20, 0))
        self.key_var = tk.StringVar(value='3')
        ttk.Entry(frame_params, textvariable=self.key_var, width=8).pack(
            side='left', padx=(6, 0)
        )
        ttk.Label(
            frame_params,
            text='(любое целое — программа сама приведёт к диапазону)',
            foreground='gray',
        ).pack(side='left', padx=(6, 0))

        # --- Кнопка действия ---
        label = 'Зашифровать' if self.mode == 'encrypt' else 'Расшифровать'
        icon = '🔒' if self.mode == 'encrypt' else '🔓'
        ttk.Button(
            parent, text=f'{icon}  {label}',
            command=self._run,
        ).pack(fill='x', padx=6, pady=4, ipady=4)

        # --- Поле вывода ---
        frame_out = ttk.LabelFrame(parent, text='Результат', padding=6)
        frame_out.pack(fill='both', expand=True, padx=6, pady=(3, 3))

        self.output_text = scrolledtext.ScrolledText(
            frame_out, wrap='word', height=10, font=('Consolas', 10),
        )
        self.output_text.pack(fill='both', expand=True)

        btns_out = ttk.Frame(frame_out)
        btns_out.pack(fill='x', pady=(4, 0))
        ttk.Button(
            btns_out, text='📋 Копировать',
            command=lambda: copy_widget_to_clipboard(self.root, self.output_text),
        ).pack(side='left')
        ttk.Button(
            btns_out, text='💾 Сохранить в файл',
            command=lambda: save_widget_to_file(self.output_text),
        ).pack(side='left', padx=(6, 0))

        # --- Строка статуса ---
        self.status_label = ttk.Label(parent, text='Готов к работе.', foreground='gray')
        self.status_label.pack(fill='x', padx=6, pady=(0, 6))

    # ----- Обработчик кнопки -------------------------------------------------
    def _run(self):
        """Прочитать ввод, проверить, запустить шифрование в фоновом потоке."""
        raw_text = self.input_text.get('1.0', 'end-1c')
        lang = self.lang_var.get()
        key_str = self.key_var.get().strip()

        # Валидация: непустой текст
        if not raw_text.strip():
            messagebox.showwarning(
                'Пустой текст',
                'Введите текст для обработки или загрузите его из файла.',
            )
            return

        # Валидация: ключ — целое число
        try:
            key = int(key_str)
        except ValueError:
            messagebox.showerror(
                'Неверный ключ',
                f'«{key_str}» — не целое число.\n\n'
                f'Ключ — это целое число (например, 3, 7, -5, 100).\n'
                f'Программа сама приведёт его к нужному диапазону.',
            )
            return

        # Если ключ "свернулся" по модулю — сообщаем пользователю.
        normalized_key = normalize_key(key, lang)
        max_key = RUSSIAN_ALPHABET_SIZE if lang == 'ru' else LATIN_ALPHABET_SIZE
        if normalized_key != key:
            self.status_label.configure(
                text=(f'Ключ {key} приведён к диапазону '
                      f'[0;{max_key-1}]: используется {normalized_key}'),
                foreground='#b06000',
            )
        else:
            self.status_label.configure(text='Обрабатываю...', foreground='gray')

        self.set_busy(True)
        threading.Thread(
            target=self._worker,
            args=(raw_text, normalized_key, lang),
            daemon=True,
        ).start()

    # ----- Фоновый поток -----------------------------------------------------
    def _worker(self, raw_text, key, lang):
        """Выполняется в фоновом потоке — здесь нельзя трогать виджеты."""
        try:
            if self.mode == 'encrypt':
                result = caesar_encrypt(raw_text, key, lang)
            else:
                result = caesar_decrypt(raw_text, key, lang)
            cleaned_len = len(prepare_text(raw_text, lang))
            self.root.after(0, self._on_done, result, cleaned_len)
        except Exception as e:  # noqa: BLE001
            self.root.after(0, self._on_error, str(e))

    def _on_done(self, result, cleaned_len):
        """Колбэк в главном потоке после успешной обработки."""
        self.output_text.delete('1.0', 'end')
        self.output_text.insert('1.0', result)

        action = 'Зашифровано' if self.mode == 'encrypt' else 'Расшифровано'
        if cleaned_len == 0:
            self.status_label.configure(
                text='⚠ После очистки не осталось букв выбранного алфавита!',
                foreground='red',
            )
        else:
            formatted = f'{cleaned_len:,}'.replace(',', ' ')
            self.status_label.configure(
                text=f'✓ {action}. Обработано букв: {formatted}',
                foreground='#008040',
            )
        self.set_busy(False)

    def _on_error(self, message):
        self.set_busy(False)
        self.status_label.configure(text=f'⚠ Ошибка: {message}', foreground='red')
        messagebox.showerror('Ошибка', f'Произошла ошибка:\n{message}')
