from .alphabet import (
    get_alphabet_set,
    get_alphabet_size,
)


def prepare_text(text, lang):
    text = text.lower()
    if lang == 'ru':
        text = text.replace('ё', 'е')
    allowed = get_alphabet_set(lang)
    return ''.join(ch for ch in text if ch in allowed)


def normalize_key(key, lang):
    return key % get_alphabet_size(lang)


def format_output(text, group_size=5):
    groups = [text[i:i + group_size] for i in range(0, len(text), group_size)]
    return ' '.join(groups)
