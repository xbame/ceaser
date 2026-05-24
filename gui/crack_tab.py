# -*- coding: utf-8 -*-
"""
Вкладка "Взломать" — частотный анализ + таблицы кандидатов на ключ.
"""

import threading
from tkinter import ttk, scrolledtext, messagebox

from core import crack_caesar, caesar_decrypt
from .file_helpers import (
    load_file_into, save_widget_to_file, copy_widget_to_clipboard,
)


class CrackTab:
    """Вкладка взлома шифра."""

    def __init__(self, parent, root, set_busy):
        self.root = root
        self.set_busy = set_busy

        # Чтобы _apply_key_from_table знал, из какого ввода брать шифртекст:
        self._raw_text = ''

        self._build(parent)

    # ----- Сборка интерфейса -------------------------------------------------
    def _build(self, parent):
        ttk.Label(
            parent,
            text=('Взлом методом частотного анализа (только русский язык).\n'
                  'Самые частые буквы шифра → самые частые буквы русского '
                  '(о, е, а, и…). Надёжно при 100+ буквах.'),
            foreground='gray', justify='left',
        ).pack(anchor='w', padx=6, pady=(6, 0))

        # --- Поле ввода шифртекста ---
        frame_in = ttk.LabelFrame(parent, text='Зашифрованный текст', padding=6)
        frame_in.pack(fill='both', expand=True, padx=6, pady=6)

        self.input_text = scrolledtext.ScrolledText(
            frame_in, wrap='word', height=7, font=('Consolas', 10), undo=True,
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
            command=self._clear_all,
        ).pack(side='left', padx=(6, 0))

        # --- Кнопка взлома ---
        ttk.Button(
            parent, text='🕵  Взломать (частотный анализ)',
            command=self._run,
        ).pack(fill='x', padx=6, pady=4, ipady=4)

        # --- Две таблицы бок о бок ---
        paned = ttk.PanedWindow(parent, orient='horizontal')
        paned.pack(fill='both', expand=True, padx=6, pady=(0, 4))

        self.freq_table = self._build_freq_table(paned)
        self.cand_table = self._build_cand_table(paned)

        # --- Поле вывода расшифровки ---
        frame_out = ttk.LabelFrame(parent, text='Расшифрованный текст', padding=4)
        frame_out.pack(fill='x', padx=6, pady=(0, 4))

        self.output_text = scrolledtext.ScrolledText(
            frame_out, wrap='word', height=4, font=('Consolas', 10),
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

        self.status_label = ttk.Label(parent, text='Готов к работе.', foreground='gray')
        self.status_label.pack(fill='x', padx=6, pady=(0, 4))

    def _build_freq_table(self, paned):
        """Левая таблица: частоты шифрбукв ↔ эталонные русские частоты."""
        frame = ttk.LabelFrame(
            paned, text='Частоты букв шифртекста vs русского языка', padding=4
        )
        paned.add(frame, weight=1)

        cols = ('cipher', 'cipher_pct', 'arrow', 'plain', 'plain_pct', 'key_cand')
        table = ttk.Treeview(frame, columns=cols, show='headings', height=10)
        headings = [
            ('cipher', 'Буква шифра', 90),
            ('cipher_pct', 'Частота, %', 90),
            ('arrow', '→', 25),
            ('plain', 'Буква откр.', 90),
            ('plain_pct', 'Эталон, %', 90),
            ('key_cand', 'Ключ', 55),
        ]
        for col_id, title, width in headings:
            table.heading(col_id, text=title)
            table.column(col_id, width=width, anchor='center')
        table.pack(fill='both', expand=True)

        ttk.Label(
            frame,
            text='(i-я частая буква шифра предположительно → i-я частая буква языка)',
            foreground='gray', font=('Segoe UI', 8),
        ).pack(anchor='w', pady=(2, 0))
        return table

    def _build_cand_table(self, paned):
        """Правая таблица: кандидаты на ключ с голосами и МНК."""
        frame = ttk.LabelFrame(paned, text='Кандидаты на ключ', padding=4)
        paned.add(frame, weight=1)

        cols = ('key', 'votes', 'mnk', 'preview')
        table = ttk.Treeview(frame, columns=cols, show='headings', height=10)
        headings = [
            ('key', 'Ключ', 50),
            ('votes', 'Голоса ЧА', 70),
            ('mnk', 'Score МНК', 90),
            ('preview', 'Превью расшифровки', 200),
        ]
        for col_id, title, width in headings:
            table.heading(col_id, text=title)
            anchor = 'w' if col_id == 'preview' else 'center'
            table.column(col_id, width=width, anchor=anchor)
        table.pack(fill='both', expand=True)

        # Двойной клик по строке — применить этот ключ к шифртексту.
        table.bind('<Double-1>', self._apply_key_from_table)

        ttk.Label(
            frame,
            text='ЧА = частотный анализ (голоса). МНК = метод наим. квадратов.\n'
                 'Двойной клик по строке — применить этот ключ.',
            foreground='gray', font=('Segoe UI', 8),
        ).pack(anchor='w', pady=(2, 0))
        return table

    # ----- Обработчики -------------------------------------------------------
    def _clear_all(self):
        self.input_text.delete('1.0', 'end')
        self.freq_table.delete(*self.freq_table.get_children())
        self.cand_table.delete(*self.cand_table.get_children())
        self.output_text.delete('1.0', 'end')

    def _run(self):
        """Запустить взлом в фоновом потоке."""
        raw_text = self.input_text.get('1.0', 'end-1c')
        if not raw_text.strip():
            messagebox.showwarning(
                'Пустой текст',
                'Введите зашифрованный текст для взлома.',
            )
            return
        self._raw_text = raw_text

        self.status_label.configure(text='Анализирую частоты…', foreground='gray')
        self.set_busy(True)
        threading.Thread(
            target=self._worker, args=(raw_text,), daemon=True,
        ).start()

    def _worker(self, raw_text):
        try:
            result = crack_caesar(raw_text)
            self.root.after(0, self._on_done, result)
        except Exception as e:  # noqa: BLE001
            self.root.after(0, self._on_error, str(e))

    def _on_done(self, result):
        """Заполнить таблицы и поле вывода результатами взлома."""
        # Очистка таблиц
        self.freq_table.delete(*self.freq_table.get_children())
        self.cand_table.delete(*self.cand_table.get_children())

        if result is None:
            self.output_text.delete('1.0', 'end')
            self.status_label.configure(
                text='⚠ Текст слишком короткий (< 20 букв) — анализ невозможен',
                foreground='red',
            )
            self.set_busy(False)
            return

        self._fill_freq_table(result.mappings, result.best_key)
        self._fill_cand_table(result.candidates, result.best_key)

        self.output_text.delete('1.0', 'end')
        self.output_text.insert('1.0', result.decrypted_text)

        self._update_status(result)
        self.set_busy(False)

    def _fill_freq_table(self, mappings, best_key):
        """Заполнить левую таблицу прямыми соответствиями частот."""
        for m in mappings:
            marker = ' ★' if m.key == best_key else ''
            self.freq_table.insert('', 'end', values=(
                m.cipher_char.upper(),
                f'{m.cipher_pct:.2f}%',
                '→',
                m.plain_char.upper(),
                f'{m.plain_pct:.2f}%',
                f'{m.key}{marker}',
            ))

    def _fill_cand_table(self, candidates, best_key):
        """Заполнить правую таблицу кандидатами на ключ (показываем топ-8)."""
        shown = 0
        for c in candidates:
            if c.votes == 0 and shown >= 5:
                break
            preview_full = caesar_decrypt(self._raw_text, c.key, 'ru')
            preview_clean = preview_full.replace(' ', '')[:35]
            marker = ' ← ЛУЧШИЙ' if c.key == best_key else ''
            self.cand_table.insert('', 'end', values=(
                c.key, c.votes, f'{c.mnk_score:.2f}',
                preview_clean + marker,
            ))
            shown += 1
            if shown >= 8:
                break

    def _update_status(self, result):
        if result.mappings:
            top = result.mappings[0]
            hint = (f'Самая частая в шифре: «{top.cipher_char.upper()}» '
                    f'({top.cipher_pct:.1f}%) → «{top.plain_char.upper()}» '
                    f'({top.plain_pct:.1f}%)  ⟹  ключ = {result.best_key}')
        else:
            hint = f'Найден ключ = {result.best_key}'

        self.status_label.configure(
            text=f'✓ {hint}. Если результат бессмыслен — '
                 f'попробуйте другой ключ из таблицы (двойной клик).',
            foreground='#008040',
        )

    def _apply_key_from_table(self, _event):
        """Двойной клик по строке кандидатов — расшифровать выбранным ключом."""
        selection = self.cand_table.selection()
        if not selection:
            return
        item = self.cand_table.item(selection[0])
        try:
            key = int(item['values'][0])
        except (ValueError, IndexError):
            return

        raw_text = self.input_text.get('1.0', 'end-1c')
        if not raw_text.strip():
            return

        decrypted = caesar_decrypt(raw_text, key, 'ru')
        self.output_text.delete('1.0', 'end')
        self.output_text.insert('1.0', decrypted)

    def _on_error(self, message):
        self.set_busy(False)
        self.status_label.configure(text=f'⚠ Ошибка: {message}', foreground='red')
        messagebox.showerror('Ошибка', f'Произошла ошибка:\n{message}')
