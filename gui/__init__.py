# -*- coding: utf-8 -*-
"""
Пользовательский интерфейс (tkinter).

Модули:
    app          — главный класс CaesarApp (окно + Notebook)
    cipher_tab   — вкладка "Зашифровать" / "Расшифровать"
    crack_tab    — вкладка "Взломать"
    file_helpers — открыть/сохранить/копировать (общие для всех вкладок)

Зависимости:
    app          → cipher_tab, crack_tab
    cipher_tab   → core, file_helpers
    crack_tab    → core, file_helpers
    file_helpers → tkinter (никакой логики шифра)
"""

from .app import CaesarApp

__all__ = ['CaesarApp']
