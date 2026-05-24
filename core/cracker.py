# -*- coding: utf-8 -*-
"""
Взлом шифра Цезаря методом частотного анализа.

ИДЕЯ
====
Буквы русского языка встречаются с известными частотами ('о' ≈ 11%, 'е' ≈ 8.5%,
'а' ≈ 8% и т.д.). Шифр Цезаря сдвигает все буквы на одинаковое число позиций,
поэтому распределение частот сохраняется — оно лишь "переезжает" по кругу.

Если мы знаем, как именно "переехали" частоты, мы знаем ключ.

АЛГОРИТМ
========
Главная функция `crack_caesar` — это пайплайн из шести шагов:

    1. Очищаем шифртекст.
    2. Считаем частоты букв шифртекста.
    3. Генерируем кандидатов на ключ путём сопоставления частот:
       i-я самая частая буква шифра → i-я самая частая буква русского.
       Каждая пара даёт один голос за определённый ключ.
    4. Для каждого из 32 возможных ключей считаем "ошибку" методом
       наименьших квадратов (МНК): насколько частоты после расшифровки
       этим ключом похожи на эталонные русские частоты.
    5. Выбираем лучший ключ: больше голосов — лучше; при равенстве
       голосов — меньше МНК-ошибка.
    6. Расшифровываем шифртекст этим ключом.

Каждый шаг — отдельная функция ниже. Чтобы понять алгоритм целиком,
читай `crack_caesar` сверху вниз — это и есть весь алгоритм.
"""

from collections import Counter
from dataclasses import dataclass, field

from .alphabet import (
    RUSSIAN_ALPHABET,
    RUSSIAN_ALPHABET_SIZE,
    RUSSIAN_INDEX,
    RUSSIAN_FREQUENCIES,
    RUSSIAN_FREQ_ORDER,
    EXPECTED_FREQ,
)
from .text import prepare_text
from .cipher import caesar_decrypt


MIN_TEXT_LENGTH = 20


# Структуры данных результата

@dataclass
class FreqMapping:
    cipher_char: str
    cipher_pct: float
    plain_char: str
    plain_pct: float
    key: int


@dataclass
class KeyCandidate:
    key: int
    votes: int
    mnk_score: float


@dataclass
class CrackResult:
    # итог работы
    best_key: int
    decrypted_text: str
    candidates: list = field(default_factory=list)   # KeyCandidate, отсортирован
    freq_table: list = field(default_factory=list)   # (буква, кол-во, %)
    mappings: list = field(default_factory=list)     # FreqMapping



# Подсчёт частот букв шифртекста


def compute_letter_frequencies(clean_text):
    total = len(clean_text)
    if total == 0:
        return [0.0] * RUSSIAN_ALPHABET_SIZE
    counts = Counter(clean_text) # считает сколько раз встречается каждая буква
    return [counts.get(letter, 0) / total * 100 for letter in RUSSIAN_ALPHABET] # возвращает список букв с частотами в процентах


def build_cipher_freq_table(clean_text):
    """
    Таблица "буква — количество — процент" по убыванию частоты.
    Используется как для шага 3 (выбор самых частых букв), так и для UI.
    """
    total = len(clean_text)
    if total == 0:
        return []
    counts = Counter(clean_text)
    table = [
        (ch, counts[ch], counts[ch] / total * 100)
        for ch in RUSSIAN_ALPHABET # кортеж буква, количество, процент
        if counts.get(ch, 0) > 0 # добалвние только букв, которые есть в тексте
    ]
    table.sort(key=lambda row: -row[1])  # по убыванию количества
    return table


# =============================================================================
# Шаг 3. Генерация кандидатов на ключ сопоставлением частот
# =============================================================================
#
# Берём top_n самых частых букв шифра. Для каждой пробуем сопоставить с
# map_top самыми частыми буквами русского (берём не только лучшую, чтобы
# учесть "выбросы" в коротких текстах).
#
# Каждая пара даёт один голос за конкретный ключ:
#       cipher_pos = (plain_pos + key) mod N
#   =>  key = (cipher_pos - plain_pos) mod N
#
# Прямые соответствия (i-я частая шифра ↔ i-я частая языка) дополнительно
# попадают в список mappings для отображения в таблице UI.

def generate_key_candidates_by_frequency_matching(
    freq_table, top_n=10, map_top=5
):

    top_n = min(top_n, len(freq_table))
    map_top = min(map_top, len(RUSSIAN_FREQ_ORDER))

    key_votes = {}
    mappings = []

    for i in range(top_n):
        cipher_ch, _count, cipher_pct = freq_table[i]

        # сопоставление частот и отбор кандитадатов на ключ
        for j in range(map_top):
            plain_ch = RUSSIAN_FREQ_ORDER[j]
            plain_pct = RUSSIAN_FREQUENCIES[plain_ch]

            # кандидат на ключ из этой пары
            key = (RUSSIAN_INDEX[cipher_ch] - RUSSIAN_INDEX[plain_ch]) % RUSSIAN_ALPHABET_SIZE
            key_votes[key] = key_votes.get(key, 0) + 1

            if i == j:
                mappings.append(FreqMapping(
                    cipher_char=cipher_ch,
                    cipher_pct=cipher_pct,
                    plain_char=plain_ch,
                    plain_pct=plain_pct,
                    key=key,
                ))

    return key_votes, mappings


# Оценка ключей методом наименьших квадратов


def least_squares_score(observed_freq, key):
    score = 0.0
    for i in range(RUSSIAN_ALPHABET_SIZE):
        shifted_idx = (i + key) % RUSSIAN_ALPHABET_SIZE
        diff = observed_freq[shifted_idx] - EXPECTED_FREQ[i]
        score += diff * diff
    return score


def score_all_keys_by_least_squares(observed_freq): # список ошибок
    return [
        least_squares_score(observed_freq, key)
        for key in range(RUSSIAN_ALPHABET_SIZE)
    ]



# Объединение оценок и выбор лучшего ключа


def pick_best_key(key_votes, mnk_scores):
    candidates = [
        KeyCandidate(
            key=k, # ключ
            votes=key_votes.get(k, 0), # число голосов
            mnk_score=mnk_scores[k], # ошибка мнк
        )
        for k in range(RUSSIAN_ALPHABET_SIZE)
    ]
    candidates.sort(key=lambda c: (-c.votes, c.mnk_score))
    return candidates[0].key, candidates



# Сбор всего


def crack_caesar(ciphertext):
    # очистка
    clean = prepare_text(ciphertext, 'ru')
    if len(clean) < MIN_TEXT_LENGTH:
        return None

    # частоты букв шифртекста
    observed_freq = compute_letter_frequencies(clean)
    freq_table = build_cipher_freq_table(clean)

    # кандидаты на ключ сопоставлением
    key_votes, mappings = generate_key_candidates_by_frequency_matching(freq_table)

    # оценка каждого ключа МНК
    mnk_scores = score_all_keys_by_least_squares(observed_freq)

    # выбор лучшего ключа
    best_key, candidates = pick_best_key(key_votes, mnk_scores)

    # расшифровка
    decrypted = caesar_decrypt(ciphertext, best_key, 'ru')

    return CrackResult(
        best_key=best_key,
        decrypted_text=decrypted,
        candidates=candidates,
        freq_table=freq_table,
        mappings=mappings,
    )
