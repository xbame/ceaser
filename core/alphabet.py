RUSSIAN_ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
RUSSIAN_ALPHABET_SIZE = len(RUSSIAN_ALPHABET)  # 32

LATIN_ALPHABET = "abcdefghijklmnopqrstuvwxyz"
LATIN_ALPHABET_SIZE = len(LATIN_ALPHABET)  # 26

# для более быстрой проверки
RUSSIAN_SET = set(RUSSIAN_ALPHABET)
LATIN_SET = set(LATIN_ALPHABET)

# словарь буква:позиция
RUSSIAN_INDEX = {ch: i for i, ch in enumerate(RUSSIAN_ALPHABET)}
LATIN_INDEX = {ch: i for i, ch in enumerate(LATIN_ALPHABET)}


# частоты букв русского алфавита
RUSSIAN_FREQUENCIES = {
    'а': 8.01, 'б': 1.59, 'в': 4.54, 'г': 1.70, 'д': 2.98,
    'е': 8.45, 'ж': 0.94, 'з': 1.65, 'и': 7.35, 'й': 1.21,
    'к': 3.49, 'л': 4.40, 'м': 3.21, 'н': 6.70, 'о': 10.97,
    'п': 2.81, 'р': 4.73, 'с': 5.47, 'т': 6.26, 'у': 2.62,
    'ф': 0.26, 'х': 0.97, 'ц': 0.48, 'ч': 1.44, 'ш': 0.73,
    'щ': 0.36, 'ъ': 0.04, 'ы': 1.90, 'ь': 1.74, 'э': 0.32,
    'ю': 0.64, 'я': 2.01,
}

# частоты списком
EXPECTED_FREQ = [RUSSIAN_FREQUENCIES[letter] for letter in RUSSIAN_ALPHABET]

# список букв по убыванию частоты
RUSSIAN_FREQ_ORDER = sorted(
    RUSSIAN_FREQUENCIES.keys(),
    key=lambda c: -RUSSIAN_FREQUENCIES[c]
)



def get_alphabet(lang):
    return RUSSIAN_ALPHABET if lang == 'ru' else LATIN_ALPHABET


def get_alphabet_size(lang):
    return RUSSIAN_ALPHABET_SIZE if lang == 'ru' else LATIN_ALPHABET_SIZE


def get_index_map(lang):
    return RUSSIAN_INDEX if lang == 'ru' else LATIN_INDEX


def get_alphabet_set(lang):
    return RUSSIAN_SET if lang == 'ru' else LATIN_SET
