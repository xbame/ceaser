# -*- coding: utf-8 -*-
"""
Движок шифра Цезаря — чистая логика без UI.

Модули:
    alphabet  — алфавиты, эталонные частоты, индексы букв
    text      — подготовка и форматирование текста, нормализация ключа
    cipher    — шифрование и расшифровка (caesar_encrypt / caesar_decrypt)
    cracker   — взлом методом частотного анализа (crack_caesar)

Зависимости (стрелка = "импортирует"):
    text     → alphabet
    cipher   → alphabet, text
    cracker  → alphabet, text, cipher
"""

from .alphabet import (
    RUSSIAN_ALPHABET, RUSSIAN_ALPHABET_SIZE,
    LATIN_ALPHABET, LATIN_ALPHABET_SIZE,
    RUSSIAN_FREQUENCIES, RUSSIAN_FREQ_ORDER, EXPECTED_FREQ,
)
from .text import prepare_text, normalize_key, format_output
from .cipher import caesar_encrypt, caesar_decrypt
from .cracker import (
    crack_caesar,
    CrackResult, KeyCandidate, FreqMapping,
    compute_letter_frequencies,
    build_cipher_freq_table,
    least_squares_score,
    MIN_TEXT_LENGTH,
)

__all__ = [
    # алфавиты и частоты
    'RUSSIAN_ALPHABET', 'RUSSIAN_ALPHABET_SIZE',
    'LATIN_ALPHABET', 'LATIN_ALPHABET_SIZE',
    'RUSSIAN_FREQUENCIES', 'RUSSIAN_FREQ_ORDER', 'EXPECTED_FREQ',
    # подготовка текста
    'prepare_text', 'normalize_key', 'format_output',
    # шифр
    'caesar_encrypt', 'caesar_decrypt',
    # взлом
    'crack_caesar', 'CrackResult', 'KeyCandidate', 'FreqMapping',
    'compute_letter_frequencies', 'build_cipher_freq_table',
    'least_squares_score', 'MIN_TEXT_LENGTH',
]
