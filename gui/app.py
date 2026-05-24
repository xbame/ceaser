# -*- coding: utf-8 -*-
"""
Главный класс приложения.

Создаёт окно, выбирает тему ttk и собирает три вкладки:
    Зашифровать  → CipherTab(mode='encrypt')
    Расшифровать → CipherTab(mode='decrypt')
    Взломать     → CrackTab
"""

import tkinter as tk
from tkinter import ttk

from .cipher_tab import CipherTab
from .crack_tab import CrackTab


class CaesarApp:
    """Корневое окно — содержит Notebook с тремя вкладками."""

    def __init__(self, root):
        self.root = root
        self.root.title("Шифр Цезаря — Лабораторная работа №1")
        self.root.geometry("900x650")
        self.root.minsize(700, 500)

        self._apply_theme()

        notebook = ttk.Notebook(root)
        notebook.pack(fill='both', expand=True, padx=8, pady=8)

        # Каждая вкладка — самостоятельный объект, владеющий своими виджетами.
        # Все три получают set_busy — общий механизм блокировки UI на время работы.
        tab_encrypt = ttk.Frame(notebook)
        tab_decrypt = ttk.Frame(notebook)
        tab_crack = ttk.Frame(notebook)

        notebook.add(tab_encrypt, text='  🔒 Зашифровать  ')
        notebook.add(tab_decrypt, text='  🔓 Расшифровать  ')
        notebook.add(tab_crack, text='  🕵 Взломать  ')

        CipherTab(tab_encrypt, root, mode='encrypt', set_busy=self._set_busy)
        CipherTab(tab_decrypt, root, mode='decrypt', set_busy=self._set_busy)
        CrackTab(tab_crack, root, set_busy=self._set_busy)

    def _apply_theme(self):
        """Выбрать более современную тему ttk, если она доступна в системе."""
        style = ttk.Style()
        for theme in ('vista', 'clam', 'aqua', 'default'):
            if theme in style.theme_names():
                style.theme_use(theme)
                return

    def _set_busy(self, busy):
        """
        Меняет курсор на "часики" (busy=True) или возвращает обычный (busy=False).

        Используется вкладками как колбэк — на время фоновой обработки.
        """
        try:
            self.root.configure(cursor='watch' if busy else '')
            self.root.update_idletasks()
        except tk.TclError:
            pass  # окно могло быть уже закрыто — игнорируем
