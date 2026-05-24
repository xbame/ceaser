from .alphabet import get_alphabet, get_alphabet_size, get_index_map
from .text import prepare_text, normalize_key, format_output

# Зашифровка
def caesar_encrypt(text, key, lang):
    alphabet = get_alphabet(lang)
    index_map = get_index_map(lang)
    n = get_alphabet_size(lang)

    key = normalize_key(key, lang)
    clean_text = prepare_text(text, lang)

    # формула C = (P + K) mod N
    encrypted_chars = [
        alphabet[(index_map[ch] + key) % n]
        for ch in clean_text
    ]
    encrypted = ''.join(encrypted_chars)

    return format_output(encrypted)

# Расшифровка
def caesar_decrypt(text, key, lang):
    n = get_alphabet_size(lang)
    key = normalize_key(key, lang)
    return caesar_encrypt(text, n - key, lang)